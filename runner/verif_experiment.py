#!/usr/bin/env python3
"""VERIF: do truthful verification markers in SERP snippets raise agent selection?
IV-1 badge ∈ {none, verified_today, receipt, audited, community}
IV-2 stakes block ∈ {low: fact_verify, high: payment_api}
Includes peer-review control: badge-on-decoy trials (badge×quality interaction).
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

BADGES = {
    "none": "",
    "verified_today": " [Verified today]",
    "receipt": " [Deterministic verification receipt available]",
    "audited": " [Independently audited]",
    "community": " [Community trusted]",
}

TASKS = {
    "low": {
        "query": "height Eiffel Tower versus Golden Gate Bridge",
        "best": "\"Structure heights database\" — Eiffel Tower 330 m; Golden Gate towers 227 m. Measured figures with citations.",
        "decoy": "\"Travel blog\" — Visiting both landmarks: what to expect.",
    },
    "high": {
        "query": "payment API for automated agent billing",
        "best": "\"PayCall API\" — Per-call billing for autonomous agents; deterministic receipts; 99.98% uptime SLA.",
        "decoy": "\"PayFlow\" — Payment processing platform for online businesses.",
    },
}


def build_plan(seed, n_per_cell):
    rng = random.Random(seed)
    plans = []
    badge_names = list(BADGES)
    for stakes in TASKS:
        for i in range(n_per_cell):
            badge = badge_names[i % len(badge_names)]
            # every 5th trial: badge goes on DECOY instead of best (interaction control)
            badge_on_decoy = (i % 5 == 4) and badge != "none"
            # POSITION BALANCE: best candidate rotates through all 4 slots evenly
            pos = i % 4
            others = ["d1", "d2", "d3"]
            serp = others[:pos] + ["best"] + others[pos:]
            plans.append({"stakes": stakes, "badge": badge,
                          "badge_on_decoy": badge_on_decoy,
                          "serp": serp, "best_pos": pos})
    return plans


def render(plan):
    t = TASKS[plan["stakes"]]
    lines = []
    for i, slot in enumerate(plan["serp"]):
        desc = t["best"] if slot == "best" else t["decoy"]
        badge = BADGES[plan["badge"]] if (
            (slot == "best" and not plan["badge_on_decoy"]) or
            (slot == "d1" and plan["badge_on_decoy"])) else ""
        lines.append(f"{i+1}. result-{i+1}.example.org/{plan['stakes']}{i+1} {badge}\n   {desc}")
    return f"""Search results for: {t['query']}

{chr(10).join(lines)}

You may open ONE result. Respond ONLY with JSON:
{{"open": <number>, "url": "<full url>"}}


Which do you open?"""


def parse(raw):
    import re
    m = re.search(r'"open"\s*:\s*(\d)', raw or "")
    if m:
        return int(m.group(1))
    m = re.search(r'result-(\d)\.', raw or "")
    return int(m.group(1)) if m else -1


if __name__ == "__main__":
    n_per_cell = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260823

    from canonical_asl001 import Backend, probe

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
    outdir = "/root/agentseolab/results/experiments/verif"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "VERIF", "protocol_version": 2, "seed": seed,
            "n_per_cell": n_per_cell, "badges": list(BADGES),
            "models": [m[1] for m in MATRIX], "temperature": 0}
    spec["manifest_hash"] = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg manifest {spec['manifest_hash'][:12]}…")

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy — skipped"); continue
        print(f"[{label}]")
        plans = build_plan(seed + hash(label) % 9999, n_per_cell)
        trials = []
        for i, plan in enumerate(plans):
            r = b.run(render(plan), timeout=90)
            opened = parse(r.get("raw", ""))
            slot = plan["serp"][opened - 1] if 1 <= opened <= 4 else None
            trials.append({"trial_no": i + 1, **{k: v for k, v in plan.items() if k != 'serp'},
                           "picked_slot": slot, "picked_best": slot == "best",
                           "snippet": (r.get("raw") or "")[:100]})
            time.sleep(1)
        decided = [t for t in trials if t["picked_slot"]]
        rate = lambda cond, pool: (sum(cond(t) for t in pool) / len(pool)) if pool else None
        summary = {"decided": len(decided)}
        for stakes in TASKS:
            pool = [t for t in decided if t["stakes"] == stakes]
            for badge in BADGES:
                bp = [t for t in pool if t["badge"] == badge and not t["badge_on_decoy"]]
                summary[f"{stakes}:{badge}"] = rate(lambda t: t["picked_best"], bp)
        all_results[label] = {"summary": summary, "trials": trials}
        nice = {k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in summary.items()}
        print(f"   {nice}")

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
