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
        if 'summary' not in d: continue  # canary/fitness files use their own format
        s = d['summary']
        key = d["experiment_id"]
        matchups.setdefault(key, {"a_wins": s.get("a",0), "b_wins": s.get("b",0),
                                  "n": s.get("a",0)+s.get("b",0)})
    return matchups

from wilson import wilson

def bt_estimate(wins_a, wins_b, **_):
    """Two-candidate proportion + Wilson score CI.
    (True Bradley-Terry applies to multi-candidate tournaments; see abuse.md P0.)"""
    if wins_a + wins_b == 0: return None
    r = wilson(wins_a, wins_a + wins_b)
    return {"p_variant_a": r["p"], "ci95": r["ci95"], "n_decided": r["n"],
            "significant": r["excludes_0.5"]}

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
