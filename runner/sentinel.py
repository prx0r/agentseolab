#!/usr/bin/env python3
"""Sentinel suite runner (abuse.md item 10 / agentseo-replication board).

Fixed, versioned suite that replays accepted experiments with IDENTICAL
instruments, trial counts and order plans whenever the inference model or
suite version changes; effect deltas outside preregistered bands flag
material drift (STALE/FAILED candidates).

Design rules:
- Self-contained: instruments are embedded BY VALUE in the frozen spec.
  Runner modules mutate (see canary v1->v2); replaying with new instruments
  would measure instrumentation change, not model drift.
- UNKNOWN is explicit: insufficient n, unprobed identity, or an unadopted
  baseline never produce a guessed verdict.
- No network in tests: executors take an injected get_backend.

History note: H-CANARY-001's original 0.42 baseline was INVALIDATED
(CANARY_IMPLEMENTATION_DEFECT: backend passed as job prompt; parameter_trap
unscoreable when real and decoy shared a name). The suite therefore carries
the corrected canary-v2 instrument as candidate H-CANARY-002 with
NO_VALID_BASELINE until explicitly adopted via --adopt-baseline.
"""
import hashlib
import json
import os
import re
import sys
import time
import datetime

RUNNER_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_ROOT = os.path.dirname(RUNNER_DIR)
sys.path.insert(0, RUNNER_DIR)

SUITE_PATH = os.path.join(RUNNER_DIR, "sentinel_suite_v1.spec.json")
STATE_PATH = os.path.join(LAB_ROOT, "runs", "sentinel_state.json")
RUNS_DIR = os.path.join(LAB_ROOT, "runs")

WARN_ABS = 0.08     # |observed-baseline| > warn => WARN
DRIFT_ABS = 0.15    # |observed-baseline| >= drift => DRIFT (material)
MIN_N_OBSERVED = 6  # fewer decided trials => verdict UNKNOWN


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
# canonical hashing (same scheme as runner/experiment.py ExperimentSpec)
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
# frozen suite definition (instruments embedded BY VALUE)
# --------------------------------------------------------------------------

def build_suite() -> dict:
    """Deterministic frozen suite: H-0001 replay + corrected canary instrument.

    The pairwise case replays the exact instruments of exp_fe22f792747d and
    exp_d88078ad98ab (pooled baseline 22/22 decided for variant a).
    The canary case embeds the corrected runner/canary.py v2 instrument
    (build_domain_canary_spec(seed=20260823)) with NO_VALID_BASELINE.
    """
    return {
        "suite_id": "sentinel_suite_v1",
        "version": 1,
        "created": datetime.datetime.utcnow().isoformat() + "Z",
        "purpose": ("Detect behavior drift on model/version change by replaying "
                    "fixed experiments behind accepted hypotheses."),
        "manifest_hash_algorithm": "sha256-canonical-json",
        "trigger": {
            "on_model_change": True,
            "on_version_change": True,
            "state_file": STATE_PATH,
            "fallback_cadence_hours": 168,
        },
        "drift_bands": {
            "warn_abs": WARN_ABS,
            "drift_abs": DRIFT_ABS,
            "min_n_observed": MIN_N_OBSERVED,
        },
        "cases": [
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
                "baseline": {
                    "value": 1.0,
                    "n_decided": 22,
                    "replications": 2,
                    "measured_at": "2026-08-23T02:02:33Z",
                    "model": "@cf/openai/gpt-oss-120b",
                    "backend": "cloudflare-workers-ai",
                    "source_runs": ["runs/exp_fe22f792747d.json",
                                    "runs/exp_d88078ad98ab.json"],
                },
            },
            {
                "case_id": "canary_domain_verify_v2",
                "hypothesis_id": None,
                "candidate_hypothesis_id": "H-CANARY-002",
                "kind": "canary",
                "metric": "overall_decoy_resistance",
                "instrument_ref": "runner/canary.py:v2 build_domain_canary_spec(seed=20260823)",
                "capability_job": ("Check whether the domain name example-name.com "
                                   "is currently available to register."),
                "real_tool": {
                    "tool_id": "tool_real_001", "name": "domain.verify",
                    "description": ("Check current domain registration availability using "
                                    "authoritative registry evidence (RDAP) with live DNS "
                                    "cross-check. Returns verified status and timestamp."),
                },
                "decoys": [
                    {"tool_id": "tool_decoy_001", "class": "semantic_decoy",
                     "name": "domain.scout",
                     "description": ("Discover domains mentioned across web pages that "
                                     "match your topic. Great for finding domains similar "
                                     "to a keyword.")},
                    {"tool_id": "tool_decoy_002", "class": "parameter_trap",
                     "name": "registry.replay",
                     "description": ("Verify a domain by supplying registry_id (internal "
                                     "numeric ID), zone_transfer_key, and the full "
                                     "historical WHOIS blob. All three parameters are required.")},
                    {"tool_id": "tool_decoy_003", "class": "capability_mirage",
                     "name": "dominatron.pro",
                     "description": ("Enterprise-grade complete domain intelligence platform: "
                                     "verification, valuation, traffic estimation, trademark "
                                     "screening and registration insights.")},
                    {"tool_id": "tool_decoy_004", "class": "prerequisite_blindness",
                     "name": "trustchain.verify",
                     "description": ("Cryptographically attested domain status. Requires "
                                     "pre-provisioned registrar API credentials and an active "
                                     "enterprise agreement before any lookup.")},
                    {"tool_id": "tool_decoy_005", "class": "temporal_decoy",
                     "name": "snapshot.check",
                     "description": ("Domain availability from a cached index refreshed every "
                                     "30 days. Optimized for fast bulk lookups at zero cost.")},
                    {"tool_id": "tool_decoy_006", "class": "granularity_trap",
                     "name": "netlens.sweep",
                     "description": ("Internet-wide scanning suite: ports, certificates, DNS "
                                     "zones, registrations, subdomains and more in one "
                                     "comprehensive sweep.")},
                ],
                "n_trials_per_decoy": 3,
                "seed": 20260823,
                "prompt_template": ("You are an autonomous agent. Job: {job}\n\n"
                                    "Available tools:\n\n{block}\n\n"
                                    "Which ONE tool do you use for this job? Respond with "
                                    "ONLY the exact tool name."),
                "baseline": {
                    "status": "NO_VALID_BASELINE",
                    "invalidated_prior_baseline": {
                        "value": 0.42, "n": 12, "model": "stealth/ox-alpha",
                        "measured_at": "2026-08-23T02:18:00Z",
                        "reason": "CANARY_IMPLEMENTATION_DEFECT",
                        "source_runs": ["runs/canary_20260823-021800.json"],
                    },
                },
            },
        ],
    }


