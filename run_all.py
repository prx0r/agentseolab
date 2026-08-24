
#!/usr/bin/env python3
import json, os, sqlite3, hashlib, uuid, time, re
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
CF_MODEL = "@cf/meta/llama-3.2-3b-instruct"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment.db")

SITE_INTENT = {
    "purpose": "A public service exposing small deterministic APIs and MCP tools.",
    "primary_job": "Discover and execute utilities quickly.",
    "audiences": ["AI agents", "developers"],
    "capabilities": ["QR code generation", "PDF signing", "timezone conversion"],
}

def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(p): return f"{p}_{uuid.uuid4().hex[:12]}"
def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def call_cf(prompt, max_tokens=150):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    data = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read())
            return r.get("result", {}).get("response", "").strip()
    except Exception as e:
        print(f"    API error: {e}")
        return None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS site_intents (intent_id TEXT PRIMARY KEY, intent_hash TEXT, created_at TEXT, purpose TEXT, payload_json TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS experiments (experiment_id TEXT PRIMARY KEY, intent_id TEXT, created_at TEXT, kind TEXT, hypothesis_id TEXT, preregistered INTEGER, payload_json TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pairwise_comparisons (comparison_id TEXT PRIMARY KEY, experiment_id TEXT, candidate_a TEXT, candidate_b TEXT, ordering TEXT, chosen TEXT, abstained INTEGER, agent_model TEXT, provider TEXT, session_id TEXT, timestamp TEXT, response_raw TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS field_trials (trial_id TEXT PRIMARY KEY, intent_id TEXT, agent_model TEXT, provider TEXT, session_id TEXT, started_at TEXT, search_queries_json TEXT, final_action TEXT, task_success INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS hypotheses (hypothesis_id TEXT PRIMARY KEY, statement TEXT, status TEXT, effect_estimate REAL, sample_size INTEGER, model_families_json TEXT, preregistered INTEGER DEFAULT 0)")
    conn.commit()
    return conn

def store_exp(conn, kind, hyp_id=None):
    eid = new_id("experiment")
    iid = conn.execute("SELECT intent_id FROM site_intents LIMIT 1").fetchone()[0]
    conn.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?)", (eid, iid, now_iso(), kind, hyp_id, 1, json.dumps({"model": CF_MODEL})))
    conn.commit()
    return eid

def pair_choice(conn, eid, a, b, prompt):
    resp = call_cf(prompt)
    chosen = None
    if resp:
        for ch in resp:
            if ch.upper() in ("A", "B"):
                chosen = ch.upper()
                break
    if chosen:
        cname = a if chosen == "A" else b
        conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,0,?,?,?,?,?)",
            (new_id("comp"), eid, a, b, chosen, cname, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(), resp))
        conn.commit()
        return cname, resp
    conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,1,?,?,?,?,?)",
        (new_id("comp"), eid, a, b, "AB", None, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(), resp or ""))
    conn.commit()
    return None, resp


# ============================================================
# EXP 1: FIELD TRACE — Agent search behavior
# ============================================================
def exp_field_trace(conn):
    print("\n  [EXP 1] Field Trace")
    print("  " + "-" * 50)
    tasks = [
        "I need a free QR code generator for a URL",
        "I want to sign a PDF document online for free",
        "I need to convert a timezone for a meeting",
    ]
    all_queries = []
    for task in tasks:
        prompt = f"""You need: {task}
What 3 search queries would you try? One per line, numbered."""
        resp = call_cf(prompt, max_tokens=80)
        queries = []
        if resp:
            for line in resp.strip().split("\n"):
                m = re.match(r"^\d+[.) ]\s*(.+)", line.strip())
                if m: queries.append(m.group(1).strip().strip('"'))
        all_queries.extend(queries)
        print(f"  Task: {task[:50]}")
        for q in queries[:3]:
            print(f"    -> {q}")
        time.sleep(0.2)
    iid = conn.execute("SELECT intent_id FROM site_intents LIMIT 1").fetchone()[0]
    conn.execute("INSERT INTO field_trials VALUES (?,?,?,?,?,?,?,?,?)",
        (new_id("trial"), iid, CF_MODEL.split("/")[-1], "cloudflare", new_id("s"), now_iso(),
         json.dumps(all_queries), "search_completed", 1))
    conn.commit()
    print(f"  Stored {len(all_queries)} queries across {len(tasks)} tasks")
    return all_queries

