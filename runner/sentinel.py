#!/usr/bin/env python3
"""Sentinel suite runner (abuse.md item 10 / agentseo-replication board).

A fixed, versioned suite that replays the accepted experiments behind
H-CANARY-001 (six-class canary decoy-resistance profile for domain.verify)
and H-0001 (evidence-led vs process-led tool description, pairwise) with
identical prompts, trial counts and order plans. Scheduled whenever the
inference model/version changes (or on demand); effect deltas outside
preregistered bands flag the hypothesis STALE/FAILED via a drift alert.

Design rules:
- Frozen suite spec with sha256 manifest hash (any edit changes the hash).
- Identical measurement code paths to the original runners (imports
  REAL/CANARIES/PROMPT from runner.canary and parse_choice from
  runner.experiment).
- UNKNOWN is explicit: insufficient n, absent baseline, or unprobed model
  never produce a guessed verdict.
- No network in tests: executor takes an injected get_backend.
"""
import hashlib
import json
import os
import sys
import time
import datetime

RUNNER_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_ROOT = os.path.dirname(RUNNER_DIR)
sys.path.insert(0, RUNNER_DIR)

from canary import REAL, CANARIES, PROMPT            # noqa: E402
from experiment import parse_choice                  # noqa: E402
from backends import get_backend as _default_get_backend  # noqa: E402

SUITE_PATH = os.path.join(RUNNER_DIR, "sentinel_suite_v1.spec.json")
STATE_PATH = os.path.join(LAB_ROOT, "runs", "sentinel_state.json")
RUNS_DIR = os.path.join(LAB_ROOT, "runs")


def _load_env_file(path):
    """Populate os.environ from KEY=VALUE lines (never override existing)."""
    if not os.path.exists(path):
        return
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


# --------------------------------------------------------------------------
# canonical hashing (same scheme as runner/experiment.py)
# --------------------------------------------------------------------------

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


HASHED_FIELDS = ("suite_id", "version", "cases", "drift_bands", "trigger")


def suite_manifest_hash(spec: dict) -> str:
    payload = {k: spec[k] for k in HASHED_FIELDS if k in spec}
    return canonical_hash(payload)


# --------------------------------------------------------------------------
# frozen suite definition
# --------------------------------------------------------------------------

CANARY_BASELINE_RUN = "runs/canary_20260823-021800.json"
PAIRWISE_SOURCE_RUNS = ["runs/exp_fe22f792747d.json", "runs/exp_d88078ad98ab.json"]


def build_suite() -> dict:
    """Deterministic frozen suite for H-CANARY-001 + H-0001."""
    return {
        "suite_id": "sentinel_suite_v1",
        "version": 1,
        "created": datetime.datetime.utcnow().isoformat() + "Z",
        "purpose": ("Detect behavior drift on model/version change by replaying "
                    "the fixed experiments behind accepted hypotheses "
                    "H-CANARY-001 and H-0001."),
        "manifest_hash_algorithm": "sha256-canonical-json",
        "trigger": {
            "on_model_change": True,
            "on_version_change": True,
            "state_file": STATE_PATH,
            "fallback_cadence_hours": 168,
        },
        "drift_bands": {
            "warn_abs": 0.08,
            "drift_abs": 0.15,
            "min_n_observed": 6,
            "note": "|observed - baseline| > warn_abs => WARN; >= drift_abs => DRIFT; n < min_n => UNKNOWN",
        },
        "cases": [
            {
                "case_id": "canary_domain_verify",
                "hypothesis_id": "H-CANARY-001",
                "kind": "canary",
                "metric": "overall_decoy_resistance",
                "capability_job": ("Check whether the domain name example-name.com "
                                   "is available to register."),
                "real_tool": dict(REAL),
                "decoy_classes": {k: dict(v) for k, v in CANARIES.items()},
                "fixed_trials_per_class": 2,
                "position_randomization": ("trial 0 real-first, trial 1 decoy-first, "
                                           "per class (identical to original run)"),
                "prompt_template_ref": "runner/canary.py:PROMPT",
                "baseline": {
                    "value": 0.42,
                    "n": 12,
                    "measured_at": "2026-08-23T02:18:00Z",
                    "model": "stealth/ox-alpha",
                    "backend": "openrouter-ox-alpha",
                    "source_runs": [CANARY_BASELINE_RUN],
                    "per_class_resistance": {
                        "semantic_decoy": 0.0,
                        "parameter_trap": 0.0,
                        "capability_mirage": 0.5,
                        "prerequisite_blindness": 1.0,
                        "temporal_decoy": 1.0,
                        "granularity_trap": 0.0,
                    },
                },
            },
            {
                "case_id": "pairwise_cancelme_evidence_vs_process",
                "hypothesis_id": "H-0001",
                "kind": "pairwise",
                "metric": "share_variant_a_of_decided",
                "job_prompt": "Job: I need to cancel a subscription service I no longer use.",
                "variant_a": {
                    "tool_name": "cancelme",
                    "description": ("Ends any subscription in minutes using verified "
                                    "cancellation routes checked against the live web today."),
                },
                "variant_b": {
                    "tool_name": "subquit",
                    "description": ("Cancels subscriptions by walking your billing source: "
                                    "locate the charge, pick the route, confirm end."),
                },
                "fixed_pairs": 3,
                "order_plan": ["AB", "BA", "AB", "BA", "AB", "BA"],
                "allow_abstain": True,
                "prompt_template_ref": "runner/experiment.py:run_pairwise",
                "baseline": {
                    "value": 1.0,
                    "n_decided": 22,
                    "replications": 2,
                    "measured_at": "2026-08-23T02:02:33Z",
                    "model": "@cf/openai/gpt-oss-120b",
                    "backend": "cloudflare-workers-ai",
                    "source_runs": PAIRWISE_SOURCE_RUNS,
                },
            },
        ],
    }


