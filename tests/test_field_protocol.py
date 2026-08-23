#!/usr/bin/env python3
"""Protocol self-tests: extraction rules, schema conformance, idempotent ingest.

Run from anywhere. Uses only the pilot trace + a scratch copy of lab.db.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, "/root/agentseolab/runner")
from field import (URL_RE, canonical_hash, extract_events, host_of,
                   is_search_engine)

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))


# ---------- unit: url/search-engine classification ----------
check("host_of", host_of("https://www.whoisxmlapi.com/x") == "www.whoisxmlapi.com")
check("search_engine_google", is_search_engine("https://www.google.com/search?q=x"))
check("search_engine_ddg", is_search_engine("https://duckduckgo.com/?q=x"))
check("not_search_engine_vendor",
      not is_search_engine("https://www.whoisxmlapi.com/"))
check("url_regex_basic", URL_RE.findall("see https://a.io/x and http://b.org/y") ==
      ["https://a.io/x", "http://b.org/y"])

# ---------- unit: canonical hash matches models.rs ----------
payload = json.load(open("/root/agentseolab/examples/site_intent.json"))
intent = {
    "purpose": payload["purpose"], "primary_job": payload["primary_job"],
    "audiences": payload["audiences"], "capabilities": payload["capabilities"],
    "geographic_scope": None, "language": "en", "commercial_model": None,
    "constraints": payload.get("constraints", {}), "prohibited_meanings": [],
    "desired_tld": None, "desired_length": None, "desired_word_rules": None,
}
check("canonical_hash_matches_rust",
      canonical_hash(intent) == "3939117e2637448335a9c107ac11dd6ac306e54384a0dc6badcc1cbf7d7814eb")

# ---------- frozen intent integrity in live lab.db ----------
con = sqlite3.connect("file:/root/agentseolab/lab.db?mode=ro", uri=True)
row = con.execute("SELECT intent_hash, purpose, primary_job FROM site_intents "
                  "WHERE intent_id='intent_f001domainavail7c31'").fetchone()
rec = json.load(open("/root/agentseolab/results/field/INTENT_F001.json"))
check("frozen_intent_present", row is not None)
check("frozen_intent_hash_stable", row and row[0] == rec["intent_hash"])
check("frozen_intent_job_is_f001",
      row and row[2] == "find-domain-availability-api")
recomputed = canonical_hash(rec["payload"])
check("frozen_intent_hash_recomputes", recomputed == rec["intent_hash"])

# ---------- pilot trial ingested exactly once ----------
n = con.execute("SELECT COUNT(*) FROM field_trials WHERE session_id=?",
                ("20260823_023900_f63b4b",)).fetchone()[0]
check("pilot_trial_once", n == 1, f"n={n}")
trial = con.execute(
    "SELECT trial_id, intent_id, agent_model, provider, task_success, "
    "final_action FROM field_trials WHERE session_id=?",
    ("20260823_023900_f63b4b",)).fetchone()
check("pilot_trial_references_frozen_intent",
      trial and trial[1] == "intent_f001domainavail7c31")
nobs = con.execute("SELECT COUNT(*) FROM observations WHERE session_id=?",
                   ("20260823_023900_f63b4b",)).fetchone()[0]
ev_count = len(json.load(open(
    "/root/agentseolab/results/field/20260823T024100Z_scout_f001pilot/trace_raw.json"))["events"])
check("observations_match_trace", nobs == ev_count, f"{nobs} vs {ev_count}")

valid_events = {"search_query", "search_results", "result_open", "citation",
                "final_choice", "rationale", "tool_invocation"}
bad = con.execute(
    "SELECT COUNT(*) FROM observations WHERE session_id=? AND evidence_tier!='field'",
    ("20260823_023900_f63b4b",)).fetchone()[0]
check("all_pilot_obs_are_field_tier", bad == 0)
bad2 = con.execute(
    f"SELECT COUNT(*) FROM observations WHERE session_id=? AND "
    f"event_type NOT IN ({','.join('?'*len(valid_events))})",
    ("20260823_023900_f63b4b", *valid_events)).fetchone()[0]
check("all_pilot_event_types_in_vocab", bad2 == 0)
con.close()

# ---------- idempotency: re-ingest must not duplicate ----------
tmpdb = tempfile.mktemp(suffix=".db")
shutil.copy("/root/agentseolab/lab.db", tmpdb)
r = subprocess.run(["python3", "/root/agentseolab/runner/field.py", "ingest",
                    "--trace", "/root/agentseolab/results/field/20260823T024100Z_scout_f001pilot",
                    "--db", tmpdb], capture_output=True, text=True)
con = sqlite3.connect(tmpdb)
n_after = con.execute("SELECT COUNT(*) FROM field_trials WHERE session_id=?",
                      ("20260823_023900_f63b4b",)).fetchone()[0]
nobs_after = con.execute("SELECT COUNT(*) FROM observations WHERE session_id=?",
                         ("20260823_023900_f63b4b",)).fetchone()[0]
con.close()
os.remove(tmpdb)
check("reingest_skips_duplicates",
      r.returncode == 0 and n_after == 1 and nobs_after == ev_count,
      f"rc={r.returncode} trials={n_after} obs={nobs_after}")
out = r.stdout
check("reingest_emits_skip_notice", "SKIP" in out, out[:80])

# ---------- synthetic-trace guard: extractor on fabricated session ----------
class FakeRow(dict):
    def __getitem__(self, k):
        return dict.__getitem__(self, k)


fake_msgs = [
    {"id": 1, "role": "user", "content": "task", "tool_name": None,
     "tool_calls": None, "timestamp": 100},
    {"id": 2, "role": "assistant", "content": "", "tool_name": None,
     "tool_calls": json.dumps([{"id": "c1", "function": {
         "name": "web_search", "arguments": '{"query": "best domain api"}'}}]),
     "timestamp": 101},
    {"id": 3, "role": "tool", "content": "result https://x.io/a then https://y.io/b",
     "tool_name": "web_search", "tool_calls": None, "timestamp": 102},
]
events = extract_events(fake_msgs)
kinds = [e["event_type"] for e in events]
check("synthetic_unit_fixture_search_query", "search_query" in kinds)
check("synthetic_unit_fixture_results_join",
      any(e["event_type"] == "search_results" and
          len(e["payload"].get("results", [])) == 2 for e in events))
sq = next(e for e in events if e["event_type"] == "search_query")
sr = next((e for e in events if e["event_type"] == "search_results" and
           "results" in e["payload"]), None)
check("results_ranked_in_order",
      sr and [r["rank"] for r in sr["payload"]["results"]] == [1, 2])

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
