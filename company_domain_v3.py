#!/usr/bin/env python3
import json, os, sqlite3, hashlib, uuid, time, re, math, random
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_domain_v3.db")

MODELS = [
    ("@cf/meta/llama-3.2-1b-instruct", "llama-1b"),
    ("@cf/google/gemma-2b-it-lora", "gemma-2b"),
    ("@cf/meta/llama-3.2-3b-instruct", "llama-3b"),
    ("@cf/mistral/mistral-7b-instruct-v0.2-lora", "mistral-7b"),
    ("@cf/meta/llama-3.1-8b-instruct-fp8", "llama-8b"),
]

def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(p): return f"{p}_{uuid.uuid4().hex[:12]}"

def call_cf(model, prompt, max_tokens=200):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model}"
    data = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            r = json.loads(resp.read())
            rt = r.get("result", {}).get("response", "")
            return str(rt).strip() if rt else ""
    except Exception as e:
        print(f"    API err: {e}")
        return None

def check_single(domain):
    """Direct RDAP check (authoritative, no rate limits)."""
    try:
        resp = urllib.request.urlopen(f"https://rdap.verisign.com/com/v1/domain/{domain}", timeout=10)
        data = json.loads(resp.read())
        status = data.get("status", ["unknown"])
        return "TAKEN" if status and status[0] != "unknown" else "UNKNOWN"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "AVAILABLE"
        return "UNKNOWN"
    except:
        return "UNKNOWN"

def batch_check(domains):
    """Direct RDAP checks."""
    results = []
    for d in domains:
        status = check_single(d)
        results.append({"domain": d, "status": status})
        time.sleep(0.1)
    return results

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for table in [
        "CREATE TABLE IF NOT EXISTS hypotheses (id TEXT PRIMARY KEY, statement TEXT, status TEXT, preregistered INTEGER, created_at TEXT)",
        "CREATE TABLE IF NOT EXISTS site_intents (intent_id TEXT PRIMARY KEY, hash TEXT, purpose TEXT, created_at TEXT)",
        "CREATE TABLE IF NOT EXISTS candidates (domain TEXT PRIMARY KEY, family TEXT, length INTEGER, available INTEGER, source TEXT)",
        "CREATE TABLE IF NOT EXISTS field_traces (id TEXT PRIMARY KEY, model TEXT, task TEXT, queries_json TEXT, chosen_domain TEXT, timestamp TEXT)",
        "CREATE TABLE IF NOT EXISTS pairwise_v3 (id TEXT PRIMARY KEY, model TEXT, experiment TEXT, a TEXT, b TEXT, len_a INTEGER, len_b INTEGER, ordering TEXT, chosen TEXT, first_chosen INTEGER, timestamp TEXT, raw TEXT)",
        "CREATE TABLE IF NOT EXISTS semantic_inv (id TEXT PRIMARY KEY, model TEXT, domain TEXT, prediction TEXT, correct INTEGER, timestamp TEXT)",
        "CREATE TABLE IF NOT EXISTS cross_model (id TEXT PRIMARY KEY, pair TEXT, model TEXT, chosen TEXT, timestamp TEXT)",
    ]:
        c.execute(table)
    conn.commit()
    return conn

# ============================================================
# STEP 1: Frozen Intent
# ============================================================
def step1_intent(conn):
    print("\n  STEP 1: Freeze SiteIntent")
    print("  " + "=" * 55)
    intent = {
        "purpose": "A service providing verified machine-readable facts to AI agents. Not reasoning - observations, proofs, decisions.",
        "primary_job": "Agent needs a verified fact. Can figure it out (expensive) or call this (cheap, proven).",
        "audiences": ["AI agents", "developers", "MCP integrators"],
        "capabilities": ["email verification", "DNS validation", "API health", "package safety", "OAuth validation"],
        "constraints": {"tld": ".com", "max_length": 12}
    }
    h = hashlib.sha256(json.dumps(intent, sort_keys=True).encode()).hexdigest()
    iid = new_id("intent")
    conn.execute("INSERT INTO site_intents VALUES (?,?,?,?)", (iid, h, intent["purpose"], now_iso()))
    conn.commit()
    print(f"  Frozen: {iid}, hash: {h[:16]}...")
    return iid, intent