# ============================================================
# EXP 2: SEMANTIC INVERSION — What does this domain do?
# ============================================================
def exp_semantic_inversion(conn):
    print("\n  [EXP 2] Semantic Inversion")
    print("  " + "-" * 50)
    domains = ["tinyget.com", "hound.com", "radar.com", "fig.com", "velko.com", "fetchkit.com"]
    target = ["tool", "api", "qr", "utility", "function", "service", "developer", "agent", "code"]
    eid = store_exp(conn, "semantic_inversion", "H-0002")
    correct = 0
    for d in domains:
        prompt = f"You see domain: {d}\nWhat does this website do? One sentence."
        resp = call_cf(prompt, max_tokens=50)
        hit = any(kw in resp.lower() for kw in target) if resp else False
        if hit: correct += 1
        conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,?, ?,?,?,?,?)",
            (new_id("comp"), eid, d, "CATEGORY", "AB" if hit else "BA",
             d if hit else None, 0 if hit else 1, CF_MODEL.split("/")[-1], "cloudflare",
             new_id("s"), now_iso(), resp))
        print(f"  {d:18} {'HIT' if hit else 'MISS':4} {resp[:60] if resp else '...'}")
        time.sleep(0.2)
    conn.commit()
    rate = correct/len(domains)*100
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0002", "Domains transmit product category without description", "provisional",
         rate/100, len(domains), json.dumps(["llama"]), 1))
    conn.commit()
    print(f"  Transmission rate: {correct}/{len(domains)} = {rate:.0f}%")
    return rate

# ============================================================
# EXP 3: NAMING-FAMILY TOURNAMENT — All families head-to-head
# ============================================================
def exp_naming_tournament(conn):
    print("\n  [EXP 3] Naming-Family Tournament")
    print("  " + "-" * 50)
    candidates = {
        "descriptive": "domainchecker.com",
        "action_object": "getpdf.com",
        "suggestive": "tinyget.com",
        "animal": "hound.com",
        "tool_object": "radar.com",
        "nature": "fig.com",
        "motion": "fetch.com",
        "invented": "velko.com",
    }
    families = list(candidates.keys())
    pairs = list(combinations(families, 2))
    wins = {f: 0 for f in families}
    valid = 0
    eid = store_exp(conn, "naming_tournament", "H-0003")
    print(f"  {len(families)} families, {len(pairs)} pairs")
    for fa, fb in pairs:
        a, b = candidates[fa], candidates[fb]
        prompt = f"Which brand works best for small utility APIs?\nA: {a}\nB: {b}\nLetter only."
        cname, _ = pair_choice(conn, eid, a, b, prompt)
        if cname:
            winner_fam = fa if cname == a else fb
            wins[winner_fam] += 1
            valid += 1
            print(f"  {fa:15} vs {fb:15} -> {winner_fam}")
        time.sleep(0.2)
    print(f"\n  Leaderboard:")
    for f in sorted(wins, key=wins.get, reverse=True):
        bar = "#" * wins[f]
        print(f"    {f:18} {wins[f]:>2} {bar}")
    top = max(wins, key=wins.get)
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0003", f"Best naming family is {top}", "preliminary", wins[top]/valid if valid else 0,
         valid, json.dumps(["llama"]), 1))
    conn.commit()
    return wins

# ============================================================
# EXP 4: ARCHETYPE MAPPING — Semantic vectors for words
# ============================================================
def exp_archetype_mapping(conn):
    print("\n  [EXP 4] Archetype Mapping")
    print("  " + "-" * 50)
    words = ["hound", "radar", "fig", "ant", "cloud", "fetch"]
    dims = ["tracking", "speed", "precision", "search", "small", "power", "friendliness"]
    eid = store_exp(conn, "archetype_mapping", "H-0004")
    vectors = {}
    for w in words:
        prompt = f"""Rate the word "{w}" on these dimensions (0.0 to 1.0):
{", ".join(dims)}
Respond as CSV values only, no labels."""
        resp = call_cf(prompt, max_tokens=40)
        vals = []
        if resp:
            nums = re.findall(r"\d+\.?\d*", resp)
            vals = [float(n) for n in nums[:len(dims)]]
        while len(vals) < len(dims):
            vals.append(0.0)
        vectors[w] = dict(zip(dims, vals))
        print(f"  {w:10} {dict(zip(dims, [f'{v:.1f}' for v in vals[:5]]))}")
        time.sleep(0.2)
    # Intent fit: "find information on the web" -> which word matches best?
    intent = "find information on the web"
    scores = {}
    for w, vec in vectors.items():
        # Simple: average of tracking + search + speed
        fit = (vec.get("tracking", 0) + vec.get("search", 0) + vec.get("speed", 0)) / 3
        scores[w] = fit
    best = max(scores, key=scores.get)
    print(f"\n  Intent fit for '{intent}':")
    for w in sorted(scores, key=scores.get, reverse=True):
        print(f"    {w:10} fit={scores[w]:.2f}")
    print(f"  Best match: {best}")
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0004", f"Archetype {best} best fits 'find information' intent", "preliminary",
         scores[best], len(scores), json.dumps(["llama"]), 1))
    conn.commit()
    return vectors

