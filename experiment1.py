#!/usr/bin/env python3
"""
AgentSEOLab Experiment 1: Hostname Pairwise Preference
======================================================
Following SCIENTIFIC_METHOD.md exactly:
1. Freeze immutable SiteIntent BEFORE candidate generation
2. Run pairwise comparisons with Cloudflare free models
3. Record raw comparisons (never throw away data)
4. Generate structured report
"""

import json
import os
import sqlite3
import hashlib
import uuid
import time
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
CF_MODEL = "@cf/meta/llama-3.2-3b-instruct"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment.db")

SITE_INTENT = {
    "purpose": "A public service exposing small deterministic APIs and MCP tools that agents and developers can invoke with minimal friction.",
    "primary_job": "When an agent needs a small capability, discover and execute the correct utility quickly.",
    "audiences": ["autonomous AI agents", "developers"],
    "capabilities": ["QR code generation", "PDF signing", "timezone conversion", "file compression", "calendar file creation"],
    "constraints": {"tld": ".com", "max_chars_preferred": 12, "avoid_hyphens": True, "avoid_numbers": True, "zero_prior_brand_awareness": True},
    "language": "en",
    "prohibited_meanings": ["adult content", "gambling", "violence"]
}

CANDIDATES = [
    {"name": "tinyget.com", "family": "suggestive_compound", "rationale": "tiny=small utility, get=retrieve/invoke"},
    {"name": "oneutil.com", "family": "action_object", "rationale": "one=single purpose, util=utility"},
    {"name": "toolopus.com", "family": "animal_metaphor", "rationale": "opus=productive (octopus), tool=explicit category"},
    {"name": "fetchkit.com", "family": "motion_object", "rationale": "fetch=action, kit=tool collection"},
    {"name": "quickfn.com", "family": "suggestive_compound", "rationale": "quick=speed, fn=function"},
    {"name": "apicandy.com", "family": "metaphorical", "rationale": "API=explicit, candy=delightful/easy"},
]

PROMPT_TEMPLATE = """You are choosing a domain name for a new product.

PRODUCT DESCRIPTION:
{purpose}

The product offers these tools: {capabilities}

Choose ONE domain name that would work BEST for this product. Consider:
- Which name makes the product purpose clearest?
- Which name would you remember and visit?
- Which name feels most professional?

Option A: {a}
Option B: {b}

Respond with ONLY the letter (A or B). Nothing else."""


