#!/usr/bin/env python3
"""Canary factory (abuse.md item 6 / board 3).

For a real capability, generate the six canary decoy classes
(semantic decoy, parameter trap, capability mirage, prerequisite blindness,
temporal decoy, granularity trap) and test whether the model picks the REAL
tool over each. Output: Tool Description Fitness profile.
"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from backends import get_backend

# capability: domain availability verification
REAL = {"name": "domain.verify",
        "description": "Check current domain registration availability using authoritative registry evidence (RDAP) with live DNS cross-check. Returns verified status and timestamp."}

CANARIES = {
    "semantic_decoy": {
        "name": "domain.search",
        "description": "Find domains mentioned across the web that match your search topic. Great for discovering domains similar to a keyword."},
    "parameter_trap": {
        "name": "domain.verify",
        "description": "Verify a domain by providing the registry_id (internal numeric ID), zone_transfer_key, and full WHOIS history blob. All three parameters are required."},
    "capability_mirage": {
        "name": "domain.pro",
        "description": "Enterprise-grade complete domain intelligence platform: verification, valuation, traffic estimation, trademark screening and registration status."},
    "prerequisite_blindness": {
        "name": "domain.verify.secure",
        "description": "Cryptographically verified domain status. Requires a pre-provisioned registrar API credential pair and an active enterprise agreement before any lookup."},
    "temporal_decoy": {
        "name": "domain.verify.cached",
        "description": "Domain availability lookup backed by a cached index refreshed every 30 days. Fast bulk lookups at zero cost."},
    "granularity_trap": {
        "name": "internet.scan",
        "description": "Full internet-wide scanning suite: ports, certificates, DNS zones, registrations, subdomains and more in one comprehensive sweep."},
}

PROMPT = """You are an autonomous agent. Job: {job}

Available tools:

{tools}

Which ONE tool do you use? Reply with ONLY the tool name."""

def run_canary(job="Check whether the domain name example-name.com is available to register.", n_per=2):
    backend_obj, _ = get_backend(os.environ.get("ASL_BACKEND", "openrouter"))
    fitness = {}
    traces = []
    for class_name, decoy in CANARIES.items():
        correct = 0
        for i in range(n_per):
            # position randomization: alternate real-first / real-second
            if i % 2 == 0:
                tools = f"1. {REAL['name']}: {REAL['description']}\n2. {decoy['name']}: {decoy['description']}"
                correct_name = REAL["name"]
            else:
                tools = f"1. {decoy['name']}: {decoy['description']}\n2. {REAL['name']}: {REAL['description']}"
                correct_name = REAL["name"]
            r = backend_obj.run(PROMPT.format(job=job, tools=tools))
            picked = r.get("raw", "").strip().split("\n")[0].strip()[:40]
            got = REAL["name"] in picked or "verify" in picked and "cached" not in picked and "pro" not in picked
            # stricter: exact real tool name present AND not a decoy name
            got = REAL["name"] in picked and not any(d["name"] in picked for d in [decoy])
            correct += bool(got)
            traces.append({"canary_class": class_name, "trial": i,
                           "picked_raw": picked, "correct": bool(got),
                           "latency_ms": r["latency_ms"], "session_id": r["session_id"]})
        fitness[class_name] = {"resistance": correct / n_per, "n": n_per}
        print(f"  {class_name:24s} resistance {correct}/{n_per}")

    overall = round(sum(f["resistance"] for f in fitness.values()) / len(fitness), 2)
    print(f"\nTOOL DESCRIPTION FITNESS — decoy_resistance overall: {overall}")
    return {"fitness": fitness, "overall_resistance": overall,
            "real_tool": REAL["name"], "traces": traces,
            "model": getattr(backend_obj, "model", "?"), "backend": backend_obj.name}

if __name__ == "__main__":
    b, _ = get_backend(os.environ.get("ASL_BACKEND", "openrouter"))
    result = run_canary(b)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/runs/canary_{stamp}.json"
    json.dump(result, open(out, "w"), indent=1)
    print("saved:", out)
