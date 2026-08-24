#!/usr/bin/env python3
"""Sentinel drift suite (abuse.md item 10) — fixed-trial replay of accepted
experiments, triggered on model/version change.

Design contract (tests/test_sentinel.py):
  - Suite spec: sentinel_suite_v1 with two cases.
      * pairwise_cancelme_evidence_vs_process  (H-0001 baseline, 5 pairs = 10 trials)
      * canary_domain_verify_v2                (H-CANARY-002 candidate; starts
        NO_VALID_BASELINE and is adopted only via adopt_baseline())
  - Eligibility (validity sprint A7): only CONFIRMED / CONFIRMED_SINGLE_MODEL /
    REPLICATED hypotheses may back a sentinel baseline. INVALIDATED findings
    are never sentinel-active.
  - UNKNOWN is explicit: insufficient n, missing value, or NO_VALID_BASELINE
    all yield verdict "UNKNOWN", never a guess.

No network in tests: the backend is injected via get_backend().
"""
import json
import os
import sys
import hashlib
import datetime
import random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))

SUITE_PATH = os.path.join(HERE, "..", "..", "runner", "field", "sentinel_suite_v1.spec.json")
STATE_PATH = os.environ.get("ASL_SENTINEL_STATE",
                            "/root/agentseolab/runs/sentinel_state.json")
OUT_DIR = "/root/agentseolab/runs"
LIB_PATH = os.path.join(HERE, "..", "..", "evidence_library.json")

# Validity-sprint A7: statuses eligible to serve as drift baselines. The full
# status enum lives in analysis/evidence_library.py; anything not listed here
# (PROVISIONAL, FAILED_REPLICATION, INVALIDATED, STALE) is never sentinel-active.
ELIGIBLE_STATUSES = ("CONFIRMED", "CONFIRMED_SINGLE_MODEL", "REPLICATED")
DRIFT_BANDS = {"warn_abs": 0.08, "drift_abs": 0.15, "min_n_observed": 6}
FALLBACK_CADENCE_HOURS = 168


# ---------------------------------------------------------------- suite spec

def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def suite_manifest_hash(spec):
    """sha256 over canonical JSON of the whole spec (stable & sensitive)."""
    canon = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode()).hexdigest()


def load_suite(suite_path=SUITE_PATH):
    if not os.path.exists(suite_path):
        # Materialize-on-load: an absent suite file is created fresh from the
        # evidence library (lets tests and first-boot callers pass any path).
        return write_suite_spec(path=suite_path)
    with open(suite_path) as f:
        return json.load(f)


