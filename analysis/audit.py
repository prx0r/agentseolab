#!/usr/bin/env python3
"""agentseolab audit — anti-theatre gate.
Verifies evidence integrity before any finding can be trusted."""
import json, os, sys, hashlib, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

ISSUES = []
def check(name, ok, detail=""):
    status = "✓" if ok else "✗ FAIL"
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    if not ok: ISSUES.append((name, detail))

def run_audit(runs_dir="/root/agentseolab/runs", lib_path="/root/agentseolab/evidence_library.json"):
    print("=== AgentSEOLab Evidence Audit ===\n")
    
    # 1. All runs have valid JSON
    run_files = [f for f in glob.glob(f"{runs_dir}/exp_*.json") if ".spec." not in f]
    spec_files = set(glob.glob(f"{runs_dir}/*.spec.json"))
    bad_json = []
    for f in run_files:
        try: json.load(open(f))
        except: bad_json.append(f)
    check("all runs parseable JSON", len(bad_json) == 0, f"{len(bad_json)} corrupt" if bad_json else "")
    
    # 2. Every non-spec run references a spec
    orphaned = [f for f in run_files if f.replace(".json",".spec.json") not in spec_files]
    check("every run has frozen spec", len(orphaned) == 0, f"orphaned: {orphaned}" if orphaned else "")
    
    # 3. Manifest hashes recompute
    import hashlib
    def chash(obj):
        def canon(v):
            if isinstance(v, dict): return {k: canon(v[k]) for k in sorted(v.keys())}
            if isinstance(v, list): return [canon(x) for x in v]
            return v
        return "sha256:" + hashlib.sha256(json.dumps(canon(obj), sort_keys=False, separators=(",",":")).encode()).hexdigest()
    hash_ok = True
    for sf in sorted(spec_files):
        d = json.load(open(sf))
        stored = d.pop("manifest_hash", None)
        if stored and chash(d) != stored:
            hash_ok = False
            print(f"    HASH MISMATCH in {sf}")
        d["manifest_hash"] = stored  # restore
    check("manifest hashes recompute", hash_ok)
    
    # 4. No INVALIDATED hypothesis is sentinel-active
    lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {"hypotheses":[]}
    inv_active = [h["id"] for h in lib.get("hypotheses",[])
                  if h.get("status") == "INVALIDATED"
                  and h.get("sentinel_active")]
    check("no INVALIDATED finding is sentinel-active", len(inv_active) == 0,
          str(inv_active) if inv_active else "")
    
    # 5. Evidence library exists
    check("evidence library exists", os.path.exists(lib_path))
    
    n_hyp = len(lib.get("hypotheses",[]))
    statuses = {}
    for h in lib.get("hypotheses",[]): 
        s = h.get("status","?")
        statuses[s] = statuses.get(s,0)+1
    
    print(f"\n=== Summary ===")
    print(f"Runs: {len(run_files)} · Specs: {len(spec_files)} · Hypotheses: {n_hyp}")
    print(f"Hypothesis states: {statuses}")
    print(f"Issues: {len(ISSUES)}")
    
    return len(ISSUES) == 0

if __name__ == "__main__":
    import time; time.sleep(0.1)
    ok = run_audit()
    import sys; sys.exit(0 if ok else 1)
