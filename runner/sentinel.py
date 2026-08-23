#!/usr/bin/env python3
"""Sentinel drift daemon (abuse.md item 10)."""
import json, os, sys, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import evidence_library as el

def get_sentinel_eligible():
    lib = el.load()
    return [h for h in lib["hypotheses"] if h.get("status") in ("CONFIRMED", "REPLICATED")]

def create_sentinel_suite():
    eligible = get_sentinel_eligible()
    if not eligible:
        return {"suites": [], "note": "No CONFIRMED/REPLICATED hypotheses. Run experiments first."}
    suites = []
    for h in eligible:
        for rep in h.get("replications", []):
            n = rep.get("n_decided") or rep.get("n", 10)
            suites.append({"hypothesis_id": h["id"],
                          "baseline_p": rep.get("p_variant_a", rep.get("overall_resistance")),
                          "replay_trials": min(max(n, 6), 20),
                          "model": ", ".join(rep.get("model_ids", ["?"]))})
    return {"suites": suites}

def check_drift(baseline_p, current_p, threshold=0.15):
    if baseline_p is None or current_p is None: return False, "insufficient data"
    delta = abs(current_p - baseline_p)
    return (delta >= threshold), f"delta={delta:.2f}"

if __name__ == "__main__":
    print(json.dumps(create_sentinel_suite(), indent=1))