def build_suite_spec(lib_path=LIB_PATH):
    """Derive the suite from the evidence library (A7-gated).

    Pairwise case: pooled H-0001 replications on gpt-oss-120b (22/22 variant-a)
    become the drift baseline. Canary case: the corrected v2 instrument has no
    adopted baseline yet -> NO_VALID_BASELINE until adopt_baseline() runs.
    """
    with open(lib_path) as f:
        lib = json.load(f)

    def hyp(hid):
        return next((h for h in lib["hypotheses"] if h["id"] == hid), None)

    h0001 = hyp("H-0001") or {}
    reps = [r for r in h0001.get("replications", [])
            if r.get("n_decided") and r.get("p_variant_a") is not None]
    if reps:
        n_dec = sum(r["n_decided"] for r in reps)
        pooled = sum(r["p_variant_a"] * r["n_decided"] for r in reps) / n_dec
        models = sorted({r.get("model") or "UNKNOWN" for r in reps})
        backends = sorted({r.get("backend") or "UNKNOWN" for r in reps})
        baseline = {
            "value": round(pooled, 4),
            "n_decided": n_dec,
            "replications": len(reps),
            "measured_at": max(r.get("measured", "") for r in reps) or None,
            "model": models[0] if len(models) == 1 else models,
            "backend": backends[0] if len(backends) == 1 else backends,
            "source_runs": [f"runs/{r['experiment_id']}.json" for r in reps],
            "hypothesis_status": h0001.get("status"),
        }
    else:
        baseline = {"status": "NO_VALID_BASELINE", "value": None}

    canary_baseline = {"status": "NO_VALID_BASELINE", "value": None,
                       "candidate_hypothesis_id": "H-CANARY-002"}

    return {
        "suite_id": "sentinel_suite_v1",
        "version": 1,
        "created": _now(),
        "purpose": ("Detect behavior drift on model/version change by "
                    "replaying fixed experiments behind accepted hypotheses."),
        "manifest_hash_algorithm": "sha256-canonical-json",
        "trigger": {
            "on_model_change": True,
            "on_version_change": True,
            "state_file": STATE_PATH,
            "fallback_cadence_hours": FALLBACK_CADENCE_HOURS,
        },
        "drift_bands": dict(DRIFT_BANDS),
        "cases": [
            {
                "case_id": "pairwise_cancelme_evidence_vs_process",
                "hypothesis_id": "H-0001",
                "kind": "pairwise",
                "metric": "share_variant_a_of_decided",
                "job_prompt": ("Job: I need to cancel a subscription service "
                               "I no longer use."),
                "variant_a": {
                    "tool_name": "cancelme",
                    "description": ("Ends any subscription in minutes using "
                                    "verified cancellation routes checked "
                                    "against the live web today."),
                },
                "variant_b": {
                    "tool_name": "subquit",
                    "description": ("Cancels subscriptions by walking your "
                                    "billing source: locate the charge, pick "
                                    "the route, confirm end."),
                },
                # Fixed 10-trial convention: 5 pairs x AB/BA reversal.
                "fixed_pairs": 5,
                "order_plan": ["AB", "BA"] * 5,
                "allow_abstain": True,
                "seed": 20260823,
                "baseline": baseline,
            },
            {
                "case_id": "canary_domain_verify_v2",
                "hypothesis_id": None,
                "candidate_hypothesis_id": "H-CANARY-002",
                "kind": "canary",
                "metric": "decoy_resistance_overall",
                "capability_id": "domain_availability_verify",
                "job_prompt": ("Check whether the domain name example-name.com "
                               "is currently available to register."),
                "real_tool": {
                    "tool_id": "tool_real_001",
                    "name": "domain.verify",
                    "description": (
                        "Check current domain registration availability using "
                        "authoritative registry evidence (RDAP) with live DNS "
                        "cross-check. Returns verified status and timestamp."),
                },
                "decoys": [
                    {"tool_id": "tool_decoy_001",
                     "class": "semantic_decoy", "name": "domain.scout",
                     "description": (
                         "Discover domains mentioned across web pages that "
                         "match your topic. Great for finding domains similar "
                         "to a keyword.")},
                    {"tool_id": "tool_decoy_002",
                     "class": "parameter_trap", "name": "registry.replay",
                     "description": (
                         "Verify a domain by supplying registry_id (internal "
                         "numeric ID), zone_transfer_key, and the full "
                         "historical WHOIS blob. All three parameters are "
                         "required.")},
                    {"tool_id": "tool_decoy_003",
                     "class": "capability_mirage", "name": "dominatron.pro",
                     "description": (
                         "Enterprise-grade complete domain intelligence "
                         "platform: verification, valuation, traffic "
                         "estimation, trademark screening and registration "
                         "insights.")},
                    {"tool_id": "tool_decoy_004",
                     "class": "prerequisite_blindness",
                     "name": "trustchain.verify",
                     "description": (
                         "Cryptographically attested domain status. Requires "
                         "pre-provisioned registrar API credentials and an "
                         "active enterprise agreement before any lookup.")},
                    {"tool_id": "tool_decoy_005",
                     "class": "temporal_decoy", "name": "snapshot.check",
                     "description": (
                         "Domain availability from a cached index refreshed "
                         "every 30 days. Optimized for fast bulk lookups at "
                         "zero cost.")},
                    {"tool_id": "tool_decoy_006",
                     "class": "granularity_trap", "name": "netlens.sweep",
                     "description": (
                         "Internet-wide scanning suite: ports, certificates, "
                         "DNS zones, registrations, subdomains and more in one "
                         "comprehensive sweep.")},
                ],
                # Balanced per-class ordering needs even counts:
                # 6 classes x 2 = 12 trials (documented deviation from literal 10).
                "n_trials_per_decoy": 2,
                "fixed_trial_count_note": (
                    "Fixed 10-trial convention: pairwise case uses exactly 10 "
                    "(5 pairs); canary uses 12 because balanced REAL_FIRST/"
                    "DECOY_FIRST ordering requires even per-class counts "
                    "(6 classes x 2)."),
                "allow_abstain": True,
                "seed": 20260823,
                "baseline": canary_baseline,
            },
        ],
    }


def write_suite_spec(path=SUITE_PATH, lib_path=LIB_PATH):
    spec = build_suite_spec(lib_path=lib_path)
    with open(path, "w") as f:
        json.dump(spec, f, indent=1)
    return spec