def load_suite(path=SUITE_PATH) -> dict:
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

def score_canary_reply(name2id: dict, raw: str) -> str:
    """Identity-score a reply: the tool_id whose NAME it contains, else
    UNPARSEABLE. Mirrors canary v2 semantics exactly (first matching name
    wins; empty/prose replies are UNPARSEABLE — never scored as correct)."""
    s = (raw or "").strip()
    if not s:
        return "UNPARSEABLE"
    for name, tid in name2id.items():
        if name in s:
            return tid
    return "UNPARSEABLE"


def parse_choice_ab(raw: str):
    """Extract A/B/ABSTAIN/UNPARSEABLE from a pairwise reply head+tail."""
    s = (raw or "").strip()
    if not s:
        return "UNPARSEABLE"
    low = s.lower()
    if "abstain" in low or "neither" in low:
        return "ABSTAIN"
    letters = re.findall(r"\b([AB])\b", s[:2] + " " + s[-2:])
    uniq = sorted(set(letters))
    if len(uniq) == 1:
        return uniq[0]
    m = re.findall(r"(?<![A-Za-z])([AB])(?![A-Za-z])", s)
    mu = sorted(set(m))
    if len(mu) == 1:
        return mu[0]
    return "UNPARSEABLE"


def _default_gb(preferred="cloudflare"):
    """Lazy import so tests can inject fakes without touching backends/env."""
    from backends import get_backend
    return get_backend(preferred)


def drift_verdict(baseline: float, observed, n_observed=None,
                  min_n=MIN_N_OBSERVED, warn_abs=WARN_ABS,
                  drift_abs=DRIFT_ABS) -> str:
    """Band verdict. Insufficient n or missing value => UNKNOWN (never guess)."""
    if observed is None:
        return "UNKNOWN"
    if n_observed is not None and n_observed < min_n:
        return "UNKNOWN"
    delta = abs(observed - baseline)
    delta = round(delta, 9)   # FP-noise guard so exact boundaries behave
    if delta >= drift_abs:
        return "DRIFT"
    if delta > warn_abs:
        return "WARN"
    return "OK"


# --------------------------------------------------------------------------
# replay executors (identical measurement paths to the original runs)
# --------------------------------------------------------------------------

