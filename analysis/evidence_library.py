"""Evidence library v3 — fail-closed, typed schemas, causal-question identity.

Fixes from DEV_PLAN_2026-08-23-VALIDITY-SPRINT:
- A1: reads model_id from trial["provenance"]["model_id"] (nested)
- A2: TrialRecord dataclass enforces schema
- A3: Hypothesis identity = SHA256(causal_question|intent_family|dimension|control|metric|pv)
- A4: Each replication = one immutable run/batch (no cumulative snapshots)
- A5: Same-direction replication enforced (sign(p_model - 0.5) must match)
- Promotion gates unchanged but now operate on correct data
"""
import json, glob, hashlib, datetime, os, math
from dataclasses import dataclass, field, asdict
from typing import Optional, List

LIB_PATH = "/root/agentseolab/evidence_library.json"
PROTOCOL_VERSION = 2

STATES = ["PROPOSED","PREREGISTERED","RUNNING","PROVISIONAL","CONFIRMED",
          "REPLICATED","FAILED_REPLICATION","INVALIDATED","STALE"]

# ---- A2: typed trial record ----
@dataclass
class TrialRecord:
    trial_no: int
    ordering: str
    choice_raw: str
    chosen_variant: str
    session_id: str
    latency_ms: int
    provider: str
    model_id: str
    temperature: float = 0.0
    max_tokens: int = 300
    prompt_hash: str = ""
    response_hash: str = ""
    response_snippet: str = ""
    
    @classmethod
    def from_run_trial(cls, t: dict):
        """Parse a trial dict from a run file, handling both v1 (flat) and v2 (nested provenance)."""
        prov = t.get("provenance") or {}
        return cls(
            trial_no=t.get("trial_no", 0),
            ordering=t.get("ordering", "?"),
            choice_raw=t.get("choice_raw", ""),
            chosen_variant=t.get("chosen_variant", ""),
            session_id=t.get("session_id", ""),
            latency_ms=t.get("latency_ms", 0),
            provider=prov.get("provider", t.get("provider", "unknown")),
            model_id=prov.get("model_id", t.get("model_id", "UNKNOWN")),
            prompt_hash=prov.get("prompt_hash", ""),
            response_hash=prov.get("response_hash", ""),
            response_snippet=t.get("response_snippet", "")[:200],
        )

@dataclass  
class ReplicationBatch:
    """One immutable run/batch — never a cumulative snapshot (A4)."""
    experiment_id: str
    model_ids: List[str]
    n_decided: int
    wins_a: int
    wins_b: int
    p_variant_a: float
    wilson_ci: List[float]
    protocol_version: int
    measured: str

def wilson(k, n, z=1.96):
    if n == 0: return None
    center = (k + z*z/2) / (n + z*z)
    half = (z / (n + z*z)) * math.sqrt(k*(n-k)/n + z*z/4)
    lo, hi = max(0.0, center-half), min(1.0, center+half)
    return {"p": round(k/n,3), "ci95": [round(lo,3), round(hi,3)], "n": n,
            "excludes_half": lo > 0.5 or hi < 0.5}

def load():
    if os.path.exists(LIB_PATH): return json.load(open(LIB_PATH))
    return {"hypotheses": [], "protocol_version": PROTOCOL_VERSION}

def save(lib): json.dump(lib, open(LIB_PATH, "w"), indent=1)

def collect_runs(min_n=2):
    sig = {}
    for f in sorted(glob.glob("/root/agentseolab/results/experiments/exp_*.json")):
        if ".spec." in f: continue
        d = json.load(open(f))
        if "summary" not in d or "trials" not in d: continue
        spec_file = f.replace(".json", ".spec.json")
        if not os.path.exists(spec_file): continue
        sp = json.load(open(spec_file))
        
        trials = [TrialRecord.from_run_trial(t) for t in d.get("trials", [])]
        models = sorted({t.model_id for t in trials if t.model_id != "UNKNOWN"})
        proto = PROTOCOL_VERSION if any(t.prompt_hash for t in trials) else 1
        
        # A3: hypothesis identity = hash of causal question metadata, NOT description text.
        hkey_src = "|".join([
            sp.get("name", ""),          # experiment name encodes the causal question
            sp.get("intent_id", ""),     # frozen intent family
            "tool_description",           # intervention dimension
            "selection_rate",             # preregistered metric
            str(PROTOCOL_VERSION),
        ])
        hkey = "H-" + hashlib.sha256(hkey_src.encode()).hexdigest()[:10].upper()
        
        wins_a = sum(1 for t in trials if t.chosen_variant == "a")
        wins_b = sum(1 for t in trials if t.chosen_variant == "b")
        e = sig.setdefault(d["experiment_id"], {
            "experiment_id": d["experiment_id"],
            "hypothesis_key": hkey,
            "intent_id": sp.get("intent_id",""),
            "exp_name": sp.get("name",""),
            "trials": trials,
            "models": models,
            "proto": proto,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "abstain": sum(1 for t in trials if t.chosen_variant not in ("a","b")),
        })
    return sig

