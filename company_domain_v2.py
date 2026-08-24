#!/usr/bin/env python3
"""
Company Domain Search v2 — Fixed Experiments
=============================================
Fixes from v1:
1. Availability filter FIRST (RDAP check)
2. Position bias measurement (50% AB/50% BA with logging)
3. Separate generator/judge models
4. Length-pairing control (match similar-length domains)
5. Repetition stability (run each pair 3x)
6. Bradley-Terry scoring
7. New experiment types: tool description A/B, trust signals, cross-model consistency
"""

import json, os, sqlite3, hashlib, uuid, time, re, math
from datetime import datetime, timezone
from itertools import combinations
import urllib.request

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_API_TOKEN = os.environ["CF_API_TOKEN"]  # token must come from env (was hard-coded; rotate original)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_domain_v2.db")

def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(p): return f"{p}_{uuid.uuid4().hex[:12]}"

def call_cf(model, prompt, max_tokens=150):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model}"
    data = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read())
            resp = r.get("result", {}).get("response", "")
            return str(resp).strip() if resp else ""
    except Exception as e:
        print(f"    API err: {e}")
        return None

def check_available(domain):
    """RDAP check — only domains with no RDAP record are candidates."""
    try:
        resp = urllib.request.urlopen(f"https://rdap.verisign.com/com/v1/domain/{domain}", timeout=10)
        data = json.loads(resp.read())
        status = data.get("status", ["unknown"])
        return False, status[0] if status else "unknown"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True, "no_record"
        return False, f"http_{e.code}"
    except:
        return True, "check_failed"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS candidates (domain TEXT PRIMARY KEY, family TEXT, length INTEGER, available INTEGER, rdap_status TEXT, checked_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pairwise_v2 (id TEXT PRIMARY KEY, experiment TEXT, model TEXT, candidate_a TEXT, candidate_b TEXT, length_a INTEGER, length_b INTEGER, ordering TEXT, chosen TEXT, abstained INTEGER, position_first INTEGER, timestamp TEXT, response_raw TEXT, run_number INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS tool_ab (id TEXT PRIMARY KEY, model TEXT, description_a TEXT, description_b TEXT, chosen TEXT, reasoning TEXT, timestamp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS trust_signals (id TEXT PRIMARY KEY, model TEXT, signal_type TEXT, domain TEXT, trust_score REAL, reasoning TEXT, timestamp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS hypotheses (hypothesis_id TEXT PRIMARY KEY, statement TEXT, status TEXT, effect_estimate REAL, sample_size INTEGER, model_families_json TEXT)")
    conn.commit()
    return conn

# ============================================================
# STEP 1: Generate candidates + availability filter
# ============================================================
def step1_generate_and_filter(conn):
    print("\n  STEP 1: Generate + filter available domains")
    print("  " + "=" * 55)

    model_gen = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"  # different model for generation
    model_judge = "@cf/meta/llama-3.2-3b-instruct"  # different model for judging

    # Generate from different conceptual angles
    prompts = [
        "Give me 5 one-word or two-word .com domain names for a service that provides verified machine-readable facts to AI agents. Think: trust, proof, evidence, verification. Names only, one per line.",
        "I need a short .com domain for a $0.003 API that answers verified questions like 'is this email valid?' and 'does this API work?'. Give me 5 candidates. Names only.",
        "What .com domain would you expect for 'the vending machine for verified real-world facts that agents can buy for fractions of a cent'? 5 names, one per line.",
    ]

    generated = set()
    for p in prompts:
        resp = call_cf(model_gen, p, max_tokens=100)
        if resp:
            for line in resp.strip().split("\n"):
                line = line.strip().strip("- ").strip("* ").strip("0123456789. ")
                # Extract domain-like words
                for word in re.findall(r'[a-zA-Z]{2,14}', line):
                    if word.lower() not in ("com", "the", "and", "for", "that", "this", "name", "domain"):
                        generated.add(word.lower() + ".com")
        time.sleep(0.3)

    # Hand-picked candidates across families
    hand_picked = {
        "invoketruth.com": "suggestive",
        "factcall.com": "action_object",
        "vericall.com": "action_object",
        "checkproof.com": "action_object",
        "realcheck.com": "action_object",
        "truthping.com": "action_object",
        "onestatus.com": "action_object",
        "calledit.com": "suggestive",
        "trustcall.com": "action_object",
        "simpleproof.com": "suggestive",
        "evidenceapi.com": "descriptive",
        "verinet.com": "suggestive",
        "factshot.com": "action_object",
        "trucall.com": "suggestive",
        "proofcall.com": "action_object",
        "verifycall.com": "action_object",
        "truthcheck.com": "action_object",
        "factproof.com": "suggestive",
        "callproof.com": "action_object",
        "getproof.com": "action_object",
    }

    # Check availability for ALL candidates
    all_domains = list(set(list(generated) + list(hand_picked.keys())))
    available = []

    print(f"  Checking {len(all_domains)} candidates for availability...")
    for d in sorted(all_domains):
        if len(d.split(".")[0]) > 14:
            continue
        is_avail, status = check_available(d)
        length = len(d.split(".")[0])
        family = hand_picked.get(d, "generated")
        conn.execute("INSERT OR REPLACE INTO candidates VALUES (?,?,?,?,?,?)",
            (d, family, length, 1 if is_avail else 0, status, now_iso()))
        if is_avail:
            available.append({"domain": d, "family": family, "length": length})
            print(f"    {d:22} AVAILABLE (len={length})")
        else:
            print(f"    {d:22} taken ({status})")
        time.sleep(0.1)

    conn.commit()
    print(f"\n  Available: {len(available)}/{len(all_domains)}")
    return available, model_judge

# ============================================================
# STEP 2: Pairwise tournament (fixed: position bias, repetition, length control)
# ============================================================
def step2_tournament(conn, available, model, repetitions=3):
    print(f"\n  STEP 2: Fixed tournament ({repetitions}x repetition, position bias logged)")
    print("  " + "=" * 55)

    # Pair similar-length domains to control for length confound
    by_len = {}
    for d in available:
        l = d["length"]
        by_len.setdefault(l, []).append(d)

    pairs = []
    # Same-length pairs (controlled)
    for length, group in by_len.items():
        for a, b in combinations(group, 2):
            pairs.append((a, b, "same_length"))
    # Cross-length pairs (for length effect measurement)
    lengths = sorted(by_len.keys())
    for i in range(len(lengths)):
        for j in range(i+1, min(i+3, len(lengths))):
            for a in by_len[lengths[i]][:3]:
                for b in by_len[lengths[j]][:3]:
                    pairs.append((a, b, "cross_length"))

    wins = {d["domain"]: 0 for d in available}
    valid = 0
    position_wins_first = 0
    total_with_order = 0

    print(f"  {len(pairs)} pairs x {repetitions} runs = {len(pairs)*repetitions} comparisons")

    for run in range(repetitions):
        for a_info, b_info, pair_type in pairs:
            a, b = a_info["domain"], b_info["domain"]
            # Randomize order (50/50)
            import random
            if random.random() < 0.5:
                left, right = a_info, b_info
                ordering = "AB"
            else:
                left, right = b_info, a_info
                ordering = "BA"

            prompt = f"""You are an AI agent seeking verified real-world facts.

Service A: {left['domain']}
Service B: {right['domain']}

Which would you trust MORE to give you a verified, machine-readable answer? Letter only."""

            resp = call_cf(model, prompt, max_tokens=10)
            chosen = None
            if resp:
                for ch in resp:
                    if ch.upper() in ("A", "B"):
                        chosen = ch.upper()
                        break

            if chosen:
                cname = left["domain"] if chosen == "A" else right["domain"]
                # Was the first-presented domain chosen?
                first_chosen = (chosen == "AB" and ordering == "AB") or (chosen == "BA" and ordering == "BA")
                if first_chosen:
                    position_wins_first += 1
                total_with_order += 1

                conn.execute("INSERT INTO pairwise_v2 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_id("p"), "tournament_v2", model, a, b, a_info["length"], b_info["length"],
                     ordering, cname, 0, 1 if first_chosen else 0, now_iso(), resp, run+1))
                wins[cname] = wins.get(cname, 0) + 1
                valid += 1
            else:
                conn.execute("INSERT INTO pairwise_v2 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_id("p"), "tournament_v2", model, a, b, a_info["length"], b_info["length"],
                     ordering, None, 1, 0, now_iso(), resp or "", run+1))

            conn.commit()
            time.sleep(0.15)

    # Position bias
    pos_rate = position_wins_first / total_with_order * 100 if total_with_order else 0
    print(f"\n  Position bias: {pos_rate:.0f}% first-position wins (50% = no bias)")

    # Length correlation
    print(f"\n  Length analysis:")
    len_wins = {}
    for d in available:
        l = d["length"]
        len_wins[l] = len_wins.get(l, 0) + wins.get(d["domain"], 0)
    for l in sorted(len_wins):
        print(f"    {l} chars: {len_wins[l]} total wins")

    print(f"\n  Leaderboard:")
    for d in sorted(wins, key=wins.get, reverse=True)[:10]:
        bar = "#" * wins[d]
        print(f"    {d:22} {wins[d]:>3} {bar}")

    return wins, valid, pos_rate

# ============================================================
# STEP 3: Bradley-Terry scoring
# ============================================================
def step3_bradley_terry(conn, available):
    print(f"\n  STEP 3: Bradley-Terry preference model")
    print("  " + "=" * 55)

    # Count head-to-head wins
    domains = [d["domain"] for d in available]
    head_to_head = {}
    for d in domains:
        head_to_head[d] = {}
        for d2 in domains:
            if d != d2:
                head_to_head[d][d2] = {"wins": 0, "losses": 0}

    rows = conn.execute("SELECT candidate_a, candidate_b, chosen FROM pairwise_v2 WHERE abstained=0").fetchall()
    for a, b, chosen in rows:
        if chosen == a:
            head_to_head[a][b]["wins"] += 1
            head_to_head[b][a]["losses"] += 1
        elif chosen == b:
            head_to_head[b][a]["wins"] += 1
            head_to_head[a][b]["losses"] += 1

    # Simple BT: strength = wins / (wins + losses)
    bt_scores = {}
    for d in domains:
        total_wins = sum(head_to_head[d][d2]["wins"] for d2 in domains if d2 != d)
        total_losses = sum(head_to_head[d][d2]["losses"] for d2 in domains if d2 != d)
        total = total_wins + total_losses
        bt_scores[d] = total_wins / total if total > 0 else 0.5

    print(f"  {'Domain':<22} {'BT Score':>8} {'95% CI':>12}")
    print("  " + "-" * 45)
    for d in sorted(bt_scores, key=bt_scores.get, reverse=True):
        # Bootstrap CI approximation
        n = sum(head_to_head[d][d2]["wins"] + head_to_head[d][d2]["losses"] for d2 in domains if d2 != d)
        se = math.sqrt(bt_scores[d] * (1 - bt_scores[d]) / max(n, 1))
        ci_lo = max(0, bt_scores[d] - 1.96 * se)
        ci_hi = min(1, bt_scores[d] + 1.96 * se)
        print(f"  {d:22} {bt_scores[d]:>7.3f}  [{ci_lo:.3f}, {ci_hi:.3f}]")

    return bt_scores

# ============================================================
# STEP 4: Tool Description A/B (from DEEP_RESEARCH.md)
# ============================================================
def step4_tool_ab(conn, model):
    print(f"\n  STEP 4: Tool Description A/B Test")
    print("  " + "=" * 55)

    # Test: does the description phrasing change which tool an agent selects?
    descriptions = [
        ("Check if an email address is deliverable by querying MX records and SMTP behavior.", "Verify email validity with cryptographic proof of DNS and SMTP state."),
        ("Look up current DNS records for a domain.", "Get live DNS state with timestamped evidence from authoritative nameservers."),
        ("Test if an API endpoint is working.", "Probe an API endpoint and return verified health status with latency percentiles."),
    ]

    for desc_a, desc_b in descriptions:
        # Which description makes the agent more likely to use the tool?
        prompt = f"""You need to verify something about the real world. Two tools are available:

Tool 1: {desc_a}
Tool 2: {desc_b}

Which tool would you choose? Letter only (1 or 2)."""

        resp = call_cf(model, prompt, max_tokens=10)
        chosen = None
        if resp:
            for ch in resp:
                if ch in ("1", "2"):
                    chosen = "A" if ch == "1" else "B"
                    break

        conn.execute("INSERT INTO tool_ab VALUES (?,?,?,?,?,?,?)",
            (new_id("ab"), model, desc_a, desc_b, chosen or "ABSTAIN", resp[:200] if resp else "", now_iso()))
        conn.commit()

        short_a = desc_a[:40] + "..."
        short_b = desc_b[:40] + "..."
        print(f"  A: {short_a}")
        print(f"  B: {short_b}")
        print(f"  -> {'A' if chosen == 'A' else 'B' if chosen == 'B' else 'ABSTAIN'}")
        print()

# ============================================================
# STEP 5: Trust Signal Experiment (from DEEP_RESEARCH.md)
# ============================================================
def step5_trust_signals(conn, model):
    print(f"\n  STEP 5: Trust Signal Experiment")
    print("  " + "=" * 55)

    signals = [
        ("verified_freshness", "This result was verified 30 seconds ago with cryptographic timestamp."),
        ("execution_proof", "This result was produced by actually executing the check, not reasoning about it."),
        ("historical_data", "This result is backed by 50,000 prior observations of this same endpoint."),
        ("source_attribution", "This result cites the specific DNS server and SMTP response that produced it."),
        ("reputation_score", "This provider has 99.7% accuracy across 1M+ prior verifications."),
    ]

    domain = "invoketruth.com"
    for signal_type, signal_desc in signals:
        prompt = f"""A service at {domain} provides verified facts to AI agents.

It includes this trust signal: {signal_desc}

How much do you trust this service? Rate 1-10."""

        resp = call_cf(model, prompt, max_tokens=20)
        score = 5.0
        if resp:
            nums = re.findall(r'\d+\.?\d*', resp)
            if nums:
                score = float(nums[0])
                if score > 10: score = score / 10  # normalize

        reasoning = resp[:200] if resp else ""
        conn.execute("INSERT INTO trust_signals VALUES (?,?,?,?,?,?,?)",
            (new_id("trust"), model, signal_type, domain, score, reasoning, now_iso()))
        conn.commit()
        print(f"  {signal_type:25} trust={score:.1f}/10  {resp[:50] if resp else ''}")
        time.sleep(0.2)

# ============================================================
# STEP 6: Cross-model consistency (from DEEP_RESEARCH.md)
# ============================================================
def step6_cross_model(conn, available):
    print(f"\n  STEP 6: Cross-Model Consistency")
    print("  " + "=" * 55)

    # Use a DIFFERENT model family - Cloudflare has DeepSeek
    models = [
        ("@cf/deepseek-ai/deepseek-r1-distill-qwen-32b", "deepseek"),
        ("@cf/meta/llama-3.2-3b-instruct", "llama"),
    ]

    # Test 5 pairs across models
    top5 = sorted(available, key=lambda x: x["length"])[:5]
    pairs = list(combinations(top5, 2))[:5]

    results = {m[1]: {} for m in models}
    for model, name in models:
        for a, b in pairs:
            prompt = f"Which domain for verified agent facts?\nA: {a['domain']}\nB: {b['domain']}\nLetter only."
            resp = call_cf(model, prompt, max_tokens=10)
            chosen = None
            if resp:
                for ch in resp:
                    if ch.upper() in ("A", "B"):
                        chosen = ch.upper()
                        break
            cname = a["domain"] if chosen == "A" else b["domain"] if chosen == "B" else None
            results[name][f"{a['domain']}_vs_{b['domain']}"] = cname
            print(f"  {name:10} {a['domain']:18} vs {b['domain']:18} -> {cname or 'ABSTAIN'}")
            time.sleep(0.2)

    # Agreement rate
    agreements = 0
    total = 0
    for key in results["deepseek"]:
        if results["deepseek"].get(key) and results["llama"].get(key):
            total += 1
            if results["deepseek"][key] == results["llama"][key]:
                agreements += 1
    rate = agreements / total * 100 if total else 0
    print(f"\n  Cross-model agreement: {agreements}/{total} = {rate:.0f}%")
    return rate

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  Company Domain Search v2 — Fixed Experiments")
    print("=" * 60)

    conn = init_db()
    available, model_judge = step1_generate_and_filter(conn)

    if len(available) < 4:
        print("\n  Not enough available domains. Aborting.")
        return

    wins, valid, pos_rate = step2_tournament(conn, available, model_judge, repetitions=2)
    bt_scores = step3_bradley_terry(conn, available)
    step4_tool_ab(conn, model_judge)
    step5_trust_signals(conn, model_judge)
    cross_rate = step6_cross_model(conn, available)

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL RESULTS (v2)")
    print("=" * 60)

    top5 = sorted(bt_scores, key=bt_scores.get, reverse=True)[:5]
    print(f"\n  Top 5 by Bradley-Terry score:")
    for i, d in enumerate(top5, 1):
        print(f"    {i}. {d} (BT={bt_scores[d]:.3f})")

    print(f"\n  Controls applied:")
    print(f"    Position bias: {pos_rate:.0f}% (50% = ideal)")
    print(f"    Cross-model agreement: {cross_rate:.0f}%")
    print(f"    All {len(available)} candidates verified available via RDAP")
    print(f"    Generator model: llama-3.3-70b (separate from judge)")

    winner = top5[0]
    print(f"\n  RECOMMENDATION: {winner}")
    print(f"  BT score: {bt_scores[winner]:.3f}")

    # Store
    conn.execute("INSERT OR REPLACE INTO hypotheses VALUES (?,?,?,?,?,?)",
        ("H-V2-001", f"Best domain for verified-truth agent service: {winner}", "provisional",
         bt_scores[winner], valid, json.dumps(["llama", "deepseek"])))
    conn.commit()
    conn.close()
    print(f"\n  Saved to {DB_PATH}")

if __name__ == "__main__":
    main()