# ============================================================
# EXP 5: MEMORY — Free recall after one exposure
# ============================================================
def exp_memory(conn):
    print("\n  [EXP 5] Memory — Recall after one exposure")
    print("  " + "-" * 50)
    domains = ["tinyget.com", "radar.com", "velko.com", "fetchkit.com", "hound.com"]
    eid = store_exp(conn, "memory_recall", "H-0005")
    recall_results = {}
    # Show all domains once
    exposure = "Here are 5 websites: " + ", ".join(domains)
    print(f"  Exposure: {exposure[:60]}...")
    # Then ask to recall
    prompt = f"""I just told you about these websites: {", ".join(domains)}
Without looking, list as many as you can remember. One per line."""
    resp = call_cf(prompt, max_tokens=100)
    recalled = []
    if resp:
        for line in resp.strip().split("\n"):
            line = line.strip().strip("- ").strip("* ").strip()
            for d in domains:
                if d.split(".")[0].lower() in line.lower():
                    recalled.append(d)
    recalled = list(dict.fromkeys(recalled))  # dedupe preserving order
    print(f"  Recalled: {len(recalled)}/{len(domains)}")
    for d in domains:
        hit = d in recalled
        recall_results[d] = hit
        print(f"    {d:18} {'RECALL' if hit else 'FORGOT'}")
    rate = len(recalled)/len(domains)*100
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0005", "Concrete words recalled better than invented names", "preliminary",
         rate/100, len(domains), json.dumps(["llama"]), 1))
    conn.commit()
    return recall_results

# ============================================================
# EXP 6: EXPOSURE CURVE — Preference change with repetition
# ============================================================
def exp_exposure_curve(conn):
    print("\n  [EXP 6] Exposure Curve")
    print("  " + "-" * 50)
    # First exposure: ask cold
    # Then "repeated exposure": describe the brand, ask again
    pairs = [("tinyget.com", "velko.com"), ("radar.com", "fig.com")]
    eid = store_exp(conn, "exposure_curve", "H-0006")
    results = {"cold": {}, "warm": {}}
    for phase in ["cold", "warm"]:
        print(f"  Phase: {phase}")
        for a, b in pairs:
            if phase == "warm":
                prompt = f"""tinyget.com is a popular developer utility platform with QR codes, PDF tools, and APIs.
radar.com is a monitoring service for tracking website uptime.
fig.com is a fruit-themed design studio.

Which brand works best for small utility APIs?
A: {a}  B: {b}
Letter only."""
            else:
                prompt = f"Which domain works better as a brand?\nA: {a}\nB: {b}\nLetter only."
            cname, _ = pair_choice(conn, eid, a, b, prompt)
            if cname:
                key = f"{a}_vs_{b}"
                results[phase][key] = cname
                print(f"    {a} vs {b} -> {cname}")
            time.sleep(0.2)
    # Check if preference shifted
    shift = 0
    for key in results["cold"]:
        if results["cold"].get(key) != results["warm"].get(key):
            shift += 1
    print(f"  Preference shifts after context: {shift}/{len(pairs)}")
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0006", "Brand context changes preference for invented names", "preliminary",
         shift/len(pairs) if pairs else 0, len(pairs)*2, json.dumps(["llama"]), 1))
    conn.commit()
    return results

# ============================================================
# EXP 7: PROCESSING FLUENCY — Spell-after-hear
# ============================================================
def exp_fluency(conn):
    print("\n  [EXP 7] Processing Fluency — Spell after hearing")
    print("  " + "-" * 50)
    domains = ["tinyget.com", "velko.com", "fetchkit.com", "apicandy.com", "toolopus.com"]
    eid = store_exp(conn, "fluency", "H-0007")
    correct = 0
    for d in domains:
        word = d.split(".")[0]
        prompt = f"""I just heard a website name that sounds like: "{word}"
Please spell the domain name you think I mean. Just the domain."""
        resp = call_cf(prompt, max_tokens=30)
        hit = word.lower() in (resp or "").lower()
        if hit: correct += 1
        conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,?, ?,?,?,?,?)",
            (new_id("comp"), eid, d, "SPELLING", "AB" if hit else "BA",
             d if hit else None, 0 if hit else 1, CF_MODEL.split("/")[-1], "cloudflare",
             new_id("s"), now_iso(), resp))
        print(f"  {word:15} expected={word:15} got={resp[:20] if resp else '...':20} {'OK' if hit else 'FAIL'}")
        time.sleep(0.2)
    conn.commit()
    rate = correct/len(domains)*100
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0007", "Suggestive names spelled correctly more often than invented names", "preliminary",
         rate/100, len(domains), json.dumps(["llama"]), 1))
    conn.commit()
    print(f"  Spelling accuracy: {correct}/{len(domains)} = {rate:.0f}%")
    return rate