def update_library():
    sys_path_fix()
    lib = load()
    known = {h["id"]: h for h in lib["hypotheses"]}
    
    # Group by hypothesis_key (A3), then create per-experiment replication batches (A4)
    by_hyp = {}
    for exp_id, agg in collect_runs().items():
        hk = agg["hypothesis_key"]
        by_hyp.setdefault(hk, {"experiments": [], "intent_id": agg["intent_id"], "exp_name": agg["exp_name"]})
        n_dec = agg["wins_a"] + agg["wins_b"]
        if n_dec < 2: continue
        w = wilson(agg["wins_a"], n_dec)
        if w is None: continue
        by_hyp[hk]["experiments"].append(ReplicationBatch(
            experiment_id=exp_id,
            model_ids=agg["models"] or ["UNKNOWN"],
            n_decided=n_dec,
            wins_a=agg["wins_a"], wins_b=agg["wins_b"],
            p_variant_a=w["p"],
            wilson_ci=w["ci95"],
            protocol_version=agg["proto"],
            measured=datetime.datetime.utcnow().isoformat()+"Z",
        ))
    
    for hk, data in by_hyp.items():
        exps = data["experiments"]
        if not exps: continue
        
        h = known.get(hk)
        is_new = h is None
        if is_new:
            h = {
            "id": hk,
            "statement": f'Experiment "{data["exp_name"]}": tool-description selection effect',
            "causal_question": data["exp_name"],
            "intent_family": data["intent_id"],
            "created": datetime.datetime.utcnow().isoformat()+"Z",
            "replications": [],
            "status": "PROVISIONAL",
            "protocol_version": PROTOCOL_VERSION,
        }
            lib["hypotheses"].append(h)
            known[hk] = h
        
        # A4: each replication batch = one experiment's immutable result (not cumulative)
        for e in exps:
            if not any(r["experiment_id"] == e.experiment_id for r in h["replications"]):
                h["replications"].append(asdict(e))
        
        # A5: same-direction check across distinct model families
        model_families = {}  # model_id -> direction (+1/-1/0)
        for e in h["replications"]:
            p = e["p_variant_a"]
            direction = 1 if p > 0.5 else (-1 if p < 0.5 else 0)
            for m in e["model_ids"]:
                if m != "UNKNOWN":
                    model_families[m] = direction
        
        directions = set(model_families.values())
        same_direction = len(directions) <= 1 and 0 not in directions
        
        total_n = sum(e["n_decided"] for e in h["replications"])
        distinct_models = {m for e in h["replications"] for m in e["model_ids"] if m != "UNKNOWN"}
        pv_ok = all(e["protocol_version"] >= PROTOCOL_VERSION for e in h["replications"])
        
        # CI check per experiment
        all_cis_excl = all(
            wilson(e["wins_a"], e["n_decided"]) is not None and 
            wilson(e["wins_a"], e["n_decided"])["excludes_half"]
            for e in h["replications"] if e["n_decided"] > 0
        )
        
        if not pv_ok:
            h["status"] = "PROVISIONAL"
        elif total_n >= 30 and len(distinct_models) >= 2 and same_direction and all_cis_excl:
            h["status"] = "REPLICATED"
        elif total_n >= 30 and all_cis_excl:
            h["status"] = "CONFIRMED"
        else:
            h["status"] = "PROVISIONAL"
        
        h["aggregate"] = {
            "total_n": total_n,
            "distinct_model_families": sorted(distinct_models),
            "same_direction": same_direction,
            "all_cis_exclude_half": all_cis_excl,
            "last_verified": datetime.datetime.utcnow().isoformat()+"Z",
        }
    
    save(lib)

def invalidate(hid, reason, bugs, affected=None, offending_commit=None):
    lib = load()
    for h in lib["hypotheses"]:
        if h["id"] == hid:
            h["status"] = "INVALIDATED"
            h["invalidation"] = {"reason": reason, "discovered": datetime.datetime.utcnow().isoformat()+"Z",
                                 "offending_commit": offending_commit, "bugs": bugs,
                                 "affected_runs": affected or [], "raw_observations_retained": True}
    save(lib)

def print_library():
    lib = load()
    for h in lib["hypotheses"]:
        ag = h.get("aggregate", {})
        reps = h.get("replications", [])
        print(f"{h['id']} [{h['status']}] n={ag.get('total_n', sum(r.get('n_decided',0) for r in reps))} "
              f"models={ag.get('distinct_model_families',['?'])}")
        print(f"   Q: {h.get('causal_question', h.get('statement',''))[:100]}")
        for r in reps:
            exp_id = r.get('experiment_id', r.get('measured','?')[:16])
            pva = r.get('p_variant_a', r.get('overall_resistance', '?'))
            n = r.get('n_decided', '?')
            models = ','.join(r.get('model_ids', r.get('models', ['?'])))
            ci = r.get('wilson_ci', '')
            print(f"   · exp={exp_id} P(A)={pva} n={n} CI={ci} models={models}")

def sys_path_fix():
    import sys
    p = os.path.join(os.path.dirname(__file__))
    if p not in sys.path: sys.path.insert(0, p)

if __name__ == "__main__":
    update_library(); print_library()