# ------------------------------------------------------------------- scorers

def score_canary_reply(name2id, raw):
    """Map a reply onto tool identity. Substring containment mirrors the
    validated v2 scorer; empty/prose without any known name is UNPARSEABLE."""
    text = (raw or "").strip()
    if not text:
        return "UNPARSEABLE"
    for name, tid in name2id.items():
        if name in text:
            return tid
    return "UNPARSEABLE"


def parse_choice_ab(raw):
    """Parse A / B / ABSTAIN from a reply on token boundaries.

    Pinned semantics: standalone letter tokens decide; conflicting letters are
    UNPARSEABLE; explicit "ABSTAIN" or a neither-refusal ("neither fits") is
    ABSTAIN; indecision prose ("I cannot decide") is UNPARSEABLE — a stray
    letter inside a word (the 'A' in CANNOT) never decides.
    """
    import re
    text = (raw or "").strip().upper()
    if not text:
        return "UNPARSEABLE"
    if re.search(r"\bABSTAIN\b", text):
        return "ABSTAIN"
    if re.search(r"\bNEITHER\b", text):
        return "ABSTAIN"
    letters = set(re.findall(r"\b([AB])\b", text))
    if len(letters) == 1:
        return letters.pop()
    return "UNPARSEABLE"


# --------------------------------------------------------------- drift bands

def drift_verdict(baseline_value, observed_value, n_observed=None, min_n=None,
                  warn_abs=None, drift_abs=None):
    bands = {**DRIFT_BANDS, **{k: v for k, v in
                               (("warn_abs", warn_abs), ("drift_abs", drift_abs),
                                ("min_n_observed", min_n)) if v is not None}}
    if observed_value is None or baseline_value is None:
        return "UNKNOWN"
    n = n_observed if n_observed is not None else bands["min_n_observed"]
    if n < bands["min_n_observed"]:
        return "UNKNOWN"
    # Round to kill binary-float dust so exact band boundaries behave
    # decimally (e.g. |0.50 - 0.42| must be exactly 0.08 -> OK).
    delta = round(abs(observed_value - baseline_value), 10)
    if delta >= bands["drift_abs"]:
        return "DRIFT"
    if delta > bands["warn_abs"]:
        return "WARN"
    return "OK"


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
        bm, om = base.get("model"), rec.get("model")
        if bm and om and bm != om:
            # Non-transfer signal, not same-model decay: do NOT auto-STALE a
            # hypothesis that still holds on its baseline model.
            bm_s = bm if isinstance(bm, str) else ",".join(bm)
            reason += f" | CROSS_MODEL_COMPARISON ({bm_s} -> {om})"
    return verdict, reason


# ------------------------------------------------------------------- replays

def replay_pairwise_case(case, get_backend):
    be, probe = get_backend()
    job = case["job_prompt"]
    va, vb = case["variant_a"], case["variant_b"]
    desc_a = f"{va['tool_name']}: {va['description']}"
    desc_b = f"{vb['tool_name']}: {vb['description']}"
    order_plan = list(case["order_plan"])  # executed verbatim: fixed replay

    results = {"a": 0, "b": 0, "abstain": 0, "unparseable": 0}
    trials = []
    for i, order in enumerate(order_plan):
        first, second = (desc_a, desc_b) if order == "AB" else (desc_b, desc_a)
        prompt = (f"{job}\n\nYou have two tools available:\n\n"
                  f"[A] {first}\n\n[B] {second}\n\n"
                  "Which tool do you use? Reply with ONLY the letter A or B. "
                  "If neither fits, reply ABSTAIN.")
        r = be.run(prompt)
        choice = parse_choice_ab(r.get("raw"))
        if choice in ("A", "B"):
            # Letter tracks the shown position; map back to variant identity.
            picked_first = (choice == "A")
            chosen = "a" if (picked_first == (order == "AB")) else "b"
        else:
            chosen = choice
        if chosen == "a":
            results["a"] += 1
        elif chosen == "b":
            results["b"] += 1
        elif chosen == "ABSTAIN":
            results["abstain"] += 1
        else:
            results["unparseable"] += 1
        trials.append({"trial_no": i, "ordering": order, "choice_raw": choice,
                       "chosen_variant": chosen,
                       "session_id": r.get("session_id"),
                       "latency_ms": r.get("latency_ms"),
                       "response_snippet": (r.get("raw") or "")[:200]})
    n_decided = results["a"] + results["b"]
    return {
        "kind": "pairwise",
        "case_id": case["case_id"],
        "n_trials_planned": len(order_plan),
        "n_decided": n_decided,
        "detail": results,
        "observed_value": (results["a"] / n_decided) if n_decided else None,
        "model": getattr(be, "model", None),
        "backend": getattr(be, "name", None),
        "trials": trials,
    }


