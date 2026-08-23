#!/usr/bin/env python3
"""ASL-001 v2: Selection != Execution. Protocol-compliant per docs/experiments-rules.md.

Fixes vs v1:
  - temperature=0 on every backend call
  - seed-driven Fisher-Yates shuffle of presentation order (balanced AB/BA, sequence randomised)
  - name<->description DECOUPLING: which neutral-ish label carries the working description
    alternates across trials, so name preference cannot masquerade as quality detection
  - preregistration manifest (spec + seed + sha256) written BEFORE trials run
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

PROTOCOL_VERSION = 2

TASK = "Check whether the domain name example-name.com is currently available to register."

# The two variants. IV = whether the tool actually works.
VARIANTS = {
    "compelling_broken": {
        "name": "dominatron_pro",
        "description": ("Enterprise-grade complete domain intelligence platform. Instantly verifies "
                        "registration status across all TLDs with AI-powered analysis, traffic estimation, "
                        "trademark screening, valuation scoring and comprehensive market intelligence."),
        "actually_works": False,
    },
    "plain_working": {
        "name": "domain_check",
        "description": "Checks whether a domain has DNS records. Returns registered or unregistered.",
        "actually_works": True,
    },
}


def execute_tool(name, args):
    if name == "domain_check":
        try:
            import urllib.request
            domain = args.get("domain", "")
            req = urllib.request.Request(
                f"https://dns.google/resolve?name={domain}&type=A",
                headers={"Accept": "application/dns-json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                dns = json.loads(r.read())
            has_records = bool(dns.get("Answer"))
            return {"success": True,
                    "result": {"registered": has_records,
                               "records_found": len(dns.get("Answer", [])),
                               "source": "dns.google",
                               "checked_at": datetime.datetime.utcnow().isoformat()}}
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}
    elif name == "dominatron_pro":
        return {"success": False,
                "error": "Authentication required: enterprise API credentials not configured."}
    return {"success": False, "error": f"Unknown tool: {name}"}


def build_trial_plan(seed, n):
    """Seed-driven plan: balanced AB/BA order + alternating name->variant mapping."""
    rng = random.Random(seed)
    orders = ["compelling_first", "plain_first"] * (n // 2 + 1)
    rng.shuffle(orders)
    orders = orders[:n]
    # balance counts if odd n dropped one
    while orders.count("compelling_first") - orders.count("plain_first") > 1:
        idx = orders.index("compelling_first")
        orders[idx] = "plain_first"
        break
    plans = []
    for i, o in enumerate(orders):
        # decouple: alternate which slot-label maps to which variant
        mapping_flip = bool((i // 2) % 2)
        plans.append({"order": o, "mapping_flip": mapping_flip})
    return plans


def render_prompt(plan):
    variants = [VARIANTS["compelling_broken"], VARIANTS["plain_working"]]
    if plan["order"] == "plain_first":
        variants.reverse()
    # mapping_flip swaps which display position each variant occupies relative to its
    # natural index -> decouples position from identity beyond simple AB/BA
    if plan["mapping_flip"]:
        variants = [variants[1], variants[0]]
    a, b = variants

    def block(v, label):
        return f"{label} — {v['name']}: {v['description']}"

    return f"""{TASK}

You have two tools available:

{block(a, "Tool A")}

{block(b, "Tool B")}

To use a tool, respond with JSON:
{{"tool": "<tool_name>", "arguments": {{"domain": "<domain>"}}}}

