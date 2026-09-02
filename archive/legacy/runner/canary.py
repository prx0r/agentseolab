#!/usr/bin/env python3
"""Canary factory v2 — validated, identity-scored, provenance-rich.

Fixes vs invalidated v1:
- keyword-only args (job can never be shadowed by backend)
- immutable tool_id identities; scorer matches exact display names mapped to
  ids; UNPARSEABLE distinct from incorrect
- substring-collision rejected by validator
- seed-driven balanced randomized ordering
- full per-trial runtime provenance
"""
import json, os, sys, time, random, argparse
sys.path.insert(0, os.path.dirname(__file__))
from backends import get_backend
from validator import validate_canary
from provenance import trial_provenance, phash

def build_domain_canary_spec(seed=20260823, n_per=3):
    return {
      "capability_id": "domain_availability_verify",
      "job": "Check whether the domain name example-name.com is currently available to register.",
      "real_tool": {
        "tool_id": "tool_real_001", "name": "domain.verify",
        "description": "Check current domain registration availability using authoritative registry evidence (RDAP) with live DNS cross-check. Returns verified status and timestamp."},
      "decoys": [
        {"tool_id":"tool_decoy_001","class":"semantic_decoy","name":"domain.scout",
         "description":"Discover domains mentioned across web pages that match your topic. Great for finding domains similar to a keyword."},
        {"tool_id":"tool_decoy_002","class":"parameter_trap","name":"registry.replay",
         "description":"Verify a domain by supplying registry_id (internal numeric ID), zone_transfer_key, and the full historical WHOIS blob. All three parameters are required."},
        {"tool_id":"tool_decoy_003","class":"capability_mirage","name":"dominatron.pro",
         "description":"Enterprise-grade complete domain intelligence platform: verification, valuation, traffic estimation, trademark screening and registration insights."},
        {"tool_id":"tool_decoy_004","class":"prerequisite_blindness","name":"trustchain.verify",
         "description":"Cryptographically attested domain status. Requires pre-provisioned registrar API credentials and an active enterprise agreement before any lookup."},
        {"tool_id":"tool_decoy_005","class":"temporal_decoy","name":"snapshot.check",
         "description":"Domain availability from a cached index refreshed every 30 days. Optimized for fast bulk lookups at zero cost."},
        {"tool_id":"tool_decoy_006","class":"granularity_trap","name":"netlens.sweep",
         "description":"Internet-wide scanning suite: ports, certificates, DNS zones, registrations, subdomains and more in one comprehensive sweep."},
      ],
      "n_trials_per_decoy": n_per,
      "seed": seed,
    }

def run_canary(*, spec: dict, backend_obj, backend_name: str):
    validate_canary(spec)
    rng = random.Random(spec["seed"])
    real = spec["real_tool"]
    name2id = {real["name"]: real["tool_id"]}
    for d in spec["decoys"]: name2id[d["name"]] = d["tool_id"]

    traces, fitness = [], {}
    for decoy in spec["decoys"]:
        # seed-driven ordering: balanced but randomized sequence
        orders = [True, False] * spec["n_trials_per_decoy"]
        rng.shuffle(orders)
        correct = 0; rows = []
        for i, real_first in enumerate(orders):
            if real_first:
                tools = "\n".join(f"- {real['name']}: {real['description']}\n- {decoy['name']}: {decoy['description']}".split("\n"))
                block = f"Tool A — {real['name']}: {real['description']}\n\nTool B — {decoy['name']}: {decoy['description']}"
            else:
                block = f"Tool A — {decoy['name']}: {decoy['description']}\n\nTool B — {real['name']}: {real['description']}"
            prompt = (f"You are an autonomous agent. Job: {spec['job']}\n\nAvailable tools:\n\n{block}\n\n"
                      f"Which ONE tool do you use for this job? Respond with ONLY the exact tool name.")
            r = backend_obj.run(prompt)
            raw = (r.get("raw") or "").strip()
            picked_name = next((n for n in name2id if n in raw), None)
            selection_id = name2id.get(picked_name, "UNPARSEABLE")
            got = (selection_id == real["tool_id"])
            correct += bool(got)
            prov = trial_provenance(backend_obj, prompt, raw,
                                    ordering="REAL_FIRST" if real_first else "DECOY_FIRST")
            rows.append({**prov, "picked_raw": picked_name or raw[:40],
                         "selection_id": selection_id, "correct": got})
            time.sleep(0.2)
        fitness[decoy["class"]] = {"resistance": correct / len(rows), "n": len(rows)}
        traces += rows
        print(f"  {decoy['class']:24s} resistance {correct}/{len(rows)}")

    overall = round(sum(f["resistance"] for f in fitness.values()) / len(fitness), 3)
    print(f"\nOVERALL decoy_resistance: {overall}  (model={getattr(backend_obj,'model','?')})")
    return {
        "kind": "canary", "capability_id": spec["capability_id"],
        "spec_hash": phash(json.dumps(spec, sort_keys=True)),
        "backend": backend_name,
        "model_id": getattr(backend_obj, "model", "?"),
        "fitness": fitness, "overall_resistance": overall, "traces": traces,
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default=os.environ.get("ASL_BACKEND", "opencode"))
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    bobj, _ = get_backend(args.backend)
    spec = build_domain_canary_spec(n_per=args.n)
    res = run_canary(spec=spec, backend_obj=bobj, backend_name=args.backend)
    out = args.out or f"/root/agentseolab/runs/canary_v2_{args.backend}_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1)
    print("saved:", out)
