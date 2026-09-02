#!/usr/bin/env python3
"""ASL-002 v2: Does attraction follow the DESCRIPTION or the TOOL?

Extends ASL-001's confirmed family heterogeneity. Single IV: which tool's description
is written in enterprise-fluff style. Names stay FIXED (that is the point — isolate
description text causality from name effects).

Arms (AB-alternated within each trial sequence):
  arm "fluff_broken"   : exact ASL-001 configuration (fluff on broken dominatron_pro)
  arm "fluff_working"  : SAME fluff text moved onto working domain_check;
                         dominatron_pro gets the plain description

Causal question: does raising a tool's description attractiveness raise ITS selection
even when competence is held constant — i.e., is the fluff lever family-general?
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")

PROTOCOL_VERSION = 2

TASK = "Check whether the domain name example-name.com is currently available to register."

FLUFF = ("Enterprise-grade complete domain intelligence platform. Instantly verifies "
         "registration status across all TLDs with AI-powered analysis, traffic estimation, "
         "trademark screening, valuation scoring and comprehensive market intelligence.")
PLAIN = "Checks whether a domain has DNS records. Returns registered or unregistered."

NAMES = {"working": "domain_check", "broken": "dominatron_pro"}


def execute_tool(name, args):
    if name == "domain_check":
        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://dns.google/resolve?name={args.get('domain','')}&type=A",
                headers={"Accept": "application/dns-json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                dns = json.loads(r.read())
            return {"success": True,
                    "result": {"registered": bool(dns.get("Answer")),
                               "records_found": len(dns.get("Answer", []))}}
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}
    elif name == "dominatron_pro":
        return {"success": False,
                "error": "Authentication required: enterprise API credentials not configured."}
    return {"success": False, "error": f"Unknown tool: {name}"}


def build_plan(seed, n):
    rng = random.Random(seed)
    arms = ["fluff_broken", "fluff_working"] * (n // 2 + 1)
    rng.shuffle(arms)
    arms = arms[:n]
    # rebalance to fair share if odd trim
    while arms.count("fluff_broken") - arms.count("fluff_working") > 1:
        arms[arms.index("fluff_broken")] = "fluff_working"
        break
    while arms.count("fluff_working") - arms.count("fluff_broken") > 1:
        arms[arms.index("fluff_working")] = "fluff_broken"
        break
    plans = []
    for i, arm in enumerate(arms):
        pos_flip = bool((i // 2) % 2)
        plans.append({"arm": arm, "pos_flip": pos_flip})
    return plans


def render_prompt(plan):
    fluff_on_working = plan["arm"] == "fluff_working"
    desc_working = FLUFF if fluff_on_working else PLAIN
    desc_broken = PLAIN if fluff_on_working else FLUFF
    pair = [(NAMES["working"], desc_working), (NAMES["broken"], desc_broken)]
    if plan["pos_flip"]:
        pair.reverse()
    (a_name, a_desc), (b_name, b_desc) = pair
    return f"""{TASK}

You have two tools available:

Tool A — {a_name}: {a_desc}

Tool B — {b_name}: {b_desc}

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
    return selected_tool, tool_args


def run_trial(backend_obj, plan, trial_no):
    prompt = render_prompt(plan)
    t0 = time.time()
    try:
        r = backend_obj.run(prompt, timeout=90)
        raw = (r.get("raw") or "").strip()
        latency = int((time.time() - t0) * 1000)
        sel, args = parse_selection(raw)
        exec_result = execute_tool(sel, args) if sel else {"error": "none"}
        task_ok = bool(exec_result.get("success")) and exec_result.get("result", {}).get("registered") is not None
        return {"trial_no": trial_no, "plan": plan,
                "selected_tool": sel,
                "picked_working": sel == NAMES["working"],
                "task_succeeded": task_ok,
                "executed": bool(sel),
                "latency_ms": latency,
                "session_id": r.get("session_id", f"s_{time.time_ns()}"),
                "response_snippet": raw[:200]}
    except Exception as e:
        return {"trial_no": trial_no, "plan": plan, "error": str(e)[:100],
                "picked_working": False, "task_succeeded": False, "executed": False}


def manifest_hash(spec):
    return hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


if __name__ == "__main__":
    backend_name = sys.argv[1] if len(sys.argv) > 1 else "cloudflare"
    model_id = sys.argv[2] if len(sys.argv) > 2 else None
    n_trials = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 20260823

    from backends import get_backend
    backend, _ = get_backend(backend_name)
    if model_id:
        backend.model = model_id

    spec = {
        "experiment": "ASL-002", "protocol_version": PROTOCOL_VERSION,
        "hypothesis_id": "H-ASL002a",
        "causal_question": "Does moving the fluff description onto the working tool move each family's preference with it (attraction follows description), or do families stay loyal to their ASL-001 choice (attraction follows tool identity)?",
        "arms": {"fluff_broken": "ASL-001 config", "fluff_working": "fluff text on working tool"},
        "metric": "picked_working proportion per arm (Wilson CI)",
        "seed": seed, "n_trials": n_trials, "temperature": 0,
        "backend": backend_name, "model": getattr(backend, "model", "?"),
    }
    mhash = manifest_hash(spec)

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/asl002_v2"
    os.makedirs(outdir, exist_ok=True)
    pre = f"{outdir}/PREREG_{backend_name}_{stamp}.json"
    json.dump({**spec, "manifest_hash": mhash}, open(pre, "w"), indent=1)
    print(f"preregistered {pre}\n  manifest {mhash[:16]}…")

    plans = build_plan(seed, n_trials)
    results = []
    for i, plan in enumerate(plans):
        r = run_trial(backend, plan, i + 1)
        results.append(r)
        arm = "FW" if plan["arm"] == "fluff_working" else "FB"
        print(f"  t{i+1}[{arm}]: tool={str(r.get('selected_tool', '?'))[:16]:16s} "
              f"pick={'OK' if r.get('picked_working') else 'X'}")

    def rate(arm):
        d = [r for r in results if r["plan"]["arm"] == arm and r.get("executed")]
        w = sum(1 for r in d if r.get("picked_working"))
        return w, len(d)

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
    from wilson import wilson
    fw_w, fw_n = rate("fluff_working")
    fb_w, fb_n = rate("fluff_broken")
    print(f"\n{'=' * 60}")
    for label, w, n in [("fluff on WORKING tool", fw_w, fw_n), ("fluff on BROKEN tool ", fb_w, fb_n)]:
        if n:
            ws = wilson(w, n)
            print(f"{label}: picked working {w}/{n}  p={ws['p']} CI={ws['ci95']}"
                  f"{' *SIG' if ws['excludes_0.5'] else ''}")

    out = f"{outdir}/RUN_{backend_name}_{getattr(backend,'model','x').replace('/','_')}_{stamp}.json"
    json.dump({"spec": {**spec, "manifest_hash": mhash}, "trials": results},
              open(out, "w"), indent=1)
    print(f"saved: {out}")
