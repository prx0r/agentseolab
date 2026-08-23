#!/usr/bin/env python3
"""Evidence library (abuse.md item 9): auto-record confirmed experiments
as hypothesis records with effect size, replication count, model families,
and STALE/FAILED lifecycle. Failures are retained forever."""
import json, glob, sqlite3, hashlib, datetime, os

DB = "/root/agentseolab/lab.db"
LIB = "/root/agentseolab/evidence_library.json"

def load():
    if os.path.exists(LIB):
        return json.load(open(LIB))
    return {"hypotheses": []}

def save(lib):
    json.dump(lib, open(LIB, "w"), indent=1)

def collect_runs(min_n=4, min_pct=80):
    """Group runs by (variant_a_desc, variant_b_desc) signature → aggregated effect."""
    sig_runs = {}
    for f in sorted(glob.glob("/root/agentseolab/runs/exp_*.json")):
        if ".spec." in f: continue
        d = json.load(open(f))
        s = d["summary"]
        a, b = s.get("a",0), s.get("b",0)
        n = a + b
        if n < min_n: continue
        spec_file = f.replace(".json", ".spec.json")
        va = vb = "?"
        if os.path.exists(spec_file):
            sp = json.load(open(spec_file))
            va = sp["variant_a"]["description"][:60]
            vb = sp["variant_b"]["description"][:60]
        key = hashlib.sha256((va+"||"+vb).encode()).hexdigest()[:10]
        sig_runs.setdefault(key, {
            "signature": {"variant_a": va, "variant_b": vb},
            "runs": [], "total_a": 0, "total_b": 0, "models": set()})
        sig_runs[key]["runs"].append({"experiment_id": d["experiment_id"], "a": a, "b": b,
                                      "model": _model_of(d)})
        sig_runs[key]["total_a"] += a; sig_runs[key]["total_b"] += b
        sig_runs[key]["models"].add(_model_of(d))
    return sig_runs

def _model_of(d):
    for t in d.get("trials", []):
        return t.get("session_id","")[:3]
    return "?"

def update_library():
    lib = load()
    known = {h["id"]: h for h in lib["hypotheses"]}
    for key, agg in collect_runs().items():
        n = agg["total_a"] + agg["total_b"]
        p = agg["total_a"] / n if n else 0.5
        hid = "H-" + key[:8].upper()
        h = known.setdefault(hid, {
            "id": hid,
            "statement": f'Tool description "{agg["signature"]["variant_a"]}" is selected over "{agg["signature"]["variant_b"]}" by autonomous agents.',
            "created": datetime.datetime.utcnow().isoformat()+"Z",
            "replications": [],
            "status": "PROVISIONAL",
        })
        rep = {"measured": datetime.datetime.utcnow().isoformat()+"Z",
               "p_variant_a": round(p,3), "n_decided": n,
               "models": sorted(agg["models"]),
               "effect_pp": round((p-0.5)*200, 1)}
        # upsert replication by models-set
        if not any(r.get("models") == rep["models"] and r.get("p_variant_a") == rep["p_variant_a"]
                   for r in h["replications"]):
            h["replications"].append(rep)
        # status ladder
        distinct_models = len({tuple(sorted(r["models"])) for r in h["replications"]})
        total_n = sum(r["n_decided"] for r in h["replications"])
        if distinct_models >= 2 and total_n >= 20:
            h["status"] = "REPLICATED"
        elif total_n >= 12:
            h["status"] = "CONFIRMED_SINGLE_MODEL"
        else:
            h["status"] = "PROVISIONAL"
        h["aggregate"] = {"n_decided": total_n,
                          "distinct_model_backends": distinct_models,
                          "last_verified": datetime.datetime.utcnow().isoformat()+"Z"}
    save(lib)

def mark_stale(hid, note=""):
    lib = load()
    for h in lib["hypotheses"]:
        if h["id"] == hid:
            h["status"] = "STALE"
            h["stale_note"] = note or datetime.datetime.utcnow().isoformat()
    save(lib)

def print_library():
    lib = load()
    for h in lib["hypotheses"]:
        ag = h.get("aggregate", {})
        print(f"{h['id']} [{h['status']}] n={ag.get('n_decided',0)} "
              f"backends={ag.get('distinct_model_backends',0)}")
        print(f"   {h['statement']}")
        for r in h["replications"]:
            print(f"   · {r['measured'][:16]} P(A)={r['p_variant_a']} n={r['n_decided']} models={','.join(r['models'])}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--stale":
        mark_stale(sys.argv[2], " ".join(sys.argv[3:]) or "manual")
    update_library()
    print_library()