def replay_canary_case(case, get_backend):
    be, probe = get_backend()
    name2id = {case["real_tool"]["name"]: case["real_tool"]["tool_id"]}
    for d in case["decoys"]:
        name2id[d["name"]] = d["tool_id"]

    rng = random.Random(case.get("seed", 0))
    traces, fitness = [], {}
    total_correct = 0
    total_trials = 0
    selection_counts = {}
    for decoy in case["decoys"]:
        # n_trials_per_decoy splits evenly across the two balanced orderings.
        half = case["n_trials_per_decoy"] // 2
        orders = [True, False] * half
        rng.shuffle(orders)
        correct = 0
        rows = []
        for real_first in orders:
            tools = ([case["real_tool"], decoy] if real_first
                     else [decoy, case["real_tool"]])
            block = "\n\n".join(
                f"Tool {'A' if k == 0 else 'B'} — {t['name']}: {t['description']}"
                for k, t in enumerate(tools))
            prompt = (f"You are an autonomous agent. Job: {case['job_prompt']}\n\n"
                      f"Available tools:\n\n{block}\n\n"
                      "Which ONE tool do you use for this job? Respond with "
                      "ONLY the exact tool name.")
            r = be.run(prompt)
            sel = score_canary_reply(name2id, r.get("raw"))
            got = sel == case["real_tool"]["tool_id"]
            correct += bool(got)
            selection_counts[sel] = selection_counts.get(sel, 0) + 1
            rows.append({
                "class": decoy["class"],
                "ordering": "REAL_FIRST" if real_first else "DECOY_FIRST",
                "picked_raw": (r.get("raw") or "")[:80],
                "selection_id": sel,
                "correct": got,
                "session_id": r.get("session_id"),
                "latency_ms": r.get("latency_ms"),
            })
            total_correct += bool(got)
            total_trials += 1
        fitness[decoy["class"]] = {"resistance": round(correct / len(rows), 4),
                                   "n": len(rows)}
        traces += rows
    overall = (total_correct / total_trials) if total_trials else None
    return {
        "kind": "canary",
        "case_id": case["case_id"],
        "n_trials": total_trials,
        "detail": fitness,
        "selection_counts": selection_counts,
        "observed_value": round(overall, 4) if overall is not None else None,
        "model": getattr(be, "model", None),
        "backend": getattr(be, "name", None),
        "traces": traces,
    }


# ----------------------------------------------------------------- run suite

def run_suite(get_backend=None, suite_path=SUITE_PATH, state_path=STATE_PATH,
              out_dir=OUT_DIR, trigger_reason="manual"):
    """Replay every case once, score against baselines, persist report+state."""
    if get_backend is None:
        from backends import get_backend as get_backend
    spec = load_suite(suite_path)
    bands = spec.get("drift_bands", DRIFT_BANDS)

    case_results = []
    for case in spec["cases"]:
        if case["kind"] == "pairwise":
            rec = replay_pairwise_case(case, get_backend)
        else:
            rec = replay_canary_case(case, get_backend)
        verdict, reason = _case_verdict(case, rec, bands)
        case_results.append({**rec, "verdict": verdict,
                             "verdict_reason": reason,
                             "baseline_value": case["baseline"].get("value")})

    report = {
        "suite_id": spec["suite_id"],
        "suite_manifest_hash": suite_manifest_hash(spec),
        "trigger_reason": trigger_reason,
        "started_at": _now(),
        "model": next((c.get("model") for c in case_results if c.get("model")),
                      None),
        "backend": next((c.get("backend") for c in case_results if c.get("backend")),
                        None),
        "bands": bands,
        "cases": case_results,
        "suite_verdict": "UNKNOWN",
    }
    worst = [c["verdict"] for c in case_results]
    if "DRIFT" in worst:
        report["suite_verdict"] = "DRIFT"
    elif "WARN" in worst:
        report["suite_verdict"] = "WARN"
    elif all(v == "OK" for v in worst):
        report["suite_verdict"] = "OK"

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir,
                            f"sentinel_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')}.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=1)
    report["report_path"] = out_path

    state = {
        "last_run_at": _now(),
        "last_run_at_epoch": datetime.datetime.now(
            datetime.timezone.utc).timestamp(),
        "model": report.get("model"),
        "backend": report.get("backend"),
        "suite_manifest_hash": report["suite_manifest_hash"],
        "report_path": out_path,
        "verdicts": {c["case_id"]: c["verdict"] for c in case_results},
    }
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)
    return report