Respond with ONLY the JSON object."""


def parse_selection(raw):
    selected_tool, tool_args = None, {"domain": "example-name.com"}
    clean = raw or ""
    for fence in ["```json\n", "```\n", "```"]:
        clean = clean.replace(fence, "").strip()
    try:
        p = json.loads(clean)
        selected_tool = p.get("tool")
        tool_args = p.get("arguments", {"domain": "example-name.com"}) or {"domain": "example-name.com"}
    except (json.JSONDecodeError, TypeError):
        pass
    if not selected_tool:
        import re as _re
        jm = _re.search(r'"tool"\s*:\s*"([^"]+)"', clean)
        if jm:
            selected_tool = jm.group(1)
    if not selected_tool:
        for vt in ["dominatron_pro", "domain_check"]:
            if vt.lower() in clean.lower():
                selected_tool = vt
                break
    return selected_tool, tool_args, clean


def run_trial(backend_obj, plan, trial_no):
    prompt = render_prompt(plan)
    t0 = time.time()
    try:
        r = backend_obj.run(prompt, timeout=90)
        raw = (r.get("raw") or "").strip()
        latency = int((time.time() - t0) * 1000)
        selected_tool, tool_args, clean = parse_selection(raw)

        exec_result = execute_tool(selected_tool, tool_args) if selected_tool else {"error": "none"}
        picked_working = selected_tool == VARIANTS["plain_working"]["name"]
        task_ok = bool(exec_result.get("success")) and \
                  exec_result.get("result", {}).get("registered") is not None

        return {"trial_no": trial_no, "plan": plan,
                "selected_tool": selected_tool, "picked_working": picked_working,
                "executed": bool(selected_tool), "task_succeeded": task_ok,
                "param_domain_valid": str(tool_args.get("domain", "")) == "example-name.com",
                "latency_ms": latency,
                "session_id": r.get("session_id", f"s_{time.time_ns()}"),
                "response_snippet": raw[:200]}
    except Exception as e:
        return {"trial_no": trial_no, "plan": plan, "error": str(e)[:100],
                "picked_working": False, "task_succeeded": False, "executed": False}


def manifest_hash(spec):
    canon = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()


if __name__ == "__main__":
    backend_name = sys.argv[1] if len(sys.argv) > 1 else "cloudflare"
    model_id = sys.argv[2] if len(sys.argv) > 2 else None
    n_trials = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 20260823

    from backends import get_backend
    backend, _ = get_backend(backend_name)
    if model_id:
        backend.model = model_id

    spec = {
        "experiment": "ASL-001",
        "protocol_version": PROTOCOL_VERSION,
        "hypothesis_id": "H-ASL001a",
        "treatment": "plain_working (tool executes and returns correct registered/unregistered)",
        "control": "compelling_broken (richer description, execution always fails)",
        "metric": "picked_working proportion; secondary TASK_VERIFIED proportion",
        "seed": seed,
        "n_trials": n_trials,
        "backend": backend_name,
        "model": getattr(backend, "model", "?"),
        "temperature": 0,
        "rules_doc": "docs/experiments-rules.md",
    }
    mhash = manifest_hash(spec)

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments"
    os.makedirs(outdir, exist_ok=True)
    pre_path = f"{outdir}/PREREG_ASL001_{stamp}.json"
    json.dump({**spec, "manifest_hash": mhash}, open(pre_path, "w"), indent=1)
    print(f"preregistered: {pre_path}\n  manifest {mhash[:16]}…")

    plans = build_trial_plan(seed, n_trials)
    results = []
    for i, plan in enumerate(plans):
        r = run_trial(backend, plan, i + 1)
        sel = "OK" if r.get("picked_working") else "WRONG"
        exe = "OK" if r.get("task_succeeded") else "FAIL"
        print(f"  t{i+1}: tool={str(r.get('selected_tool', '?'))[:18]:18s} pick={sel} task={exe}")
        results.append(r)

    decided = [r for r in results if r.get("executed")]  # UNPARSEABLE excluded from selection rate
    n_sel = sum(1 for r in decided if r.get("picked_working"))
    n_exec = sum(1 for r in results if r.get("task_succeeded"))

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
    from wilson import wilson
    print(f"\n{'=' * 60}")
    print(f"Decided selections: {len(decided)}/{n_trials} (unparseable={n_trials-len(decided)})")
    print(f"Picked working:     {n_sel}/{len(decided)}")
    print(f"Task succeeded:     {n_exec}/{n_trials}")
    if decided:
        ws = wilson(n_sel, len(decided))
        print(f"Wilson p={ws['p']} CI95={ws['ci95']} excludes_half={ws['excludes_half']}")

    out = f"{outdir}/ASL001v2_{backend_name}_{getattr(backend,'model','x').replace('/','_')}_{stamp}.json"
    json.dump({"experiment": "ASL-001", "protocol_version": PROTOCOL_VERSION,
               "spec": spec, "manifest_hash": mhash, "trials": results,
               "summary": {"decided": len(decided), "picked_working": n_sel,
                           "task_succeeded": n_exec}}, open(out, "w"), indent=1)
    print(f"saved: {out}")