def now_iso():
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def call_cf(prompt, max_tokens=10):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    data = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read())
            return r.get("result", {}).get("response", "").strip()
    except Exception as e:
        print(f"  WARN: {e}")
        return None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS site_intents (intent_id TEXT PRIMARY KEY, intent_hash TEXT NOT NULL, created_at TEXT NOT NULL, purpose TEXT NOT NULL, payload_json TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS experiments (experiment_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL, created_at TEXT NOT NULL, kind TEXT NOT NULL, hypothesis_id TEXT, preregistered INTEGER DEFAULT 0, payload_json TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS pairwise_comparisons (comparison_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL, candidate_a TEXT NOT NULL, candidate_b TEXT NOT NULL, ordering TEXT NOT NULL, chosen TEXT, abstained INTEGER DEFAULT 0, agent_model TEXT NOT NULL, provider TEXT NOT NULL, session_id TEXT NOT NULL, timestamp TEXT NOT NULL, response_raw TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS hypotheses (hypothesis_id TEXT PRIMARY KEY, statement TEXT NOT NULL, status TEXT NOT NULL, effect_estimate REAL, sample_size INTEGER NOT NULL, model_families_json TEXT NOT NULL, preregistered INTEGER DEFAULT 0)")
    conn.commit()
    return conn

def capture_intent(conn):
    h = canonical_hash(SITE_INTENT)
    iid = new_id("intent")
    conn.execute("INSERT INTO site_intents VALUES (?,?,?,?,?)", (iid, h, now_iso(), SITE_INTENT["purpose"], json.dumps(SITE_INTENT)))
    conn.commit()
    print(f"\n  Intent frozen: {iid}")
    print(f"  Hash: {h[:16]}...")
    return iid

def run_experiment(conn, iid):
    eid = new_id("experiment")
    conn.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?)", (eid, iid, now_iso(), "hostname_only_pairwise", "H-0001", 1, json.dumps({"candidates": [c["name"] for c in CANDIDATES], "model": CF_MODEL})))
    conn.commit()

    pairs = list(combinations(range(len(CANDIDATES)), 2))
    total = len(pairs) * 2
    print(f"\n  Experiment: {eid}")
    print(f"  {len(CANDIDATES)} candidates, {len(pairs)} pairs x 2 orderings = {total} comparisons\n")

    valid = 0
    abstained = 0
    wins = {}

    for idx, (i, j) in enumerate(pairs):
        ca, cb = CANDIDATES[i], CANDIDATES[j]
        for ordering in ["AB", "BA"]:
            left, right = (ca, cb) if ordering == "AB" else (cb, ca)
            prompt = PROMPT_TEMPLATE.format(purpose=SITE_INTENT["purpose"], capabilities=", ".join(SITE_INTENT["capabilities"]), a=left["name"], b=right["name"])

            n = valid + abstained + 1
            print(f"  [{n}/{total}] {left['name']:15} vs {right['name']:15} ({ordering})...", end=" ", flush=True)

            resp = call_cf(prompt)
            chosen = None
            if resp:
                for ch in resp:
                    if ch.upper() in ("A", "B"):
                        chosen = ch.upper()
                        break

            if chosen:
                cname = left["name"] if chosen == "A" else right["name"]
                conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,0,?,?,?,?,?)",
                    (new_id("comp"), eid, ca["name"], cb["name"], ordering, cname, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(), resp))
                wins[cname] = wins.get(cname, 0) + 1
                valid += 1
                print(f"-> {cname}")
            else:
                abstained += 1
                conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,1,?,?,?,?,?)",
                    (new_id("comp"), eid, ca["name"], cb["name"], ordering, None, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(), resp or ""))
                print(f"-> ABSTAIN")

            conn.commit()
            time.sleep(0.2)

    return eid, valid, abstained, wins

def report(conn, eid, valid, abstained, wins):
    total = valid + abstained
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT REPORT")
    print(f"{'='*60}")
    print(f"  Experiment:  {eid}")
    print(f"  Hypothesis:  H-0001 (suggestive compounds preferred)")
    print(f"  Model:       {CF_MODEL}")
    print(f"  Total:       {total} comparisons")
    print(f"  Valid:       {valid} ({valid/total*100:.0f}% response rate)")
    print(f"  Abstained:   {abstained}")
    print(f"\n  {'Candidate':<18} {'Wins':>5} {'%':>6}")
    print(f"  {'-'*32}")
    for c in sorted(wins, key=wins.get, reverse=True):
        pct = wins[c]/valid*100 if valid else 0
        bar = "#" * int(pct/3)
        print(f"  {c:<18} {wins[c]:>5} {pct:>5.0f}% {bar}")

    top = max(wins, key=wins.get) if wins else None
    effect = wins.get(top, 0) / valid if valid else 0
    status = "provisional" if valid >= 10 else "preliminary"
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,1)", ("H-0001", "Suggestive compound names preferred over descriptive for agent-facing tools", status, effect, valid, json.dumps(["llama"])))
    conn.commit()
    print(f"\n  Hypothesis H-0001: {status}")
    print(f"  Effect: {effect:.1%} (top candidate win rate)")
    print(f"  {'='*60}")

def main():
    print(f"{'='*60}")
    print(f"  AgentSEOLab - Experiment 1: Hostname Pairwise Preference")
    print(f"{'='*60}")

    conn = init_db()
    iid = capture_intent(conn)
    eid, valid, abstained, wins = run_experiment(conn, iid)
    report(conn, eid, valid, abstained, wins)
    conn.close()
    print(f"\n  Saved to: {DB_PATH}\n")

if __name__ == "__main__":
    main()