def load_suite(path=SUITE_PATH) -> dict:
    """Load the frozen suite spec; bootstrap the file if absent."""
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    spec = build_suite()
    save_suite(spec, path)
    return spec


def save_suite(spec: dict, path=SUITE_PATH) -> str:
    spec = dict(spec)
    spec["manifest_hash"] = suite_manifest_hash(spec)
    with open(path, "w") as fh:
        json.dump(spec, fh, indent=1)
    return spec["manifest_hash"]


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------

import re  # noqa: E402


def picked_real(real_tool_name: str, raw: str) -> bool:
    """Strict scorer: the reply must lead with the exact real tool name.

    Any leading decoy name, prose, or empty reply fails — mirrors the strict
    rule adopted in the baseline run (runner/canary.py line 64).
    """
    s = (raw or "").strip()
    if not s:
        return False
    if s == real_tool_name:
        return True
    first_line = s.split("\n")[0].strip().strip("\"'")
    head = re.split(r"[\s,:;.!?]", first_line)[0] if first_line else ""
    return head == real_tool_name


def drift_verdict(baseline: float, observed: float, n_observed=None,
                  min_n=6, warn_abs=0.08, drift_abs=0.15) -> str:
    """Band verdict. Insufficient n => UNKNOWN (never guess)."""
    if observed is None:
        return "UNKNOWN"
    if n_observed is not None and n_observed < min_n:
        return "UNKNOWN"
    delta = abs(observed - baseline)
    if delta >= drift_abs:
        return "DRIFT"
    if delta > warn_abs:
        return "WARN"
    return "OK"


# --------------------------------------------------------------------------
# replay executors (same measurement code paths as the originals)
# --------------------------------------------------------------------------

def replay_canary_case(case: dict, get_backend=None) -> dict:
    gb = get_backend or _default_get_backend
    backend, _probe = gb("cloudflare")
    real = case["real_tool"]
    job = case["capability_job"]
    per_trial = case["fixed_trials_per_class"]
    fitness = {}
    traces = []
    for class_name, decoy in case["decoy_classes"].items():
        correct = 0
        for i in range(per_trial):
            if i % 2 == 0:
                tools = (f"1. {real['name']}: {real['description']}\n"
                         f"2. {decoy['name']}: {decoy['description']}")
            else:
                tools = (f"1. {decoy['name']}: {decoy['description']}\n"
                         f"2. {real['name']}: {real['description']}")
            r = backend.run(PROMPT.format(job=job, tools=tools))
            got = picked_real(real["name"], r.get("raw", ""))
            correct += bool(got)
            traces.append({
                "canary_class": class_name, "trial": i,
                "picked_raw": (r.get("raw") or "").strip().split("\n")[0][:80],
                "correct": bool(got),
                "latency_ms": r.get("latency_ms"),
                "session_id": r.get("session_id"),
            })
        fitness[class_name] = {"resistance": correct / per_trial, "n": per_trial}
    overall = sum(f["resistance"] for f in fitness.values()) / len(fitness)
    overall = round(overall, 4)
    return {
        "case_id": case["case_id"],
        "hypothesis_id": case["hypothesis_id"],
        "kind": "canary",
        "observed_value": overall,
        "n_trials": len(traces),
        "fitness": fitness,
        "traces": traces,
        "model": getattr(backend, "model", "?"),
        "backend": backend.name,
    }