# ============================================================
# EXP 8: SOUND SYMBOLISM — Phonosemantic vectors
# ============================================================
def exp_sound_symbolism(conn):
    print("\n  [EXP 8] Sound Symbolism — Phonosemantic vectors")
    print("  " + "-" * 50)
    words = ["tinyget", "velko", "radar", "hound", "fig"]
    dims = ["small", "fast", "heavy", "soft", "sharp", "friendly"]
    eid = store_exp(conn, "sound_symbolism", "H-0008")
    vectors = {}
    for w in words:
        prompt = f"""Based purely on the SOUND of the word "{w}" (not its meaning), rate:
small(0-1), fast(0-1), heavy(0-1), soft(0-1), sharp(0-1), friendly(0-1)
CSV values only."""
        resp = call_cf(prompt, max_tokens=40)
        vals = []
        if resp:
            nums = re.findall(r"\d+\.?\d*", resp)
            vals = [float(n) for n in nums[:6]]
        while len(vals) < 6: vals.append(0.5)
        vectors[w] = dict(zip(dims, vals))
        print(f"  {w:10} {dict(zip(dims, [f'{v:.1f}' for v in vals]))}")
        time.sleep(0.2)
    # Which sounds "small and fast"? (ideal for a tiny utility)
    scores = {}
    for w, vec in vectors.items():
        scores[w] = (vec.get("small", 0) + vec.get("fast", 0) + vec.get("friendly", 0)) / 3
    best = max(scores, key=scores.get)
    print(f"\n  Best 'small+fast+friendly' sound: {best} (score={scores[best]:.2f})")
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0008", f"Sound symbolism: {best} sounds most like a small fast utility", "preliminary",
         scores[best], len(scores), json.dumps(["llama"]), 1))
    conn.commit()
    return vectors

# ============================================================
# EXP 9: PURE DOMAIN CAUSAL — Same description, different domain
# ============================================================
def exp_domain_causal(conn):
    print("\n  [EXP 9] Pure Domain Causal — Identical descriptions")
    print("  " + "-" * 50)
    desc = "Small callable utilities for agents and developers."
    pairs = [("tinyget.com", "velko.com"), ("radar.com", "fig.com"), ("hound.com", "fetchkit.com")]
    eid = store_exp(conn, "domain_causal", "H-0009")
    wins = {}
    for a, b in pairs:
        for left, right in [(a, b), (b, a)]:
            prompt = f"""Task: Find a service exposing small APIs.

A: {left}
{desc}

B: {right}
{desc}

Which would you choose? Letter only."""
            cname, _ = pair_choice(conn, eid, a, b, prompt)
            if cname:
                wins[cname] = wins.get(cname, 0) + 1
                print(f"  {left:15} vs {right:15} -> {cname}")
            time.sleep(0.2)
    print(f"\n  Domain causal wins:")
    for d in sorted(wins, key=wins.get, reverse=True):
        print(f"    {d:18} {wins[d]}")
    top = max(wins, key=wins.get) if wins else "?"
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?,?)",
        ("H-0009", f"Hostname alone shifts selection; {top} wins", "preliminary",
         wins.get(top, 0)/sum(wins.values()) if wins else 0, sum(wins.values()),
         json.dumps(["llama"]), 1))
    conn.commit()
    return wins

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  AgentSEOLab — Full Experiment Suite (9 types)")
    print("=" * 60)

    conn = init_db()

    # Capture intent if not exists
    if not conn.execute("SELECT intent_id FROM site_intents LIMIT 1").fetchone():
        h = canonical_hash(SITE_INTENT)
        iid = new_id("intent")
        conn.execute("INSERT INTO site_intents VALUES (?,?,?,?,?)",
            (iid, h, now_iso(), SITE_INTENT["purpose"], json.dumps(SITE_INTENT)))
        conn.commit()
        print(f"\n  Intent frozen: {iid}")

    results = {}
    results["field_trace"] = exp_field_trace(conn)
    results["semantic_inversion"] = exp_semantic_inversion(conn)
    results["naming_tournament"] = exp_naming_tournament(conn)
    results["archetype_mapping"] = exp_archetype_mapping(conn)
    results["memory"] = exp_memory(conn)
    results["exposure_curve"] = exp_exposure_curve(conn)
    results["fluency"] = exp_fluency(conn)
    results["sound_symbolism"] = exp_sound_symbolism(conn)
    results["domain_causal"] = exp_domain_causal(conn)

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
        print(f"  {t[0]:30} {n:>5} rows")
    hyps = conn.execute("SELECT hypothesis_id, statement, status, effect_estimate FROM hypotheses").fetchall()
    print(f"\n  Hypotheses stored: {len(hyps)}")
    for h in hyps:
        print(f"    {h[0]:12} [{h[2]:12}] {h[1][:60]}")
    print("\n" + "=" * 60)
    conn.close()

if __name__ == "__main__":
    main()