# ============================================================
# STEP 2: Generate + filter available
# ============================================================
def step2_generate(conn):
    print("\n  STEP 2: Generate candidates + availability filter")
    print("  " + "=" * 55)

    gen_model = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    prompts = [
        "Give me 10 short .com domain names for a service that provides verified machine-readable facts to AI agents. Names only, one per line.",
        "I need 10 short .com domains for a $0.003 API that answers verified questions. Names only.",
        "What 10 .com domains would an AI agent search for when it needs trusted real-world facts? Names only.",
        "Generate 10 domain names for a vending machine for verified reality. Short, .com. Names only.",
    ]

    generated = set()
    for p in prompts:
        resp = call_cf(gen_model, p, max_tokens=200)
        if resp:
            for line in resp.strip().split("\n"):
                line = line.strip().strip("- ").strip("* ").strip("0123456789. ")
                for word in re.findall(r'[a-zA-Z]{2,14}', line):
                    skip = ("com","the","and","for","that","this","name","domain","give","need","what","think","short","line")
                    if word.lower() not in skip:
                        generated.add(word.lower() + ".com")
        time.sleep(0.3)

    hand_picked = [
        "invoketruth.com","factcall.com","vericall.com","checkproof.com","realcheck.com",
        "truthping.com","onestatus.com","calledit.com","trustcall.com","simpleproof.com",
        "evidenceapi.com","verinet.com","centifacts.com","truthvend.com","verifiedbits.com",
        "getproof.com","trucall.com","proofcall.com","factproof.com","callproof.com",
        "truthcheck.com","verifycall.com","factshot.com","checkcall.com",
    ]

    all_domains = list(set(list(generated) + hand_picked))
    all_domains = [d for d in all_domains if 4 <= len(d.split(".")[0]) <= 14]
    print(f"  Generated: {len(generated)}, Hand-picked: {len(hand_picked)}, Total: {len(all_domains)}")

    # Batch availability via domainnamechecker
    print("  Checking availability (domainnamechecker v4 batch API)...")
    results = batch_check(all_domains)
    available = []
    for r in results:
        d = r.get("domain", "")
        status = r.get("status", "UNKNOWN")
        is_avail = status == "AVAILABLE"
        length = len(d.split(".")[0])
        source = "generated" if d in generated else "hand_picked"
        conn.execute("INSERT OR REPLACE INTO candidates VALUES (?,?,?,?,?)",
            (d, source, length, 1 if is_avail else 0, "cf_registry"))
        if is_avail:
            available.append({"domain": d, "length": length, "family": source})
            print(f"    {d:22} AVAILABLE (len={length})")
    conn.commit()
    print(f"  Available: {len(available)}/{len(results)}")
    return available

