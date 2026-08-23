#!/usr/bin/env python3
import datetime
"""Pristine cross-family replication experiment.
Same controlled stimulus, two genuinely different model families.
Produces the first REPLICATED-or-not verdict."""
import sys, os, json, time, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
sys.path.insert(0, os.path.dirname(__file__))
from backends import get_backend
from provenance import trial_provenance
from wilson import wilson

EV = "Ends subscriptions via verified cancellation routes checked against live registry evidence today. Returns confirmation with timestamp."
PR = "Manages subscription lifecycle through structured workflow: locate billing source, select cancellation path, confirm end date."
JOB = "I need to cancel a subscription service."
NAMES = ["tool_alpha", "tool_beta"]
N_PAIRS = 6  # 12 trials per family

def run_family(backend_obj, family_name, seed):
    rng = random.Random(seed)
    wins_ev = wins_pr = 0
    trials = []
    orders = ["EF", "PF"] * N_PAIRS
    rng.shuffle(orders)
    
    for i, order in enumerate(orders):
        # Name-description decoupling: alternate assignment
        if i % 2 == 0:
            n_ev, n_pr = NAMES[0], NAMES[1]
        else:
            n_ev, n_pr = NAMES[1], NAMES[0]
        
        ev_d = EV; pr_d = PR
        
        if order == "EF":
            prompt = f"{JOB}\n\nAvailable tools:\n\nTool {n_ev}: {ev_d}\n\nTool {n_pr}: {pr_d}\n\nWhich tool do you use? Reply with ONLY the tool name."
        else:
            prompt = f"{JOB}\n\nAvailable tools:\n\nTool {n_pr}: {pr_d}\n\nTool {n_ev}: {ev_d}\n\nWhich tool do you use? Reply with ONLY the tool name."
        
        r = backend_obj.run(prompt)
        raw = (r.get("raw") or "").strip()
        
        # Parse by exact name match
        picked = None
        if n_ev in raw and n_pr not in raw:
            picked = "evidence"
        elif n_pr in raw and n_ev not in raw:
            picked = "process"
        elif "neither" in raw.lower() or "abstain" in raw.lower():
            picked = "abstain"
        
        if picked == "evidence": wins_ev += 1
        elif picked == "process": wins_pr += 1
        
        prov = trial_provenance(backend_obj, prompt, raw, ordering=order)
        trials.append({**prov, "trial_no": len(trials)+1,
                       "picked": picked or "unparseable",
                       "raw_snippet": raw[:100],
                       "latency_ms": r.get("latency_ms", 0)})
        print(f"    t{i+1} [{order}] → {picked} ({r['latency_ms']}ms)")
    
    n_dec = wins_ev + wins_pr
    w = wilson(wins_ev, n_dec) if n_dec else None
    return {
        "family_name": family_name,
        "wins_evidence": wins_ev,
        "wins_process": wins_pr,
        "n_decided": n_dec,
        "p_evidence": round(wins_ev/n_dec, 3) if n_dec else None,
        "wilson_ci": w["ci95"] if w else None,
        "ci_g_excl": w["g_excl"] if w else False,
        "trials": trials,
    }

if __name__ == "__main__":
    from opencode_direct import OpenCodeDirect
    from backends import CloudflareBackend
    
    families = [
        ("ox-alpha-free", OpenCodeDirect()),
        ("llama-3.3-70b", CloudflareBackend(model="@cf/meta/llama-3.3-70b-instruct-fp8-fast")),
    ]
    
    all_families = []
    for name, backend in families:
        print(f"\n{'='*50}")
        print(f"FAMILY: {name}")
        print(f"{'='*50}")
        
        probe = backend.run("Say OK", timeout=30)
        if not probe.get("ok"):
            print(f"  UNHEALTHY — skipping")
            continue
        
        result = run_family(backend, name, seed=20260823)
        all_families.append(result)
        
        w = wilson(result["wins_evidence"], result["n_decided"]) if result["n_decided"] else None
        if w:
            sig = "✓ SIGNIFICANT" if w["g_excl"] else "· n.s."
            print(f"  → P(evidence)={w['p']} CI95={w['ci95']} {sig}")
    
    # Cross-family verdict
    print(f"\n{'='*50}")
    print("CROSS-FAMILY VERDICT")
    print(f"{'='*50}")
    
    decided = [f for f in all_families if f["n_decided"] >= 4]
    if len(decided) < 2:
        print("Insufficient data (<2 families with ≥4 decided trials)")
    else:
        directions = []
        for f in decided:
            p = f["p_evidence"]
            d = "+" if p > 0.5 else ("-" if p < 0.5 else "0")
            directions.append(d)
            ci_excl = f["ci_g_excl"]
            print(f"  {f['family_name']}: P={f['p_evidence']} CI={f['wilson_ci']} dir={d} ci_excl={ci_excl}")
        
        same_dir = len(set(directions)) == 1
        both_sig = all(f["ci_g_excl"] for f in decided)
        total_n = sum(f["n_decided"] for f in decided)
        
        if same_dir and both_sig and total_n >= 20:
            verdict = "REPLICATED ✓✓"
        elif same_dir and total_n >= 10:
            verdict = "CONFIRMED (single direction, needs more data for REPLICATED)"
        else:
            verdict = f"NOT REPLICATED (directions={directions}, both_sig={both_sig})"
        
        print(f"\nVERDICT: {verdict} (total n={total_n})")
    
    # Save
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/results/experiments/cross_family_{stamp}.json"
    json.dump({"kind": "cross_family", "families": all_families, 
               "timestamp": datetime.datetime.utcnow().isoformat()+"Z"}, 
              open(out, "w"), indent=1)
    print(f"\nsaved: {out}")

import datetime
