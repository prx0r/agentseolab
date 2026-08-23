#!/usr/bin/env python3
"""Bradley-Terry + bootstrap analysis from raw trial runs (abuse.md item 5).
Reads runs/*.json, produces effect sizes w/ uncertainty. Regenerable from raw."""
import json, glob, sys, random

def collect(runs_dir="/root/agentseolab/runs"):
    """Aggregate pairwise outcomes per (experiment, variant_a, variant_b)."""
    matchups = {}
    for f in glob.glob(f"{runs_dir}/*.json"):
        if f.endswith(".spec.json"): continue
        d = json.load(open(f))
        s = d["summary"]
        key = d["experiment_id"]
        matchups.setdefault(key, {"a_wins": s.get("a",0), "b_wins": s.get("b",0),
                                  "n": s.get("a",0)+s.get("b",0)})
    return matchups

def bt_estimate(wins_a, wins_b, n_iter=2000):
    """Simple BT MLE for two items: p(a) = wins_a/(wins_a+wins_b).
    Bootstrap CI over binomial resampling. Returns pct, lo95, hi95."""
    if wins_a + wins_b == 0: return None
    p = wins_a / (wins_a + wins_b)
    rng = random.Random(42)
    boot = []
    for _ in range(n_iter):
        wa = sum(1 for _ in range(wins_a+wins_b) if rng.random() < p)
        boot.append(wa / (wa + wins_b) if (wa + wins_b) else 0.5)
    boot.sort()
    return {"p_variant_a": round(p,3),
            "ci95": [round(boot[int(0.025*n_iter)],3), round(boot[int(0.975*n_iter)],3)],
            "n_decided": wins_a + wins_b,
            "significant": abs(p-0.5) > 0 and not
                (boot[int(0.025*n_iter)] <= 0.5 <= boot[int(0.975*n_iter)])}

def report():
    rows = []
    for exp_id, m in sorted(collect().items()):
        est = bt_estimate(m["a_wins"], m["b_wins"])
        if est:
            rows.append((exp_id, est))
            sig = "✓ SIGNIFICANT" if est["significant"] else "· n.s."
            print(f"{exp_id}: P(A)={est['p_variant_a']} CI95={est['ci95']} "
                  f"n={est['n_decided']} {sig}")
    if not rows: print("No decided experiments yet.")
    return rows

if __name__ == "__main__":
    report()