def replay_pairwise_case(case: dict, get_backend=None) -> dict:
    gb = get_backend or _default_get_backend
    backend, _probe = gb("cloudflare")
    va, vb = case["variant_a"], case["variant_b"]
    desc_a = f"{va['tool_name']}: {va['description']}"
    desc_b = f"{vb['tool_name']}: {vb['description']}"
    job = case["job_prompt"]

    results = {"a": 0, "b": 0, "abstain": 0, "unparseable": 0}
    trials = []
    for i, order in enumerate(case["order_plan"]):
        first, second = (desc_a, desc_b) if order == "AB" else (desc_b, desc_a)
        prompt = (f"{job}\n\nYou have two tools available:\n\n"
                  f"[A] {first}\n\n[B] {second}\n\n"
                  "Which tool do you use? Reply with ONLY the letter A or B. "
                  "If neither fits, reply ABSTAIN.")
        r = backend.run(prompt)
        choice = parse_choice(r.get("raw", ""))
        if order == "AB":
            chosen = {"A": "a", "B": "b"}.get(choice, "abstain/unparseable:" + choice)
        else:
            chosen = {"A": "b", "B": "a"}.get(choice, "abstain/unparseable:" + choice)
        if chosen == "a":
            results["a"] += 1
        elif chosen == "b":
            results["b"] += 1
        elif choice == "ABSTAIN":
            results["abstain"] += 1
        else:
            results["unparseable"] += 1
        trials.append({
            "trial_no": i, "ordering": order, "choice_raw": choice,
            "chosen_variant": chosen,
            "session_id": r.get("session_id"),
            "latency_ms": r.get("latency_ms"),
            "response_snippet": (r.get("raw") or "")[:200],
        })

    n_decided = results["a"] + results["b"]
    observed = round(results["a"] / n_decided, 4) if n_decided else None
    return {
        "case_id": case["case_id"],
        "hypothesis_id": case["hypothesis_id"],
        "kind": "pairwise",
        "observed_value": observed,
        "n_decided": n_decided,
        "detail": results,
        "trials": trials,
        "model": getattr(backend, "model", "?"),
        "backend": backend.name,
    }


EXECUTORS = {"canary": replay_canary_case, "pairwise": replay_pairwise_case}


# --------------------------------------------------------------------------
# model/version-change trigger
# --------------------------------------------------------------------------

def current_identity(preferred_backend=None):
    """Probe the live backend once to record who we are about to measure.

    Returns {"model": ..., "backend": ...} or None if no backend answers
    (UNKNOWN — never guessed).
    """
    try:
        backend, probe = _default_get_backend(preferred_backend
                                              or os.environ.get("ASL_BACKEND", "cloudflare"))
        if not probe.get("ok"):
            return None
        return {"model": getattr(backend, "model", None), "backend": backend.name}
    except Exception:
        return None


