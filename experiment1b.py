#!/usr/bin/env python3
"""Experiment 1b: Cross-validate with Llama 3.3 70B"""
import json, os, sqlite3, hashlib, uuid, time
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
CF_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment.db")

SITE_INTENT = {
    "purpose": "A public service exposing small deterministic APIs and MCP tools that agents and developers can invoke with minimal friction.",
    "primary_job": "When an agent needs a small capability, discover and execute the correct utility quickly.",
    "audiences": ["autonomous AI agents", "developers"],
    "capabilities": ["QR code generation", "PDF signing", "timezone conversion", "file compression", "calendar file creation"],
    "constraints": {"tld": ".com", "max_chars_preferred": 12, "avoid_hyphens": True, "avoid_numbers": True},
    "language": "en",
}

CANDIDATES = [
    {"name": "tinyget.com", "family": "suggestive_compound"},
    {"name": "oneutil.com", "family": "action_object"},
    {"name": "toolopus.com", "family": "animal_metaphor"},
    {"name": "fetchkit.com", "family": "motion_object"},
    {"name": "quickfn.com", "family": "suggestive_compound"},
    {"name": "apicandy.com", "family": "metaphorical"},
]

PROMPT = """You are choosing a domain name for a new product.

PRODUCT: {purpose}
TOOLS: {capabilities}

Choose ONE name that works BEST. Consider clarity, memorability, professionalism.

Option A: {a}
Option B: {b}

Respond with ONLY the letter (A or B)."""

def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(p): return f"{p}_{uuid.uuid4().hex[:12]}"

def call_cf(prompt):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    data = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": 10}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read())
            return r.get("result", {}).get("response", "").strip()
    except Exception as e:
        print(f"  WARN: {e}")
        return None

conn = sqlite3.connect(DB_PATH)
iid = conn.execute("SELECT intent_id FROM site_intents LIMIT 1").fetchone()[0]

eid = new_id("experiment")
conn.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?)", (eid, iid, now_iso(), "hostname_only_pairwise", "H-0001", 1, json.dumps({"model": CF_MODEL, "phase": "cross-validation"})))
conn.commit()

pairs = list(combinations(range(len(CANDIDATES)), 2))
total = len(pairs) * 2
wins = {}
valid = 0

print(f"Cross-validation with {CF_MODEL}")
print(f"{total} comparisons\n")

for i, j in pairs:
    ca, cb = CANDIDATES[i], CANDIDATES[j]
    for ordering in ["AB", "BA"]:
        left, right = (ca, cb) if ordering == "AB" else (cb, ca)
        prompt = PROMPT.format(purpose=SITE_INTENT["purpose"], capabilities=", ".join(SITE_INTENT["capabilities"]), a=left["name"], b=right["name"])
        n = valid + 1
        print(f"  [{n}/{total}] {left['name']:15} vs {right['name']:15}...", end=" ", flush=True)
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
            conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,1,?,?,?,?,?)",
                (new_id("comp"), eid, ca["name"], cb["name"], ordering, None, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(), resp or ""))
            print("-> ABSTAIN")
        conn.commit()
        time.sleep(0.2)

print(f"\n{'='*50}")
print(f"CROSS-VALIDATION RESULTS ({CF_MODEL})")
print(f"{'='*50}")
print(f"Valid: {valid}/{total}")
for c in sorted(wins, key=wins.get, reverse=True):
    pct = wins[c]/valid*100 if valid else 0
    print(f"  {c:<18} {wins[c]:>3} ({pct:.0f}%)")

# Compare with Llama 3.2 results
print(f"\nComparison with Llama 3.2 3B:")
llama32 = dict(conn.execute("SELECT chosen, COUNT(*) FROM pairwise_comparisons WHERE agent_model='llama-3.2-3b-instruct' AND chosen IS NOT NULL GROUP BY chosen").fetchall())
llama70 = dict(conn.execute("SELECT chosen, COUNT(*) FROM pairwise_comparisons WHERE agent_model='llama-3.3-70b-instruct-fp8-fast' AND chosen IS NOT NULL GROUP BY chosen").fetchall())
for c in sorted(set(list(llama32.keys()) + list(llama70.keys()))):
    w32 = llama32.get(c, 0)
    w70 = llama70.get(c, 0)
    print(f"  {c:<18} 3B: {w32:>2}  70B: {w70:>2}")

conn.close()
print(f"\nDone. Saved to {DB_PATH}")
