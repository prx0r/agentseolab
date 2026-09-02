#!/usr/bin/env python3
"""Analysis for SERP-style RUN files (tld/, naming01/, verif/).
Per model x cell: Wilson CI on the primary proportion + reading.
"""
import sys, json, glob
sys.path.insert(0, "/root/agentseolab/analysis")
from wilson import wilson


def analyze(outdir, metric_key, cells_fn, label_fn=None):
    rows = []
    for f in sorted(glob.glob(f"/root/agentseolab/results/experiments/{outdir}/RUN_*.json")):
        d = json.load(open(f))
        for model, res in d["results"].items():
            by_cell = {}
            for t in res["trials"]:
                if t.get(metric_key) is None or t.get(metric_key) is False and not isinstance(t.get(metric_key), bool):
                    pass
                c = cells_fn(t)
                cell = by_cell.setdefault(c, [0, 0])
                cell[1] += 1
                if t.get(metric_key):
                    cell[0] += 1
            for cell, (k, n) in sorted(by_cell.items()):
                w = wilson(k, n)
                rows.append((model, cell, k, n,
                             f"{w['p']:.2f} [{w['ci95'][0]:.2f},{w['ci95'][1]:.2f}]"
                             + (" *" if w.get("excludes_half") or w.get("excludes_0.5") else "")))
    print(f"{'model':26s} {'cell':22s} {'k/n':>8s}  p [CI95]")
    print("-" * 80)
    for r in sorted(rows):
        lab = label_fn(r[1]) if label_fn else str(r[1])
        print(f"{r[0]:26s} {lab:22s} {f'{r[2]}/{r[3]}':>8s}  {r[4]}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "tld"
    if which == "tld":
        analyze("tld", "picked_best", lambda t: t["task_family"])
    elif which == "naming01":
        analyze("naming01", "picked_target", lambda t: t["arm"])
    elif which == "verif":
        analyze("verif", "picked_best", lambda t: f'{t["stakes"]}|{t["badge"]}'
                + ("|decoy" if t.get("badge_on_decoy") else ""))
