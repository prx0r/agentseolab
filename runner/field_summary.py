#!/usr/bin/env python3
"""Deterministic batch summary for agentseo-field (protocol §9.5).

Counts only — no quality judgments. Reads lab.db field_trials/observations.
Per-subject breakdown maps trial sessions to subject profiles via the
immutable trace files (results/field/*/trace_raw.json), keeping the
field_trials schema byte-compatible with the Rust struct.

Usage: python3 runner/field_summary.py [--db lab.db] [--json]
"""
import argparse
import glob
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict

DB_DEFAULT = "/root/agentseolab/lab.db"
TRACES_ROOT = "/root/agentseolab/results/field"


def subject_by_session(traces_root=TRACES_ROOT):
    """session_id -> subject profile, from immutable trace_raw.json files."""
    m = {}
    for path in sorted(glob.glob(
            os.path.join(traces_root, "*", "trace_raw.json"))):
        if os.path.basename(os.path.dirname(path)).startswith("superseded"):
            continue
        try:
            t = json.load(open(path))
            m[t["subject"]["session_id"]] = \
                t["subject"].get("profile", "unknown")
        except (OSError, KeyError, json.JSONDecodeError):
            continue
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB_DEFAULT)
    ap.add_argument("--intent", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    where, params = "", []
    if a.intent:
        where = "WHERE intent_id=?"
        params = [a.intent]

    trials = list(con.execute(
        f"SELECT trial_id, intent_id, agent_model, provider, session_id, "
        f"started_at, completed_at, final_action, task_success "
        f"FROM field_trials {where} ORDER BY started_at", params))

    out = {"trials": [], "n": len(trials)}
    per_event = Counter()
    per_subject = defaultdict(Counter)   # profile -> Counter of metrics
    subj_map = subject_by_session()
    activation_n = 0
    success_n = 0
    success_known = 0

    for t in trials:
        obs = list(con.execute(
            "SELECT event_type, payload_json FROM observations "
            "WHERE session_id=?", (t["session_id"],)))
        kinds = Counter(o["event_type"] for o in obs)
        # search activation = any recorded search intent this session
        searches = con.execute(
            "SELECT COUNT(*) FROM observations WHERE session_id=? AND "
            "(event_type='search_query' OR event_type='search_results')",
            (t["session_id"],)).fetchone()[0]
        if searches:
            activation_n += 1
        per_event.update(kinds)
        if t["task_success"] is not None:
            success_known += 1
            success_n += bool(t["task_success"])
        subject = subj_map.get(t["session_id"], "unknown")
        sc = per_subject[subject]
        sc["n_trials"] += 1
        sc["task_success_known"] += int(t["task_success"] is not None)
        sc["task_success"] += int(bool(t["task_success"]))
        sc["search_activation"] += int(bool(searches))
        sc["events"] += sum(kinds.values())
        out["trials"].append({
            "trial_id": t["trial_id"],
            "intent_id": t["intent_id"],
            "model": t["agent_model"],
            "provider": t["provider"],
            "subject": subject,
            "session_id": t["session_id"],
            "events": dict(kinds),
            "search_intent_recorded": bool(searches),
            "task_success": t["task_success"],
            "final_action": t["final_action"],
        })

    out["per_subject"] = {
        s: dict(c) for s, c in sorted(per_subject.items())
    }
    out["aggregate"] = {
        "n_trials": len(trials),
        "search_activation_rate": (round(activation_n / len(trials), 3)
                                   if trials else None),
        "task_success_rate": (round(success_n / success_known, 3)
                              if success_known else None),
        "event_type_totals": dict(per_event),
        "note": "counts from immutable traces; judgments prohibited by protocol §0",
    }
    con.close()

    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"FIELD BATCH SUMMARY — intent F-001 (find-domain-availability-api)")
        print(f"trials: {len(trials)}")
        print(f"search_activation_rate: {out['aggregate']['search_activation_rate']}")
        print(f"task_success_rate:      {out['aggregate']['task_success_rate']}  (n known={success_known})")
        print("per-subject (counts only):")
        for s, c in out["per_subject"].items():
            print(f"  {s:10s} n={c.get('n_trials',0)} "
                  f"success={c.get('task_success',0)}/{c.get('task_success_known',0)} "
                  f"search_act={c.get('search_activation',0)}/{c.get('n_trials',0)} "
                  f"events={c.get('events',0)}")
        print("event totals:")
        for k, v in sorted(per_event.items()):
            print(f"  {k:16s} {v}")
        for t in out["trials"]:
            print(f"  · {t['trial_id']} [{t['subject']}] sess={t['session_id']} "
                  f"success={t['task_success']} events={t['events']}")


if __name__ == "__main__":
    main()
