#!/usr/bin/env python3
"""Freeze intent F-001 into lab.db (idempotent) + register the trial batch.

The Rust CLI generates its own random intent_id, which breaks reproducibility;
the protocol requires a deterministic id for the frozen record, so this script
inserts the exact frozen row directly. Safe to re-run: skips if present.
"""
import json
import sqlite3
import sys

sys.path.insert(0, "/root/agentseolab/runner")
from field import canonical_hash

REC = json.load(open("/root/agentseolab/runs/field/INTENT_F001.json"))
DB = "/root/agentseolab/lab.db"

payload_json = json.dumps({
    "intent_id": REC["intent_id"],
    "intent_hash": REC["intent_hash"],
    "created_at": REC["created_at"],
    "payload": REC["payload"],
}, separators=(",", ":"))

con = sqlite3.connect(DB)
cur = con.cursor()
row = cur.execute("SELECT intent_hash FROM site_intents WHERE intent_id=?",
                  (REC["intent_id"],)).fetchone()
if row:
    if row[0] != REC["intent_hash"]:
        print("FATAL: frozen hash drift on existing intent", file=sys.stderr)
        sys.exit(3)
    print(f"already frozen: {REC['intent_id']} ({REC['intent_hash'][:16]}…)")
else:
    cur.execute(
        """INSERT INTO site_intents
           (intent_id, intent_hash, created_at, purpose, primary_job,
            audiences, capabilities, language, constraints_json,
            prohibited_meanings, desired_tld, desired_length,
            desired_word_rules, payload_json)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (REC["intent_id"], REC["intent_hash"], REC["created_at"],
         REC["payload"]["purpose"], REC["payload"]["primary_job"],
         json.dumps(REC["payload"]["audiences"]),
         json.dumps(REC["payload"]["capabilities"]),
         REC["payload"]["language"],
         json.dumps(REC["payload"]["constraints"]),
         json.dumps(REC["payload"]["prohibited_meanings"]),
         REC["payload"]["desired_tld"], REC["payload"]["desired_length"],
         REC["payload"]["desired_word_rules"], payload_json))
    con.commit()
    print(f"FROZEN: {REC['intent_id']} hash={REC['intent_hash']}")
con.close()
