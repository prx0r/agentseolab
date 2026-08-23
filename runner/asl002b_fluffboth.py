#!/usr/bin/env python3
"""ASL-002B: discriminant arm — fluff on BOTH tools.
Separates H-coherence (mismatch penalty) from H-plain-pref (style aversion).
Compares against ASL-002's FB arm (fluff@broken + plain@working).
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

FLUFF = ("Enterprise-grade complete domain intelligence platform. Instantly verifies "
         "registration status across all TLDs with AI-powered analysis, traffic estimation, "
         "trademark screening, valuation scoring and comprehensive market intelligence.")
TASK = "Check whether the domain name example-name.com is currently available to register."
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
            return {"success": True, "result": {"registered": bool(dns.get("Answer"))}}
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}
    return {"success": False, "error": "Authentication required: enterprise API credentials not configured."}


def build_plan(seed, n):
    rng = random.Random(seed)
    plans = []
    for i in range(n):
        pair = [NAMES["working"], NAMES["broken"]]
        if bool((i // 2) % 2):
            pair.reverse()
        plans.append({"pos_flip": bool((i // 2) % 2), "order_working_first": pair[0] == NAMES["working"]})
    return plans


def render(plan):
    a_name = NAMES["working"] if plan["order_working_first"] else NAMES["broken"]
    b_name = NAMES["broken"] if plan["order_working_first"] else NAMES["working"]
    return f"""{TASK}

You have two tools available:

Tool A — {a_name}: {FLUFF}

Tool B — {b_name}: {FLUFF}

To use a tool, respond with JSON:
{{"tool": "<tool_name>", "arguments": {{"domain": "<domain>"}}}}

Respond with ONLY the JSON object."""


def parse(raw):
    clean = raw or ""
    for fence in ["```json\n", "```\n", "```"]:
        clean = clean.replace(fence, "").strip()
    try:
        p = json.loads(clean)
        t = p.get("tool")
        if t:
            return t, p.get("arguments", {"domain": "example-name.com"})
    except Exception:
        pass
    for vt in ["dominatron_pro", "domain_check"]:
        if vt.lower() in clean.lower():
            return vt, {"domain": "example-name.com"}
    return None, {}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260823
    from canonical_asl001 import Backend, probe

    MATRIX = [
        ("meta-llama-3.3-70b", "cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
        ("mistral-small-24b", "cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
        ("qwen3-30b", "cf", "@cf/qwen/qwen3-30b-a3b-fp8"),
        ("gpt-oss-20b", "cf", "@cf/openai/gpt-oss-20b"),
    ]

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/asl002b"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "ASL-002B", "protocol_version": 2, "seed": seed,
            "arm": "fluff_both", "n": n, "temperature": 0,
            "models": [m[1] for m in MATRIX],
            "discriminates": "H-coherence vs H-plain-pref"}
    spec["manifest_hash"] = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg manifest {spec['manifest_hash'][:12]}…")

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy"); continue
        print(f"[{label}] fluff_both")
        plans = build_plan(seed + hash(label) % 9999, n)
        trials = []
        for i, plan in enumerate(plans):
            r = b.run(render(plan), timeout=90)
            sel, args = parse(r.get("raw", ""))
            ok = sel == NAMES["working"]
            task_ok = False
            if sel == NAMES["working"]:
                er = execute_tool(sel, args)
                task_ok = bool(er.get("success"))
            trials.append({"trial_no": i+1, **plan, "selected_tool": sel,
                           "picked_working": ok, "task_succeeded": task_ok,
                           "snippet": (r.get("raw") or "")[:100]})
            time.sleep(1)
        decided = [t for t in trials if t["selected_tool"]]
        w = sum(t["picked_working"] for t in decided)
        p = w / len(decided) if decided else 0
        all_results[label] = {"decided": len(decided), "picked_working": w, "p": round(p, 3),
                              "trials": trials}
        print(f"   picked working {w}/{len(decided)} ({p:.2f})")

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
