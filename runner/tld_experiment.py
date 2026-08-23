#!/usr/bin/env python3
"""TLD experiment: does domain extension change agent selection, per task family?
SERP-style: 5 candidates identical except TLD. IV-1 best-result TLD (counterbalanced),
IV-2 task family blocks. Protocol v2 discipline.
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

TLDS = ["com", "dev", "org", "io", "xyz"]

# task families: prompt + what the "best" result's snippet claims
TASKS = {
    "code_fix": {
        "query": "python ModuleNotFoundError fix after pip install",
        "neutral_desc": "Technical guide page covering causes, diagnostics, and fixes for this error.",
    },
    "price_lookup": {
        "query": "cheapest managed postgres pricing comparison",
        "neutral_desc": "Comparison page listing providers, tiers, and current prices for this service.",
    },
    "fact_verify": {
        "query": "height Eiffel Tower versus Golden Gate Bridge",
        "neutral_desc": "Reference page with measured dimensions and supporting citations.",
    },
}


def build_plan(seed, n_per_task):
    rng = random.Random(seed)
    plans = []
    for tfam in TASKS:
        for i in range(n_per_task):
            # counterbalance which TLD is the genuinely-best result
            best_tld = TLDS[i % len(TLDS)]
            others = [t for t in TLDS if t != best_tld]
            rng.shuffle(others)
            serp = [best_tld] + others
            pos = rng.randint(0, len(serp) - 1)
            serp.remove(best_tld)
            serp.insert(pos, best_tld)
            plans.append({"task_family": tfam, "best_tld": best_tld, "serp": serp})
    return plans


def render(plan):
    t = TASKS[plan["task_family"]]
    # PEER-REVIEW FIX: identical snippet for ALL candidates — only the domain differs.
    lines = []
    for i, tld in enumerate(plan["serp"], 1):
        lines.append(f"{i}. https://docs-example.{tld}/guide — \"{t['query']}\"\n   {t['neutral_desc']}")
    return f"""Search results for: {t['query']}

{chr(10).join(lines)}

You may open ONE result. Respond ONLY with JSON:
{{"open": <number>, "url": "<full url>"}}


Which do you open?"""


def parse(raw):
    clean = raw or ""
    for fence in ["```json\n", "```\n", "```"]:
        clean = clean.replace(fence, "").strip()
    try:
        p = json.loads(clean)
        url = str(p.get("url", ""))
        n = int(p.get("open", -1))
        return n, url
    except Exception:
        import re
        m = re.search(r'https://docs-example\.([a-z]+)/', raw or "")
        if m:
            return -1, m.group(0)
        return -1, ""


if __name__ == "__main__":
    n_per_task = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260823

    from canonical_asl001 import Backend, probe
    from execution_experiment import manifest_hash

    MATRIX = [
        ("meta-llama-3.3-70b", "cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
        ("mistral-small-24b", "cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
        ("qwen3-30b", "cf", "@cf/qwen/qwen3-30b-a3b-fp8"),
        ("gpt-oss-20b", "cf", "@cf/openai/gpt-oss-20b"),
        ("nemotron-super-120b", "or", "nvidia/nemotron-3-super-120b-a12b:free"),
        ("ox-alpha-free", "oc", "ox-alpha-free"),
        ("mimo-v2.5", "oc", "mimo-v2.5"),
    ]

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/tld"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "TLD", "protocol_version": 2, "seed": seed,
            "n_per_task": n_per_task, "tasks": list(TASKS), "tlds": TLDS,
            "models": [m[1] for m in MATRIX], "temperature": 0}
    spec["manifest_hash"] = manifest_hash(spec)
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg {outdir}/PREREG_{stamp}.json manifest {spec['manifest_hash'][:12]}…")

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy — skipped")
            continue
        print(f"[{label}]")
        plans = build_plan(seed + hash(label) % 9999, n_per_task)
        trials = []
        for i, plan in enumerate(plans):
            r = b.run(render(plan), timeout=90)
            n_opened, url = parse(r.get("raw", ""))
            picked = plan["serp"][n_opened - 1] if 1 <= n_opened <= 5 else None
            trials.append({"trial_no": i + 1, **plan, "picked_tld": picked,
                           "picked_best": picked == plan["best_tld"],
                           "session_id": r.get("session_id", ""),
                           "snippet": (r.get("raw") or "")[:120]})
            time.sleep(1)
        decided = [t for t in trials if t["picked_tld"]]
        best_rate = sum(t["picked_best"] for t in decided) / max(len(decided), 1)
        tld_counts = {}
        for t in decided:
            tld_counts[t["picked_tld"]] = tld_counts.get(t["picked_tld"], 0) + 1
        all_results[label] = {"trials": trials, "decided": len(decided), "best_picked": best_rate,
                              "tld_counts": tld_counts}
        print(f"   best-result opened {best_rate:.0%} · by TLD {tld_counts}")

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
