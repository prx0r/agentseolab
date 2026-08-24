#!/usr/bin/env python3
"""
Company Domain Search — Work backwards from thesis
===================================================
Phase 1: Ask models what domain they'd expect (reverse engineering)
Phase 2: Semantic transmission test
Phase 3: Pairwise tournament (cross-model)
Phase 4: Phonosemantic + fluency
Phase 5: Final ranking
"""

import json, os, sqlite3, hashlib, uuid, time, re
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_domain.db")

def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(p): return f"{p}_{uuid.uuid4().hex[:12]}"

def call_cf(model, prompt, max_tokens=150):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model}"
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
    c.execute("CREATE TABLE IF NOT EXISTS generated_candidates (id TEXT PRIMARY KEY, source_model TEXT, prompt TEXT, response TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pairwise_comparisons (comparison_id TEXT PRIMARY KEY, experiment TEXT, candidate_a TEXT, candidate_b TEXT, ordering TEXT, chosen TEXT, abstained INTEGER, agent_model TEXT, provider TEXT, timestamp TEXT, response_raw TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS semantic_scores (id TEXT PRIMARY KEY, domain TEXT, concept TEXT, score REAL, agent_model TEXT, timestamp TEXT, response_raw TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS hypotheses (hypothesis_id TEXT PRIMARY KEY, statement TEXT, status TEXT, effect_estimate REAL, sample_size INTEGER, model_families_json TEXT)")
    conn.commit()
    return conn

