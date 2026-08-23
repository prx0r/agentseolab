#!/usr/bin/env python3
"""Field trial batch runner (agentseo-field protocol v1).

Runs N fresh sessions per subject profile against the frozen F-001 intent,
extracts each session's trace, and ingests into lab.db. Idempotent per session.

Usage:
  python3 runner/field_batch.py --n 3 [--profile scout]
  python3 runner/field_batch.py --n 2 --profile scout --profile curator \
      --profile patala        # --profile is repeatable (§2 subjects)
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time

sys.path.insert(0, "/root/agentseolab/runner")

PROMPT = (
    "Find a domain availability API: a service that checks whether a domain "
    "name is available to register. Use your web search and browsing tools to "
    "find real services. When you have found one, report its name and URL."
)

INTENT = json.load(open("/root/agentseolab/runs/field/INTENT_F001.json"))
DB = "/root/agentseolab/lab.db"


def latest_session_id(profile, profile_db=None):
    """Latest session id for a given subject profile (§2: one store per subject)."""
    state_db = profile_db or f"/root/.hermes/profiles/{profile}/state.db"
    con = sqlite3.connect(f"file:{state_db}?mode=ro", uri=True)
    row = con.execute("SELECT id FROM sessions ORDER BY started_at DESC "
                      "LIMIT 1").fetchone()
    con.close()
    return row[0] if row else None


def already_ingested(session_id):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    n = con.execute("SELECT COUNT(*) FROM field_trials WHERE session_id=?",
                    (session_id,)).fetchone()[0]
    con.close()
    return n > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--profile", action="append", default=None,
                    help="subject profile (§2); repeatable")
    a = ap.parse_args()
    profiles = a.profile or ["scout"]

    results = []
    for profile in profiles:
        for i in range(a.n):
            t0 = time.time()
            try:
                r = subprocess.run(
                    ["hermes", "--profile", profile, "-z", PROMPT],
                    capture_output=True, text=True, timeout=600)
                wall = round(time.time() - t0, 1)
                exit_code = r.returncode
            except subprocess.TimeoutExpired:
                # Appendix B: timeout ⇒ partial trace, still ingested (§4.4)
                wall = round(time.time() - t0, 1)
                exit_code = 124
                print(f"[{profile} {i+1}/{a.n}] TIMEOUT after {wall}s "
                      f"(partial-trace ingestion)")
            sid = latest_session_id(profile)
            print(f"[{profile} {i+1}/{a.n}] session={sid} exit={exit_code} "
                  f"wall={wall}s")
            if not sid or already_ingested(sid):
                print("   skip: no new session / already ingested")
                continue
            out_dir = (f"/root/agentseolab/runs/field/"
                       f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
                       f"_{profile}_f001")
            x = subprocess.run(
                ["python3", "/root/agentseolab/runner/field.py", "extract",
                 "--profile", profile, "--session", sid,
                 "--intent-id", INTENT["intent_id"],
                 "--intent-hash", INTENT["intent_hash"],
                 "--out", out_dir,
                 "--model", "mimo-v2.5", "--provider", "opencode-go",
                 "--network-environment",
                 "live-web-browser+curl; google blocked(captcha); ddg reachable"],
                capture_output=True, text=True)
            print("   extract:", (x.stdout.strip().splitlines() or ["?"])[-1])
            if x.returncode != 0:
                print("   extract FAILED:", x.stderr[-200:])
                continue
            g = subprocess.run(
                ["python3", "/root/agentseolab/runner/field.py", "ingest",
                 "--trace", out_dir, "--db", DB],
                capture_output=True, text=True)
            print("   ingest:", g.stdout.strip() or g.stderr.strip()[:200])
            results.append({"profile": profile, "session": sid,
                            "dir": out_dir, "exit": exit_code, "wall": wall})

    print(json.dumps({"batch_trials": len(results),
                      "sessions": [{"profile": r["profile"],
                                    "session": r["session"]}
                                   for r in results]}, indent=1))


if __name__ == "__main__":
    main()
