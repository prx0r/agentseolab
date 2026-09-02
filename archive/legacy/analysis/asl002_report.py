#!/usr/bin/env python3
"""ASL-002 v2 analysis: per-family arm comparison.
Question per family: does moving fluff onto the working tool raise P(pick working)?
"""
import sys, json, glob
sys.path.insert(0, "/root/agentseolab/analysis")
from wilson import wilson

runs = sorted(glob.glob("/root/agentseolab/results/experiments/asl002_v2/RUN_*.json"))
fams = {}
for f in runs:
    d = json.load(open(f))
    label = d["spec"]["model"].split("/")[-1][:26]
    fams.setdefault(label, []).append(d)

print(f"{'family':28s} {'FB arm':>10s} {'FW arm':>10s}  shift   reading")
print("-" * 88)
for label, ds in sorted(fams.items()):
    arms = {"fluff_broken": [0, 0], "fluff_working": [0, 0]}
    for d in ds:
        for t in d["trials"]:
            if not t.get("executed"):
                continue
            a = t["plan"]["arm"]
            arms[a][1] += 1
            if t.get("picked_working"):
                arms[a][0] += 1
    fb_w, fb_n = arms["fluff_broken"]
    fw_w, fw_n = arms["fluff_working"]
    if not fb_n or not fw_n:
        print(f"{label:28s} incomplete"); continue
    p_fb = fb_w / fb_n
    p_fw = fw_w / fw_n
    c_fb = wilson(fb_w, fb_n)
    c_fw = wilson(fw_w, fw_n)
    shift = p_fw - p_fb
    if shift > 0.15 and c_fw["excludes_0.5"]:
        reading = "attraction follows DESCRIPTION"
    elif abs(shift) <= 0.15:
        reading = "loyal to tool identity" if p_fb < 0.5 else "competence-dominated"
    else:
        reading = "shift away from fluff"
    print(f"{label:28s} {str(fb_w)+'/'+str(fb_n):>10s} {str(fw_w)+'/'+str(fw_n):>10s} "
          f"{shift:+.2f}   {reading}  CI_FB={c_fb['ci95']} CI_FW={c_fw['ci95']}")