def pair_choice(conn, experiment, a, b, prompt, model):
    resp = call_cf(model, prompt, max_tokens=10)
    chosen = None
    if resp:
        for ch in resp:
            if ch.upper() in ("A", "B"):
                chosen = ch.upper()
                break
    if chosen:
        cname = a if chosen == "A" else b
        conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (new_id("comp"), experiment, a, b, "AB" if chosen == "A" else "BA", cname, 0, model.split("/")[-1], "cloudflare", str(int(time.time())), resp))
        conn.commit()
        return cname
    conn.execute("INSERT INTO pairwise_comparisons VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (new_id("comp"), experiment, a, b, "AB", None, 1, model.split("/")[-1], "cloudflare", str(int(time.time())), resp or ""))
    conn.commit()
    return None

# ============================================================
# PHASE 1: Reverse-engineer from thesis
# ============================================================
def phase1_generate(conn):
    print("\n  PHASE 1: What domain would agents expect?")
    print("  " + "=" * 55)

    model = "@cf/meta/llama-3.2-3b-instruct"
    prompts = [
        "I'm building a service that provides verified, machine-readable truth to AI agents. Things like: is this email deliverable? Is this domain available? Does this API actually work? One call, one answer, cryptographic proof. What .com domain name would you expect this service to have? Just the name, nothing else.",
        "An agent needs to verify something about the real world (DNS status, API health, email validity). It can either figure it out itself or call a trusted service for $0.003. What domain name would this trusted service most likely have? One .com name only.",
        "What is the most natural domain name for a machine that answers verified questions about the internet? Like: is this URL live? Is this package safe? Does this OAuth endpoint work? Give me one .com domain.",
        "If you were looking for a service that provides cryptographic proof of real-world facts to AI agents, what domain would you search for? One .com name.",
    ]

    generated = []
    for i, p in enumerate(prompts):
        resp = call_cf(model, p, max_tokens=30)
        if resp:
            # Extract domain-like strings
            domains = re.findall(r'[a-zA-Z0-9]+\.com', resp)
            if not domains:
                # Maybe they just gave a name without .com
                words = resp.strip().split()
                for w in words:
                    w = w.strip('",.\'"')
                    if len(w) > 2 and len(w) < 20 and w.isalpha():
                        domains.append(w + ".com")
                        break
            for d in domains[:2]:
                d = d.lower().strip()
                conn.execute("INSERT INTO generated_candidates VALUES (?,?,?,?,?)",
                    (new_id("gen"), model, p[:100], d, now_iso()))
                generated.append(d)
                print(f"  Model generated: {d}")
        time.sleep(0.3)

    conn.commit()
    return list(dict.fromkeys(generated))  # dedupe preserving order

# ============================================================
# PHASE 2: Semantic transmission
# ============================================================
def phase2_transmission(conn, domains, model):
    print(f"\n  PHASE 2: Semantic transmission ({model.split('/')[-1]})")
    print("  " + "=" * 55)

    target = ["truth", "proof", "verified", "fact", "answer", "evidence", "reliable", "trust", "check", "confirm", "real"]
    results = {}
    for d in domains:
        prompt = f"You see domain: {d}\nWhat does this website do? One sentence."
        resp = call_cf(model, prompt, max_tokens=50)
        hits = sum(1 for kw in target if kw in (resp or "").lower())
        rate = hits / len(target)
        results[d] = {"response": resp, "score": rate, "hits": hits}
        tag = "GOOD" if hits >= 3 else "WEAK" if hits >= 1 else "MISS"
        print(f"  {d:22} [{tag}] score={rate:.2f} {resp[:55] if resp else '...'}")
        time.sleep(0.2)
    return results

# ============================================================
# PHASE 3: Pairwise tournament
# ============================================================
def phase3_tournament(conn, domains, model, experiment_name):
    print(f"\n  PHASE 3: Tournament ({model.split('/')[-1]})")
    print("  " + "=" * 55)

    pairs = list(combinations(domains, 2))
    wins = {d: 0 for d in domains}
    valid = 0
    abstained = 0

    for a, b in pairs:
        prompt = f"""You are an AI agent. You need verified real-world facts (DNS status, email validity, API health, package safety).

One of these services provides that. Which domain do you trust MORE to give you a verified, machine-readable answer?

A: {a}
B: {b}

Letter only."""
        result = pair_choice(conn, experiment_name, a, b, prompt, model)
        if result:
            wins[result] = wins.get(result, 0) + 1
            valid += 1
            print(f"  {a:20} vs {b:20} -> {result}")
        else:
            abstained += 1
            print(f"  {a:20} vs {b:20} -> ABSTAIN")
        time.sleep(0.2)

    print(f"\n  Leaderboard ({model.split('/')[-1]}):")
    for d in sorted(wins, key=wins.get, reverse=True):
        bar = "#" * wins[d]
        print(f"    {d:22} {wins[d]:>2} {bar}")
    return wins, valid, abstained

# ============================================================
# PHASE 4: Phonosemantic + fluency
# ============================================================
def phase4_sound(conn, domains, model):
    print(f"\n  PHASE 4: Sound symbolism + fluency")
    print("  " + "=" * 55)

    dims = ["trustworthy", "simple", "powerful", "technical", "friendly"]
    for d in domains:
        word = d.split(".")[0]
        prompt = f'Based on the SOUND of "{word}" (not meaning), rate: trustworthy(0-1), simple(0-1), powerful(0-1), technical(0-1), friendly(0-1). CSV only.'
        resp = call_cf(model, prompt, max_tokens=40)
        vals = []
        if resp:
            nums = re.findall(r'\d+\.?\d*', resp)
            vals = [float(n) for n in nums[:5]]
        while len(vals) < 5: vals.append(0.5)
        vec = dict(zip(dims, vals))
        trust_score = vec.get("trustworthy", 0)
        print(f"  {word:18} trust={trust_score:.1f} simple={vec.get('simple',0):.1f} power={vec.get('powerful',0):.1f} tech={vec.get('technical',0):.1f}")
        time.sleep(0.2)

    # Fluency: spell after hearing
    print("\n  Fluency (spell after hearing):")
    for d in domains:
        word = d.split(".")[0]
        prompt = f'I heard a website name that sounds like: "{word}"\nWhat domain do I mean? Just the domain.'
        resp = call_cf(model, prompt, max_tokens=20)
        ok = word.lower() in (resp or "").lower()
        print(f"    {word:18} {'OK' if ok else 'FAIL'} (got: {(resp or '?')[:20]})")
        time.sleep(0.2)

def main():
    print("=" * 60)
    print("  Company Domain Search — Backwards from Thesis")
    print("=" * 60)

    conn = init_db()
    model_3b = "@cf/meta/llama-3.2-3b-instruct"
    model_70b = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"

    # Phase 1: Generate candidates from models
    generated = phase1_generate(conn)

    # Add hand-picked candidates based on thesis
    hand_picked = [
        "invoketruth.com",   # invoke + truth (user's pick)
        "provasciii.com",    # proof + ascii (too long?)
        "trucall.com",       # true + call
        "factcall.com",      # fact + call
        "vericall.com",      # verify + call
        "checkproof.com",    # check + proof
        "evidenceapi.com",   # too long?
        "onestatus.com",     # one + status
        "realcheck.com",     # real + check
        "simpleproof.com",   # simple + proof
        "calledit.com",      # called it (colloquial)
        "trustcall.com",     # trust + call
        "factshot.com",      # fact + shot
        "truthping.com",     # truth + ping
        "verify.live",       # verify + live (not .com)
    ]

    all_domains = list(dict.fromkeys(generated + hand_picked))
    # Filter to reasonable length
    all_domains = [d for d in all_domains if len(d.split(".")[0]) <= 14]

    print(f"\n  Candidate pool: {len(all_domains)} domains")
    print(f"  Generated: {generated}")
    print(f"  Hand-picked: {len(hand_picked)}")

    # Phase 2: Semantic transmission (3B)
    trans_3b = phase2_transmission(conn, all_domains, model_3b)

    # Phase 3: Tournament on 3B
    wins_3b, valid_3b, abs_3b = phase3_tournament(conn, all_domains, model_3b, "tournament_3b")

    # Phase 3b: Tournament on 70B for cross-validation (top 8 only)
    top8 = sorted(wins_3b, key=wins_3b.get, reverse=True)[:8]
    wins_70b, valid_70b, abs_70b = phase3_tournament(conn, top8, model_70b, "tournament_70b")

    # Phase 4: Sound + fluency on top candidates
    top5 = sorted(wins_3b, key=wins_3b.get, reverse=True)[:5]
    phase4_sound(conn, top5, model_3b)

    # Final ranking
    print("\n" + "=" * 60)
    print("  FINAL RANKING")
    print("=" * 60)

    combined = {}
    for d in all_domains:
        w32 = wins_3b.get(d, 0)
        w70 = wins_70b.get(d, 0)
        t32 = trans_3b.get(d, {}).get("score", 0)
        combined[d] = {"w3b": w32, "w70b": w70, "trans": t32, "total": w32 + w70}

    print(f"\n  {'Domain':<22} {'3B wins':>7} {'70B wins':>8} {'Trans':>6} {'Score':>6}")
    print("  " + "-" * 55)
    for d in sorted(combined, key=lambda x: combined[x]["total"], reverse=True):
        c = combined[d]
        print(f"  {d:<22} {c['w3b']:>5}   {c['w70b']:>6}   {c['trans']:.2f}  {c['total']:>4}")

    winner = sorted(combined, key=lambda x: combined[x]["total"], reverse=True)[0]
    print(f"\n  WINNER: {winner}")
    print(f"  3B wins: {combined[winner]['w3b']}")
    print(f"  70B wins: {combined[winner]['w70b']}")
    print(f"  Semantic transmission: {combined[winner]['trans']:.2f}")

    # Store hypothesis
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?)",
        ("H-COMPANY-001", f"Best domain for verified-truth agent service: {winner}",
         "provisional", combined[winner]["total"] / max(valid_3b + valid_70b, 1),
         valid_3b + valid_70b, json.dumps(["llama-3b", "llama-70b"])))
    conn.commit()

    conn.close()
    print(f"\n  Results saved to {DB_PATH}")

if __name__ == "__main__":
    main()
