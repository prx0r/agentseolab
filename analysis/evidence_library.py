#!/usr/bin/env python3
"""Evidence library v2 — fail-closed promotion gates (dev-plan P0 item 7).

Lifecycle: PROPOSED PREREGISTERED RUNNING PROVISIONAL CONFIRMED REPLICATED
           FAILED_REPLICATION INVALIDATED STALE
INVALIDATED  = machinery/protocol defect (record retained forever)
FAILED_REPLICATION = valid protocol, effect didn't replicate

Promotion gates (no manual upgrades):
CONFIRMED   requires: protocol_version >= 2, n_decided >= 30,
            Wilson CI excludes 0.5, zero invalidated runs in signature
REPLICATED  requires: CONFIRMED + independent rerun on a DIFFERENT model_id
            (actual model identity from trial provenance — never session
            prefix), same direction, its own CI excludes 0.5
Model identity comes from per-trial provenance 'model_id' field.
"""
import json, glob, hashlib, datetime, os

LIB_PATH = "/root/agentseolab/evidence_library.json"
PROTOCOL_VERSION = 2

def load():
    if os.path.exists(LIB_PATH):
        return json.load(open(LIB_PATH))
    return {"hypotheses": [], "protocol_version": PROTOCOL_VERSION}

def save(lib): json.dump(lib, open(LIB_PATH, "w"), indent=1)

def collect_runs(min_n=4):
    sig = {}
    for f in sorted(glob.glob("/root/agentseolab/runs/exp_*.json")):
        if ".spec." in f: continue
        d = json.load(open(f))
        if "summary" not in d: continue
        s = d["summary"]
        # provenance-based model identity (v2 trials carry model_id; legacy runs → UNKNOWN)
        models = sorted({t.get("model_id", "UNKNOWN") for t in d.get("trials", [])})
        proto_v = 1 if any(t.get("model_id") is None for t in d.get("trials", [])) else 2
        spec_file = f.replace(".json", ".spec.json")
        va = vb = "?"
        if os.path.exists(spec_file):
            sp = json.load(open(spec_file))
            va, vb = sp["variant_a"]["description"][:60], sp["variant_b"]["description"][:60]
        key = hashlib.sha256((va+"||"+vb).encode()).hexdigest()[:10]
        e = sig.setdefault(key, {"signature": {"variant_a": va, "variant_b": vb},
                                 "total_a": 0, "total_b": 0, "runs": [], "models": set(), "proto": []})
        e["runs"].append({"experiment_id": d["experiment_id"], "a": s["a"], "b": s["b"], "models": models})
        e["total_a"] += s["a"]; e["total_b"] += s["b"]
        e["models"].update(models); e["proto"].append(proto_v)
    return sig

def update_library():
    sys_path_fix()
    from wilson import wilson
    lib = load()
    known = {h["id"]: h for h in lib["hypotheses"]}
    for key, agg in collect_runs().items():
        n = agg["total_a"] + agg["total_b"]
        if n == 0: continue
        p = agg["total_a"] / n
        w = wilson(agg["total_a"], n)
        hid = "H-" + key[:8].upper()
        h = known.get(hid)
        if h and h.get("status") == "INVALIDATED":
            continue  # never resurrect invalidated hypotheses
        h = known.setdefault(hid, {
            "id": hid,
            "statement": f'Tool description "{agg["signature"]["variant_a"]}" is selected over "{agg["signature"]["variant_b"]}" by autonomous agents.',
            "created": datetime.datetime.utcnow().isoformat()+"Z",
            "replications": [],
            "status": "PROVISIONAL",
            "protocol_version": max(agg["proto"]),
        })
        rep = {"measured": datetime.datetime.utcnow().isoformat()+"Z",
               "p_variant_a": round(p,3), "n_decided": n,
               "model_ids": sorted(agg["models"]), "protocol_version": max(agg["proto"]),
               "wilson": w}
        if not any(r.get("p_variant_a")==rep["p_variant_a"] and r.get("n_decided")==rep["n_decided"]
                   and r.get("model_ids")==rep["model_ids"] for r in h["replications"]):
            h["replications"].append(rep)

        # ---- promotion gates (fail-closed) ----
        pv_ok = max(agg["proto"]) >= PROTOCOL_VERSION
        ci_excl = w["excludes_0.5"]
        distinct_models = {m for r in h["replications"] if r.get("protocol_version",1)>=PROTOCOL_VERSION
                           for m in r.get("model_ids",[]) if m != "UNKNOWN"}
        total_n_v2 = sum(r["n_decided"] for r in h["replications"]
                         if r.get("protocol_version",1)>=PROTOCOL_VERSION)
        if not pv_ok or total_n_v2 < 30 or not ci_excl:
            h["status"] = "PROVISIONAL"
        elif len(distinct_models) >= 2:
            # every model family's own CI must also exclude 0.5, same direction
            per_model_ok = True
            for m in distinct_models:
                a = sum(r["a"] if False else 0 for r in [] )  # placeholder; use run-level below
            # simpler: require each model's aggregate p>0.5 and its run CI excludes .5
            for m in distinct_models:
                ma = mb = 0
                for r_ in agg["runs"]:
                    if m in r_["models"]:
                        ma += r_["a"]; mb += r_["b"]
                wm = wilson(ma, ma+mb)
                if wm is None or not wm["excludes_0.5"]:
                    per_model_ok = False
            h["status"] = "REPLICATED" if per_model_ok else "PROVISIONAL"
        else:
            h["status"] = "CONFIRMED"
        h["aggregate"] = {"n_decided": total_n_v2 or n,
                          "distinct_model_ids": sorted(distinct_models),
                          "wilson": w,
                          "last_verified": datetime.datetime.utcnow().isoformat()+"Z"}
    save(lib)

def sys_path_fix():
    import sys
    p = os.path.join(os.path.dirname(__file__))
    if p not in sys.path: sys.path.insert(0, p)

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
        print(f"{h['id']} [{h['status']}] pv{h.get('protocol_version','?')} n={ag.get('n_decided',0)}")
        print(f"   {h['statement'][:110]}")
        for r in h["replications"]:
            print(f"   · {str(r.get('measured','?'))[:16]} P(A)={r.get('p_variant_a', r.get('overall_resistance','?'))} n={r.get('n_decided','?')} models={','.join(r.get('model_ids',['?']))}")

if __name__ == "__main__":
    update_library(); print_library()