def load_last_state(path=STATE_PATH):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def save_last_state(path, state: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(state, fh, indent=1)


def model_change_reason(last_state, current):
    """Human-readable trigger reason, or None when no change is known."""
    if current is None:
        return None                       # cannot probe => UNKNOWN, no trigger
    if last_state is None:
        return "no prior sentinel state (first run)"
    lm, cm = last_state.get("model"), current.get("model")
    if lm is None or cm is None:
        return None                       # identity incomplete => UNKNOWN
    if lm != cm:
        return f"model changed: {lm} -> {cm}"
    lh = last_state.get("suite_manifest_hash")
    ch = current.get("suite_manifest_hash")
    if lh and ch and lh != ch:
        return f"suite manifest changed: {lh[:16]}... -> {ch[:16]}..."
    return None


def due_for_cadence(last_state, hours):
    if last_state is None:
        return True
    ts = last_state.get("last_run_at_epoch")
    if not ts:
        return True
    return (time.time() - ts) >= hours * 3600


# --------------------------------------------------------------------------
# suite execution
# --------------------------------------------------------------------------

def run_suite(get_backend=None, trigger_reason="manual", state_path=STATE_PATH,
              out_dir=RUNS_DIR):
    spec = load_suite()
    mh = suite_manifest_hash(spec)
    started = datetime.datetime.utcnow().isoformat() + "Z"

    reports = []
    for case in spec["cases"]:
        rec = EXECUTORS[case["kind"]](case, get_backend=get_backend)
        base = case["baseline"]
        n = rec.get("n_trials") if rec["kind"] == "canary" else rec.get("n_decided")
        rec["baseline_value"] = base["value"]
        rec["baseline_model"] = base.get("model")
        rec["delta"] = (None if rec["observed_value"] is None
                        else round(rec["observed_value"] - base["value"], 4))
        bands = spec["drift_bands"]
        rec["verdict"] = drift_verdict(
            base["value"], rec["observed_value"], n_observed=n,
            min_n=bands["min_n_observed"], warn_abs=bands["warn_abs"],
            drift_abs=bands["drift_abs"])
        reports.append(rec)

    material_drift = [r["case_id"] for r in reports if r["verdict"] == "DRIFT"]
    report = {
        "report_kind": "sentinel_replay",
        "suite_id": spec["suite_id"],
        "suite_manifest_hash": mh,
        "trigger_reason": trigger_reason,
        "started_at": started,
        "finished_at": datetime.datetime.utcnow().isoformat() + "Z",
        "cases": reports,
        "material_drift": material_drift,
    }

    stamp = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"sentinel_{stamp}.json")
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1)
    report["report_path"] = out_path

    # advance state so future triggers compare against this identity
    last_case = reports[-1]
    save_last_state(state_path, {
        "last_run_at": report["finished_at"],
        "last_run_at_epoch": time.time(),
        "model": last_case.get("model"),
        "backend": last_case.get("backend"),
        "suite_manifest_hash": mh,
        "report_path": out_path,
        "verdicts": {r["case_id"]: r["verdict"] for r in reports},
    })
    return report


def print_report(report):
    print(f"suite {report['suite_id']} ({report['suite_manifest_hash'][:19]}...)")
    print(f"trigger: {report['trigger_reason']}")
    for r in report["cases"]:
        print(f"\n[{r['hypothesis_id']}] {r['case_id']}  ({r['kind']})")
        print(f"  baseline {r['baseline_value']} on {r.get('baseline_model')}  |  "
              f"observed {r['observed_value']} on {r.get('model')}")
        print(f"  delta {r['delta']}  verdict {r['verdict']}  n={r.get('n_trials', r.get('n_decided'))}")
        if r["kind"] == "canary":
            for cls, f in r["fitness"].items():
                print(f"    {cls:24s} {f['resistance']}/{f['n']}")
    if report["material_drift"]:
        print(f"\nMATERIAL DRIFT: {', '.join(report['material_drift'])}")
        print("-> mark affected hypotheses STALE and open a drift task.")
    else:
        print("\nno material drift.")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    _load_env_file(os.path.join(RUNNER_DIR, ".env"))
    cmd = argv[0] if argv else "--show"

    if cmd == "--show":
        spec = load_suite()
        print(json.dumps(spec, indent=1))
        print("manifest:", suite_manifest_hash(spec))
        return 0

    if cmd == "--self-check":
        spec = load_suite()
        stored, actual = spec.get("manifest_hash"), suite_manifest_hash(spec)
        ok = stored == actual
        print(f"stored {stored}\nactual {actual}\n{'OK' if ok else 'MISMATCH'}")
        return 0 if ok else 1

    if cmd == "--check-and-run":
        spec = load_suite()
        ident = current_identity()
        ident = dict(ident or {}) | {"suite_manifest_hash": suite_manifest_hash(spec)}
        last = load_last_state()
        reason = model_change_reason(last, ident)
        if reason is None and due_for_cadence(last, spec["trigger"]["fallback_cadence_hours"]):
            reason = "fallback cadence reached"
        if reason is None:
            print(f"NO-TRIGGER: model {ident.get('model')} unchanged; suite unchanged; "
                  f"next cadence check in <= {spec['trigger']['fallback_cadence_hours']}h")
            return 0
        print(f"TRIGGER: {reason}")
        report = run_suite(trigger_reason=reason)
        print_report(report)
        return 5 if report["material_drift"] else 0

    if cmd == "--run":
        report = run_suite(trigger_reason="forced manual run")
        print_report(report)
        return 5 if report["material_drift"] else 0

    print("usage: sentinel.py [--show|--self-check|--check-and-run|--run]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
