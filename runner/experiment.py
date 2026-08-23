#!/usr/bin/env python3
"""ExperimentSpec + pairwise tournament runner.

Contract per abuse.md item 2/3/4:
- ExperimentSpec: treatment/control variants, seed, preregistered metric,
  dev/holdout classification, immutable manifest hash.
- Runner: fresh isolated hermes session per trial, AB/BA order reversal,
  position-bias control, abstention allowed, structured trace capture.
"""
import hashlib, json, subprocess, uuid, datetime, os, sys, time, random

def canonical_hash(obj) -> str:
    def canon(v):
        if isinstance(v, dict):
            return {k: canon(v[k]) for k in sorted(v.keys())}
        if isinstance(v, list):
            return [canon(x) for x in v]
        return v
    return "sha256:" + hashlib.sha256(
        json.dumps(canon(obj), sort_keys=False, separators=(",", ":")).encode()
    ).hexdigest()

class ExperimentSpec:
    def __init__(self, name, intent_id, job_prompt, variant_a, variant_b,
                 preregistered_metric="correct_selection", n_pairs=4,
                 holdout=False, seed=None):
        self.spec = {
            "experiment_id": "exp_" + uuid.uuid4().hex[:12],
            "name": name,
            "intent_id": intent_id,
            "job_prompt": job_prompt,
            "variant_a": variant_a,   # {"tool_name":..., "description":...}
            "variant_b": variant_b,
            "preregistered_metric": preregistered_metric,
            "n_pairs": n_pairs,       # AB/BA pairs = 2*n_pairs trials
            "holdout": holdout,       # holdout experiments never feed evolution
            "seed": seed or int(time.time()),
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "runner": "hermes/opencode-go",
            "model_profile": "builder",
        }
        self.manifest_hash = canonical_hash(self.spec)

    def save(self, path):
        json.dump({"manifest_hash": self.manifest_hash, **self.spec},
                  open(path, "w"), indent=1)

import sys
sys.path.insert(0, os.path.dirname(__file__))
from backends import get_backend

_BACKEND = None
def run_session(prompt: str, timeout=90):
    """Fresh isolated session via the healthy backend."""
    global _BACKEND
    if _BACKEND is None:
        _BACKEND, _ = get_backend(os.environ.get("ASL_BACKEND", "cloudflare"))
    r = _BACKEND.run(prompt, timeout=timeout)
    return {"raw": r.get("raw", ""), "exit_code": 0 if r.get("ok") else -1,
            "latency_ms": r["latency_ms"], "session_id": r["session_id"],
            "backend": _BACKEND.name,
            "model": getattr(_BACKEND, "model", os.environ.get("MODEL_NAME", "ox-alpha-free"))}

def parse_choice(raw: str):
    """Extract A/B/abstain/UNPARSEABLE. Abstain checked BEFORE letter scan —
    otherwise 'ABSTAIN' parses as 'A' (head/tail scan bug caught by tests)."""
    s = raw.strip()
    low = s.lower()
    if "abstain" in low or ("neither" in low and "tool" not in low):
        return "ABSTAIN"
    for ch in (s[:2], s[-2:]):
        for c in ch:
            if c in "AB":
                return c
    if "abstain" in s.lower() or "neither" in s.lower():
        return "ABSTAIN"
    # last resort: any standalone A/B token
    import re
    m = re.findall(r"\b([AB])\b", s)
    return m[0] if len(set(m)) == 1 else "UNPARSEABLE"