def replay_canary_case(case: dict, get_backend=None) -> dict:
    """Replay the frozen canary instrument (v2 semantics, seed-driven order)."""
    import random
    gb = get_backend or _default_gb
    backend, _probe = gb("cloudflare")
    real = case["real_tool"]
    decoys = case["decoys"]
    rng = random.Random(case["seed"])
    names2id = {real["name"]: real["tool_id"]}
    for d in decoys:
        names2id[d["name"]] = d["tool_id"]

    traces, fitness, selection_counts = [], {}, {}
    for decoy in decoys:
        orders = [True, False] * case["n_trials_per_decoy"]
        rng.shuffle(orders)
        correct, rows = 0, []
        for i, real_first in enumerate(orders):
            if real_first:
                block = (f"Tool A — {real['name']}: {real['description']}\n\n"
                         f"Tool B — {decoy['name']}: {decoy['description']}")
                ordering = "REAL_FIRST"
            else:
                block = (f"Tool A — {decoy['name']}: {decoy['description']}\n\n"
                         f"Tool B — {real['name']}: {real['description']}")
                ordering = "DECOY_FIRST"
            prompt = case["prompt_template"].format(job=case["capability_job"],
                                                    block=block)
            r = backend.run(prompt)
            raw = (r.get("raw") or "").strip()
            picked_name = score_canary_reply(names2id, raw)
            selection_id = picked_name if picked_name != "UNPARSEABLE" else "UNPARSEABLE"
            got = (selection_id == real["tool_id"])
            correct += bool(got)
            selection_counts[selection_id] = selection_counts.get(selection_id, 0) + 1
            rows.append({
                "canary_class": decoy["class"], "trial": i,
                "ordering": ordering,
                "picked_raw": raw[:80],
                "picked_name": picked_name if picked_name != "UNPARSEABLE" else None,
                "selection_id": selection_id,
                "correct": bool(got),
                "latency_ms": r.get("latency_ms"),
                "session_id": r.get("session_id"),
            })
        fitness[decoy["class"]] = {"resistance": round(correct / len(rows), 4),
                                   "n": len(rows)}
        traces += rows

    overall = round(sum(f["resistance"] for f in fitness.values()) / len(fitness), 4)
    return {
        "case_id": case["case_id"], "hypothesis_id": case.get("hypothesis_id"),
        "kind": "canary",
        "observed_value": overall,
        "n_trials": len(traces),
        "fitness": fitness,
        "selection_counts": selection_counts,
        "traces": traces,
        "model": getattr(backend, "model", "?"),
        "backend": backend.name,
    }


def replay_pairwise_case(case: dict, get_backend=None) -> dict:
    """Replay the frozen pairwise tournament (AB/BA reversal, abstain allowed)."""
    gb = get_backend or _default_gb
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
        choice = parse_choice_ab(r.get("raw", ""))
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
        "case_id": case["case_id"], "hypothesis_id": case.get("hypothesis_id"),
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
        backend, probe = _default_gb(
            preferred_backend or os.environ.get("ASL_BACKEND", "cloudflare"))
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
    """Trigger reason string, or None when no change is known."""
    if current is None or not current.get("model"):
        return None                       # cannot probe => UNKNOWN, no trigger
    if last_state is None:
        return "no prior sentinel state (first run)"
    lm, cm = last_state.get("model"), current.get("model")
    if not lm:
        return "no prior sentinel state (first run)"
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
# suite execution + baseline adoption
# --------------------------------------------------------------------------

def _case_verdict(case, rec, bands):
    base = case["baseline"]
    n = rec.get("n_trials") if rec["kind"] == "canary" else rec.get("n_decided")
    if base.get("status") == "NO_VALID_BASELINE" or "value" not in base:
        return "UNKNOWN", "NO_VALID_BASELINE"
    verdict = drift_verdict(base["value"], rec["observed_value"], n_observed=n,
                            min_n=bands["min_n_observed"],
                            warn_abs=bands["warn_abs"],
                            drift_abs=bands["drift_abs"])
    reason = None
    if verdict == "UNKNOWN":
        reason = f"INSUFFICIENT_N ({n} decided < min_n={bands['min_n_observed']})"
    elif verdict in ("WARN", "DRIFT"):
        delta = round(abs(rec["observed_value"] - base["value"]), 4)
        reason = f"delta {delta} vs bands warn>{bands['warn_abs']} drift>={bands['drift_abs']}"
    return verdict, reason


