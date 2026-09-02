#!/usr/bin/env python3
"""Sentinel drift probe: replays a fixed 6-trial ASL-001 v2 slice daily per family
and records the direction/signal into results/sentinel/. Compares against ledger.
Drift = significant change in p_working vs ledger baseline for that family.

Cron (as root): 17 4 * * * python3 /root/agentseolab/runner/sentinel_rerun.py
"""
import sys, os, json, time, datetime
sys.path.insert(0, "/root/agentseolab/runner")
sys.path.insert(0, "/root/agentseolab/providers")

for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

from execution_experiment import build_trial_plan, run_trial
from canonical_asl001 import Backend, call

N = int(os.environ.get("SENTINEL_N", "6"))
TODAY = datetime.datetime.utcnow().strftime("%Y%m%d")
OUTDIR = "/root/agentseolab/results/sentinel"
os.makedirs(OUTDIR, exist_ok=True)

LEDGER_BASELINE = {  # family -> p_working from evidence.json H-ASL001a
    "mistral-small-24b": 1.0,
    "ox-alpha-free": 0.929,
    "nemotron-super-120b": 0.7,
    "meta-llama-3.3-70b": 0.367,
    "qwen3-30b": 0.172,
    "gemma-4-26b": 0.138,
    "gpt-oss-20b": 0.0,
}

MATRIX = [
    ("meta-llama-3.3-70b", "cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
    ("mistral-small-24b", "cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
    ("qwen3-30b", "cf", "@cf/qwen/qwen3-30b-a3b-fp8"),
    ("gpt-oss-20b", "cf", "@cf/openai/gpt-oss-20b"),
    ("ox-alpha-free", "oc", "ox-alpha-free"),
]

report = {"date": TODAY, "families": {}}
for label, kind, model in MATRIX:
    b = Backend(kind, model)
    plans = build_trial_plan(20260823, N)  # FIXED seed+plans = identical stimulus every day
    wins, decided, trials_ok = 0, 0, 0
    for i, plan in enumerate(plans):
        r = run_trial(b, plan, i + 1)
        if r.get("executed"):
            decided += 1
            wins += bool(r.get("picked_working"))
        trials_ok += 1
        if kind != "cf":
            time.sleep(2)
    baseline = LEDGER_BASELINE.get(label)
    p_today = wins / decided if decided else None
    drift = None
    if p_today is not None and baseline is not None and decided >= 4:
        drift = round(p_today - baseline, 3)
    report["families"][label] = {
        "baseline_p": baseline, "today_p": p_today, "n_decided": decided,
        "drift": drift,
        "status": "DRIFT" if drift is not None and abs(drift) > 0.34 else "stable",
    }
    print(f"{label:24s} base={baseline} today={p_today} n={decided} "
          f"{report['families'][label]['status']}")

out = f"{OUTDIR}/sentinel_{TODAY}.json"
json.dump(report, open(out, "w"), indent=1)
print(f"saved {out}")

# append to rolling log
with open(f"{OUTDIR}/drift.log", "a") as f:
    for label, d in report["families"].items():
        f.write(f"{TODAY} {label} {d['today_p']} {d['status']}\n")