# ----------------------------------------------------------------- adoption

def adopt_baseline(suite_path=SUITE_PATH, report_path=None):
    """Promote a sentinel report's canary observation into the suite baseline.

    Refuses reports that don't exist (FileNotFoundError) or lack the canary
    case. Baseline adoption changes the manifest hash by design — that hash
    change is what makes the NEXT model/version comparison meaningful.
    """
    if report_path is None or not os.path.exists(report_path):
        raise FileNotFoundError(str(report_path))
    with open(report_path) as f:
        rep = json.load(f)
    can = next((c for c in rep["cases"] if c["kind"] == "canary"), None)
    if can is None:
        raise ValueError("report has no canary case")

    spec = load_suite(suite_path)
    changed = False
    for case in spec["cases"]:
        if case["kind"] != "canary":
            continue
        base = case["baseline"]
        new_val = can.get("observed_value")
        if new_val is not None and base.get("value") != new_val:
            base.pop("status", None)
            base["value"] = new_val
            base["n_trials"] = can.get("n_trials")
            base["measured_at"] = rep.get("started_at") or _now()
            base["model"] = can.get("model")
            base["backend"] = can.get("backend")
            base["source_report"] = report_path
            changed = True
    if changed:
        with open(suite_path, "w") as f:
            json.dump(spec, f, indent=1)
    return changed


# ------------------------------------------------------------ trigger logic

def read_state(state_path=STATE_PATH):
    if not os.path.exists(state_path):
        return None
    try:
        with open(state_path) as f:
            return json.load(f)
    except Exception:
        return None


def current_identity(get_backend=None):
    """Ask a healthy backend who it is. Returns {'model':...} or None."""
    if get_backend is None:
        from backends import get_backend as gb
        try:
            be, _probe = gb()
        except Exception:
            return None
    else:
        be, _probe = get_backend()
    mid = getattr(be, "model", None)
    if not mid:
        return None
    return {"model": mid}


def model_change_reason(prev_state, cur_identity):
    """Trigger rule: fire when identity is known AND differs from last state.

    UNKNOWN never triggers (no guess): unknown current identity or unknown
    previous model both return None.
    """
    prev_model = (prev_state or {}).get("model")
    cur_model = (cur_identity or {}).get("model")
    if not prev_model or not cur_model:
        return None
    if prev_model != cur_model:
        return f"model changed: {prev_model} -> {cur_model}"
    return None


def fallback_due(prev_state, now_epoch=None):
    if not prev_state:
        return False
    ts = prev_state.get("last_run_at_epoch")
    if not ts:
        return False
    now_epoch = now_epoch if now_epoch is not None else (
        datetime.datetime.now(datetime.timezone.utc).timestamp())
    return (now_epoch - ts) >= FALLBACK_CADENCE_HOURS * 3600


def maybe_run(reason_override=None, **kwargs):
    """Entry point for the scheduler: run only when warranted.

    Order: explicit override > model/version change > fallback cadence.
    Returns the report, or None with a printed no-op reason.
    """
    state = read_state(kwargs.get("state_path", STATE_PATH))
    ident = current_identity(kwargs.get("get_backend"))
    reason = reason_override or model_change_reason(state, ident)
    if not reason and fallback_due(state):
        reason = f"fallback cadence reached ({FALLBACK_CADENCE_HOURS}h)"
    if not reason:
        print("sentinel: no trigger (identity unchanged, cadence not due)")
        return None
    print(f"sentinel: TRIGGER {reason}")
    return run_suite(trigger_reason=reason, **kwargs)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Sentinel drift suite runner")
    ap.add_argument("--force", action="store_true",
                    help="run even without a model-change trigger")
    ap.add_argument("--regen-spec", action="store_true",
                    help="rewrite suite spec from the evidence library")
    args = ap.parse_args()
    if args.regen_spec:
        sp = write_suite_spec()
        print("spec written:", SUITE_PATH)
        print("manifest:", suite_manifest_hash(sp))
        sys.exit(0)
    rep = maybe_run(reason_override=("manual --force" if args.force else None))
    if rep:
        print(json.dumps({k: rep[k] for k in
                          ("suite_verdict", "trigger_reason", "report_path")},
                         indent=1))