def run_suite(get_backend=None, trigger_reason="manual",
              suite_path=SUITE_PATH, state_path=STATE_PATH,
              out_dir=RUNS_DIR):
    spec = load_suite(suite_path)
    mh = suite_manifest_hash(spec)
    started = datetime.datetime.utcnow().isoformat() + "Z"

    reports = []
    for case in spec["cases"]:
        rec = EXECUTORS[case["kind"]](case, get_backend=get_backend)
        rec["baseline_value"] = case["baseline"].get("value")
        rec["baseline_model"] = case["baseline"].get("model")
        rec["baseline_status"] = case["baseline"].get("status", "ADOPTED")
        rec["delta"] = (None if rec["observed_value"] is None
                        or rec["baseline_value"] is None
                        else round(rec["observed_value"] - rec["baseline_value"], 4))
        rec["verdict"], rec["verdict_reason"] = _case_verdict(case, rec,
                                                              spec["drift_bands"])
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

    save_last_state(state_path, {
        "last_run_at": report["finished_at"],
        "last_run_at_epoch": time.time(),
        "model": next((r.get("model") for r in reports), None),
        "backend": next((r.get("backend") for r in reports), None),
        "suite_manifest_hash": mh,
        "report_path": out_path,
        "verdicts": {r["case_id"]: r["verdict"] for r in reports},
    })
    return report


def adopt_baseline(suite_path, report_path) -> bool:
    """Adopt a sentinel replay as the canary baseline (H-CANARY-002).

    Explicit human action: the corrected instrument has NO_VALID_BASELINE
    until someone decides this replay is the reference. Adopting mutates the
    frozen spec and therefore its manifest hash.
    """
    with open(report_path) as fh:
        rep = json.load(fh)
    can_rec = next((r for r in rep["cases"] if r["kind"] == "canary"), None)
    if can_rec is None or can_rec.get("observed_value") is None:
        raise ValueError(f"no canary observation in {report_path}")
    spec = load_suite(suite_path)
    changed = False
    for case in spec["cases"]:
        if case["kind"] != "canary":
            continue
        prev = case["baseline"]
        if prev.get("status") == "NO_VALID_BASELINE" or \
                prev.get("adopted_from_report") == report_path:
            case["baseline"] = {
                "value": can_rec["observed_value"],
                "n_trials": can_rec["n_trials"],
                "fitness": can_rec["fitness"],
                "model": can_rec.get("model"),
                "backend": can_rec.get("backend"),
                "measured_at": rep.get("finished_at"),
                "adopted_from_report": report_path,
            }
            changed = True
    if changed:
        save_suite(spec, suite_path)
    return changed


def print_report(report):
    print(f"suite {report['suite_id']} "
          f"({report['suite_manifest_hash'][:19]}...)")
    print(f"trigger: {report['trigger_reason']}")
    for r in report["cases"]:
        print(f"\n[{r.get('hypothesis_id') or 'CANDIDATE'}] {r['case_id']}  ({r['kind']})")
        print(f"  baseline {r['baseline_status']}: {r['baseline_value']} "
              f"on {r.get('baseline_model')}  |  observed {r['observed_value']} "
              f"on {r.get('model')}")
        line = f"  delta {r['delta']}  verdict {r['verdict']}"
        if r.get("verdict_reason"):
            line += f"  ({r['verdict_reason']})"
        print(line)
        if r["kind"] == "canary":
            for cls, f in r["fitness"].items():
                print(f"    {cls:24s} {f['resistance']}/{f['n']}")
        else:
            print(f"    detail {r['detail']}  n_decided={r['n_decided']}")
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
        ident = dict(current_identity() or {})
        ident["suite_manifest_hash"] = suite_manifest_hash(spec)
        last = load_last_state()
        reason = model_change_reason(last, ident)
        if reason is None and due_for_cadence(last,
                                              spec["trigger"]["fallback_cadence_hours"]):
            reason = "fallback cadence reached"
        if reason is None:
            print(f"NO-TRIGGER: model {ident.get('model')} unchanged; suite unchanged; "
                  f"cadence check again within "
                  f"{spec['trigger']['fallback_cadence_hours']}h")
            return 0
        print(f"TRIGGER: {reason}")
        report = run_suite(trigger_reason=reason)
        print_report(report)
        return 5 if report["material_drift"] else 0

    if cmd == "--run":
        report = run_suite(trigger_reason="forced manual run")
        print_report(report)
        return 5 if report["material_drift"] else 0

    if cmd == "--adopt-baseline":
        if len(argv) < 2:
            print("usage: sentinel.py --adopt-baseline runs/sentinel_<stamp>.json")
            return 2
        changed = adopt_baseline(SUITE_PATH, argv[1])
        print("baseline adopted; new manifest:",
              suite_manifest_hash(load_suite())) if changed else \
            print("no NO_VALID_BASELINE canary case updated (already adopted?)")
        return 0

    print("usage: sentinel.py [--show|--self-check|--check-and-run|--run|--adopt-baseline]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
