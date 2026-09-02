#!/usr/bin/env python3
"""Analyse ASL-001 v2 run output (results/experiments/asl001_v2/RUN_*.json)."""
import sys, json, glob
sys.path.insert(0, "/root/agentseolab/analysis")
from wilson import wilson

runs = sorted(glob.glob("/root/agentseolab/results/experiments/asl001_v2/RUN_*.json"))
if not runs:
    print("no runs found"); sys.exit(1)
data = json.load(open(runs[-1]))
spec = data["spec"]
print(f"ASL-001 v2 · manifest {spec['manifest_hash'][:16]}… · seed {spec['seed']} · n={spec['n_per_model']}/model\n")

rows = []
for label, res in data["results"].items():
    if res.get("status") != "ok":
        print(f"{label:22s} SKIPPED ({res.get('status')})")
        continue
    d, w = res["decided"], res["wins"]
    if not d:
        print(f"{label:22s} no decided trials"); continue
    ws = wilson(w, d)
    rows.append((label, w, d, ws))
    flag = "SIG" if ws["excludes_0.5"] else "ns "
    direction = "→ working" if ws["p"] > 0.5 else ("→ BROKEN" if ws["p"] < 0.5 else "tie")
    print(f"{label:22s} {w:>3}/{d:<3} p={ws['p']:<6} CI={ws['ci95']} {flag} {direction}")

sig_working = [r for r in rows if r[3]["excludes_0.5"] and r[1]/r[2] > 0.5]
sig_broken  = [r for r in rows if r[3]["excludes_0.5"] and r[1]/r[2] < 0.5]
print(f"\nSignificant pro-working : {[r[0] for r in sig_working]}")
print(f"Significant pro-broken  : {[r[0] for r in sig_broken]}")
print(f"Family-clustered seduction CONFIRMED iff ≥1 family significant each way")