# ============================================================
# STEP 3: Field traces - observe ACTUAL search behavior
# (NOT hypothetical "which would you call")
# ============================================================
def step3_field_traces(conn, available, models):
    print("\n  STEP 3: Field Traces (actual search behavior)")
    print("  " + "=" * 55)
    print("  Methodology: Give agent a task, record what it searches for")
    print("  (SCIENTIFIC_METHOD.md section 3 + FIELD_TRACE_SPEC.md)")

    tasks = [
        "I need to verify if an email address is deliverable before sending a campaign.",
        "I want to check if my API endpoint is healthy and responding correctly.",
        "I need to validate that a domain's DNS is properly configured.",
        "I want to know if a software package is safe to install.",
        "I need to check if an OAuth endpoint is working correctly.",
    ]

    all_queries = []
    for model_id, model_name in models[:3]:
        print(f"\n  Model: {model_name}")
        for task in tasks:
            prompt = f"""You are an AI agent. Task: {task}

What search queries would you issue to find a service that does this? List 3 queries, one per line, numbered."""
            resp = call_cf(model_id, prompt, max_tokens=100)
            queries = []
            if resp:
                for line in resp.strip().split("\n"):
                    m = re.match(r"^\d+[.) ]\s*(.+)", line.strip())
                    if m:
                        q = m.group(1).strip().strip('"')
                        queries.append(q)
                        all_queries.append(q)
            conn.execute("INSERT INTO field_traces VALUES (?,?,?,?,?,?)",
                (new_id("trace"), model_name, task, json.dumps(queries), None, now_iso()))
            print(f"    Task: {task[:50]}...")
            for q in queries[:3]:
                print(f"      -> {q}")
            time.sleep(0.2)
    conn.commit()

    # Analyze query vocabulary
    word_freq = {}
    for q in all_queries:
        for word in q.lower().split():
            word = re.sub(r'[^a-z]', '', word)
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

    print("\n  Query vocabulary (top 15 words agents actually search):")
    for word, count in sorted(word_freq.items(), key=lambda x: -x[1])[:15]:
        bar = "#" * count
        print(f"    {word:18} {count:>3} {bar}")

    return all_queries