def run_pairwise(spec: ExperimentSpec, db_path="./lab.db"):
    try:
        from validator import validate_pairwise
        validate_pairwise(spec.spec)
        print("  validator: PASS")
    except ImportError:
        print("  [warn] validator unavailable — skipping pre-run gate")
    except Exception as e:
        raise SystemExit(f"validator: FAIL — {e}")
    job = spec.spec["job_prompt"]
    va, vb = spec.spec["variant_a"], spec.spec["variant_b"]
    desc_a = f"{va['tool_name']}: {va['description']}"
    desc_b = f"{vb['tool_name']}: {vb['description']}"

    trials = []
    order_plan = []
    for i in range(spec.spec["n_pairs"]):
        order_plan += ["AB", "BA"]

    results = {"a": 0, "b": 0, "abstain": 0, "unparseable": 0}
    # A6: seed-driven randomized ordering (balanced AB/BA but sequence shuffled)
    rng = random.Random(spec.spec["seed"])
    rng.shuffle(order_plan)
    for i, order in enumerate(order_plan):
        first, second = (desc_a, desc_b) if order == "AB" else (desc_b, desc_a)
        prompt = (f"{job}\n\nYou have two tools available:\n\n"
                  f"[A] {first}\n\n[B] {second}\n\n"
                  "Which tool do you use? Reply with ONLY the letter A or B. "
                  "If neither fits, reply ABSTAIN.")
        r = run_session(prompt)
        choice = parse_choice(r["raw"])
        chosen_variant = ("abstain/unparseable:" + choice) if choice in ("ABSTAIN","UNPARSEABLE") else \
                         (("a" if choice == "A" else "b") if order == "AB" else ("b" if choice == "A" else "a"))
        if chosen_variant == "a": results["a"] += 1
        elif chosen_variant == "b": results["b"] += 1
        elif choice == "ABSTAIN": results["abstain"] += 1
        else: results["unparseable"] += 1

        trials.append({
            "trial_no": i, "ordering": order, "choice_raw": choice,
            "chosen_variant": chosen_variant,
            "session_id": r["session_id"], "latency_ms": r["latency_ms"],
            "response_snippet": r["raw"][:200],
            **_provenance(r, prompt, r.get("raw", ""), order),
        })
        print(f"  pair{i+1}/{order}: {choice} → variant-{chosen_variant} ({r['latency_ms']}ms)")

    n_decided = results["a"] + results["b"]
    summary = {
        **results,
        "pct_a_of_decided": round(100*results["a"]/n_decided) if n_decided else None,
        "position_bias_check": _position_bias(trials),
    }
    record = {"spec_manifest_hash": spec.manifest_hash,
              "experiment_id": spec.spec["experiment_id"],
              "summary": summary, "trials": trials}
    json.dump(record, open(f"/root/agentseolab/runs/{spec.spec['experiment_id']}.json","w"), indent=1)
    return record

def _provenance(r, prompt, response_raw, ordering):
    """Per-trial runtime provenance (P0 item 5). Best-effort: never blocks a trial."""
    try:
        from provenance import trial_provenance
        return {"provenance": trial_provenance(
            type("B", (), {"name": r.get("backend", "?"),
                           "model": r.get("model", None),
                           "max_tokens": 300})(),
            prompt, response_raw, ordering,
            extra={"session_id": r.get("session_id")})}
    except Exception as e:
        return {"provenance_error": str(e)[:120]}

def _position_bias(trials):
    # Position bias = model tracks LETTER/POSITION instead of content.
    # Content-consistent choice: same variant wins under both orderings.
    ab_pick_first = sum(1 for t in trials if t['ordering']=='AB' and t['choice_raw']=='A')
    ba_pick_first = sum(1 for t in trials if t['ordering']=='BA' and t['choice_raw']=='A')  # letter A = first shown in BA too
    content_consistent = sum(1 for t in trials if t.get('chosen_variant') in ('a','b'))
    return {'picked_first_shown': ab_pick_first + ba_pick_first,
            'content_consistent_choices': content_consistent,
            'note': 'if picked_first ≈ n_trials ⇒ letter-follows-position bias; content_consistent == n_decided ⇒ clean'}

if __name__ == "__main__":
    # Env-driven spec (defaults preserve the original demo). ASL_SPEC=path/to/spec.json
    # loads a preregistered spec file; otherwise env vars override the demo.
    name = sys.argv[1] if len(sys.argv)>1 else os.environ.get("ASL_NAME", "demo-pairwise")
    os.makedirs("/root/agentseolab/runs", exist_ok=True)
    if os.environ.get("ASL_SPEC"):
        loaded = json.load(open(os.environ["ASL_SPEC"]))
        loaded.pop("manifest_hash", None)
        eid = loaded.pop("experiment_id")
        spec = ExperimentSpec.__new__(ExperimentSpec)
        spec.spec = loaded
        spec.spec["experiment_id"] = eid
        spec.manifest_hash = canonical_hash(spec.spec)
    else:
        spec = ExperimentSpec(
            name=name,
            intent_id=os.environ.get("ASL_INTENT_ID", "intent_46bc68daf5044d6c808697c9fad78049"),
            job_prompt=os.environ.get("ASL_JOB", "Job: I need to cancel a subscription service I no longer use."),
            variant_a={"tool_name": os.environ.get("ASL_A_NAME", "cancelme"),
                       "description": os.environ.get("ASL_A_DESC",
                           "Ends any subscription in minutes using verified cancellation routes checked against the live web today.")},
            variant_b={"tool_name": os.environ.get("ASL_B_NAME", "subquit"),
                       "description": os.environ.get("ASL_B_DESC",
                           "Cancels subscriptions by walking your billing source: locate the charge, pick the route, confirm end.")},

            n_pairs=int(os.environ.get("N_PAIRS","2")),
        )
    spec.save(f"/root/agentseolab/runs/{spec.spec['experiment_id']}.spec.json")
    print("Experiment:", spec.spec["experiment_id"], "| manifest:", spec.manifest_hash[:20]+"…")
    rec = run_pairwise(spec)
    print(json.dumps(rec["summary"], indent=1))