# ============================================================
# STEP 4: Pairwise tournament (all 5 models, position bias, length control)
# ============================================================
def step4_tournament(conn, available, models):
    print("\n  STEP 4: Pairwise Tournament (5 models, position bias measured)")
    print("  " + "=" * 55)

    # Only test available domains
    domains = [d["domain"] for d in available]
    if len(domains) < 3:
        print("  Not enough available domains for tournament")
        return {}

    pairs = list(combinations(domains, 2))
    wins = {d: 0 for d in domains}
    total_valid = 0
    position_wins = 0
    position_total = 0

    # Use 3 models for tournament (5 would be too many API calls)
    for model_id, model_name in models[:3]:
        print(f"\n  Model: {model_name} ({len(pairs)} pairs)")
        model_wins = {d: 0 for d in domains}
        for a, b in pairs:
            # Randomize order
            if random.random() < 0.5:
                left, right = a, b
                ordering = "AB"
            else:
                left, right = b, a
                ordering = "BA"

            a_len = len(left.split(".")[0])
            b_len = len(right.split(".")[0])

            prompt = f"""You are an AI agent needing verified real-world facts.

Service A: {left}
Service B: {right}

Which would you TRUST more? Letter only."""
            resp = call_cf(model_id, prompt, max_tokens=10)
            chosen = None
            if resp:
                for ch in resp:
                    if ch.upper() in ("A", "B"):
                        chosen = ch.upper()
                        break

            if chosen:
                cname = left if chosen == "A" else right
                first = 1 if ((chosen == "AB" and ordering == "AB") or (chosen == "BA" and ordering == "BA")) else 0
                conn.execute("INSERT INTO pairwise_v3 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_id("p"), model_name, "tournament", a, b, a_len, b_len, ordering, cname, first, now_iso(), resp))
                wins[cname] = wins.get(cname, 0) + 1
                model_wins[cname] = model_wins.get(cname, 0) + 1
                total_valid += 1
                position_wins += first
                position_total += 1
            else:
                conn.execute("INSERT INTO pairwise_v3 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_id("p"), model_name, "tournament", a, b, a_len, b_len, ordering, None, 0, now_iso(), resp or ""))
            time.sleep(0.15)
        conn.commit()

        print(f"    Top 3: ", end="")
        for d in sorted(model_wins, key=model_wins.get, reverse=True)[:3]:
            print(f"{d}({model_wins[d]}) ", end="")
        print()

    pos_rate = position_wins / position_total * 100 if position_total else 0
    print(f"\n  Position bias: {pos_rate:.0f}% first-position wins (50% = ideal)")
    print(f"  Total comparisons: {total_valid}")
    print(f"\n  Overall leaderboard:")
    for d in sorted(wins, key=wins.get, reverse=True):
        bar = "#" * wins[d]
        print(f"    {d:22} {wins[d]:>3} {bar}")

    return wins

# ============================================================
# STEP 5: Semantic inversion (what do agents predict?)
# ============================================================
def step5_semantic(conn, available, models):
    print("\n  STEP 5: Semantic Inversion (what does the name suggest?)")
    print("  " + "=" * 55)

    target = ["verify","proof","evidence","fact","check","truth","reliable","trust","answer","confirm","real"]
    domains = [d["domain"] for d in available]

    for model_id, model_name in models[:3]:
        print(f"\n  Model: {model_name}")
        correct = 0
        for d in domains:
            prompt = f"You see domain: {d}\nWhat does this website do? One sentence."
            resp = call_cf(model_id, prompt, max_tokens=50)
            hits = sum(1 for kw in target if kw in (resp or "").lower())
            is_correct = hits >= 2
            if is_correct: correct += 1
            conn.execute("INSERT INTO semantic_inv VALUES (?,?,?,?,?,?)",
                (new_id("si"), model_name, d, resp[:200] if resp else "", 1 if is_correct else 0, now_iso()))
            tag = "HIT" if is_correct else "MISS"
            print(f"    {d:22} [{tag}] {resp[:55] if resp else '...'}")
            time.sleep(0.2)
        conn.commit()
        rate = correct / len(domains) * 100 if domains else 0
        print(f"    Transmission rate: {correct}/{len(domains)} = {rate:.0f}%")

# ============================================================
# STEP 6: Cross-model consistency
# ============================================================
def step6_cross_model(conn, available, models):
    print("\n  STEP 6: Cross-Model Consistency")
    print("  " + "=" * 55)

    domains = [d["domain"] for d in available]
    if len(domains) < 3:
        return

    pairs = list(combinations(domains[:5], 2))[:8]

    for model_id, model_name in models[:3]:
        for a, b in pairs:
            prompt = f"Which domain for verified agent facts?\nA: {a}\nB: {b}\nLetter only."
            resp = call_cf(model_id, prompt, max_tokens=10)
            chosen = None
            if resp:
                for ch in resp:
                    if ch.upper() in ("A", "B"):
                        chosen = ch.upper()
                        break
            cname = a if chosen == "A" else b if chosen == "B" else None
            conn.execute("INSERT INTO cross_model VALUES (?,?,?,?,?)",
                (new_id("cm"), f"{a}_vs_{b}", model_name, cname, now_iso()))
            time.sleep(0.1)
        conn.commit()

    # Compute agreement
    print("  Agreement matrix:")
    all_models = [m[1] for m in models[:3]]
    for i, m1 in enumerate(all_models):
        for m2 in all_models[i+1:]:
            r1 = dict(conn.execute("SELECT pair, chosen FROM cross_model WHERE model=?", (m1,)).fetchall())
            r2 = dict(conn.execute("SELECT pair, chosen FROM cross_model WHERE model=?", (m2,)).fetchall())
            agree = sum(1 for p in r1 if r1.get(p) == r2.get(p) and r1[p] is not None)
            total = sum(1 for p in r1 if r1.get(p) is not None and r2.get(p) is not None)
            rate = agree / total * 100 if total else 0
            print(f"    {m1} vs {m2}: {agree}/{total} = {rate:.0f}%")

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  Company Domain Search v3 - Scientific Method")
    print("=" * 60)

    random.seed(42)  # Reproducible
    conn = init_db()

    iid, intent = step1_intent(conn)
    available = step2_generate(conn)

    if len(available) < 3:
        print("\n  Not enough available domains.")
        return

    queries = step3_field_traces(conn, available, MODELS)
    wins = step4_tournament(conn, available, MODELS)
    step5_semantic(conn, available, MODELS)
    step6_cross_model(conn, available, MODELS)

    # Final
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Candidates: {len(available)} available")
    print(f"  Models tested: {len(MODELS)}")
    print(f"  Top domain: {max(wins, key=wins.get) if wins else '?'}")
    print(f"  DB: {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main()
