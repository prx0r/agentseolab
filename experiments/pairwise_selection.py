"""DomainArena DA-T3: Pairwise Domain Selection Experiment.

Core experiment: given two domains for the same intent, which one does an AI
agent select? Tests across model families with AB/BA order randomization.

Protocol:
1. Freeze intent (sha256 hash)
2. For each model × trial:
   a. Randomize presentation order (AB or BA)
   b. Ask model: "Which domain would you use for <intent>?"
   c. Record first-choice selection
3. Aggregate with Wilson score intervals
4. Cross-family replication check

Usage:
    python -m experiments.pairwise_selection \
        --intent "A JSON repair tool" \
        --domain-a "jsonrepair.dev" \
        --domain-b "fixjson.com" \
        --trials 20

Requires: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN env vars.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path


MODELS = [
    ("@cf/meta/llama-3.3-70b-instruct-fp8-fast", "llama"),
    ("@cf/mistralai/mistral-small-3.1-24b-instruct", "mistral"),
    ("@cf/qwen/qwen3-30b-a3b-fp8", "qwen"),
]

SEED = 20260831


def call_cloudflare(model_id: str, prompt: str) -> dict:
    import urllib.request
    account = (os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
               or os.environ.get("CF_ACCOUNT_ID", ""))
    token = (os.environ.get("CLOUDFLARE_API_TOKEN", "")
             or os.environ.get("CF_TOKEN", ""))
    if not account or not token:
        return {"ok": False, "text": "", "error": "no credentials"}
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model_id}"
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100, "temperature": 0,
    }).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
        latency_ms = int((time.time() - t0) * 1000)
        text = (res.get("result", {}).get("choices") or [{}])[0].get("message", {}).get("content", "")
        return {"ok": True, "text": text.strip(), "latency_ms": latency_ms}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)[:200]}


def pairwise_prompt(domain_a: str, domain_b: str, intent: str, order: str) -> str:
    """Generate a pairwise selection prompt. order is 'AB' or 'BA'."""
    if order == "AB":
        first, second = domain_a, domain_b
    else:
        first, second = domain_b, domain_a
    return (
        f"You are choosing a domain name for a product.\n\n"
        f"Product: {intent}\n\n"
        f"Option 1: {first}\n"
        f"Option 2: {second}\n\n"
        f"Which domain would you use? Reply with ONLY the domain name."
    )


def extract_choice(response: str, domain_a: str, domain_b: str) -> str | None:
    """Parse model response to extract which domain was chosen."""
    text = response.lower().strip()
    a_lower = domain_a.lower()
    b_lower = domain_b.lower()
    if a_lower in text and b_lower in text:
        return None  # ambiguous
    if a_lower in text:
        return domain_a
    if b_lower in text:
        return domain_b
    # Fallback: check if first word matches
    words = text.split()
    if words:
        if words[0] == a_lower:
            return domain_a
        if words[0] == b_lower:
            return domain_b
    return None  # unparseable


def wilson_lower(wins: int, n: int) -> float:
    """Wilson score interval lower bound (95%)."""
    if n == 0:
        return 0.0
    p = wins / n
    z = 1.96
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    spread = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (center - spread) / denom


def run_pairwise(
    intent: str,
    domain_a: str,
    domain_b: str,
    n_trials: int,
    output_dir: Path,
) -> dict:
    print(f"\n{'='*60}")
    print(f"DA-T3 Pairwise Domain Selection")
    print(f"{'='*60}")
    print(f"Intent: {intent}")
    print(f"Domain A: {domain_a}")
    print(f"Domain B: {domain_b}")
    print(f"Trials per model: {n_trials}")
    print(f"Seed: {SEED}")
    print(f"{'='*60}\n")

    # Freeze intent hash
    intent_hash = hashlib.sha256(intent.encode()).hexdigest()

    results = []
    for model_id, family in MODELS:
        print(f"Model: {family} ({model_id})")
        wins_a = 0
        wins_b = 0
        abstentions = 0

        for trial in range(n_trials):
            rng = random.Random(SEED + trial)
            order = rng.choice(["AB", "BA"])
            prompt = pairwise_prompt(domain_a, domain_b, intent, order)
            resp = call_cloudflare(model_id, prompt)

            if not resp["ok"]:
                results.append({
                    "trial": trial, "model": model_id, "family": family,
                    "order": order, "domain_a": domain_a, "domain_b": domain_b,
                    "choice": None, "error": resp.get("error", ""),
                    "response": "", "latency_ms": 0,
                })
                continue

            choice = extract_choice(resp["text"], domain_a, domain_b)
            if choice == domain_a:
                wins_a += 1
            elif choice == domain_b:
                wins_b += 1
            else:
                abstentions += 1

            results.append({
                "trial": trial, "model": model_id, "family": family,
                "order": order, "domain_a": domain_a, "domain_b": domain_b,
                "choice": choice, "response": resp["text"][:200],
                "latency_ms": resp["latency_ms"],
            })

        n_decided = wins_a + wins_b
        prop_a = wins_a / n_decided if n_decided > 0 else 0.5
        ci_lower = wilson_lower(wins_a, n_decided)
        ci_upper = 1 - wilson_lower(wins_b, n_decided)
        significant = ci_lower > 0.5 or ci_upper < 0.5

        print(f"  wins_A={wins_a} wins_B={wins_b} abstain={abstentions}")
        print(f"  prop_A={prop_a:.1%} CI=[{ci_lower:.1%}, {ci_upper:.1%}]")
        print(f"  significant: {significant}")
        print()

    # Cross-family consensus
    family_choices = {}
    for r in results:
        if r.get("choice"):
            family_choices.setdefault(r["family"], []).append(r["choice"])

    consensus_by_family = {}
    for fam, choices in family_choices.items():
        from collections import Counter
        c = Counter(choices)
        consensus_by_family[fam] = c.most_common(1)[0]

    print("Cross-family consensus:")
    for fam, (dom, count) in consensus_by_family.items():
        print(f"  {fam}: {dom} ({count} times)")

    all_fam_winners = [dom for dom, _ in consensus_by_family.values()]
    if all_fam_winners:
        from collections import Counter
        overall = Counter(all_fam_winners).most_common(1)[0]
        print(f"\nOverall consensus: {overall[0]} ({overall[1]}/{len(MODELS)} families)")
    else:
        overall = (None, 0)

    # Write results
    output_dir.mkdir(parents=True, exist_ok=True)
    experiment_data = {
        "experiment": "DA-T3-pairwise",
        "protocol_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "intent_hash": f"sha256:{intent_hash}",
        "domain_a": domain_a,
        "domain_b": domain_b,
        "seed": SEED,
        "n_trials_per_model": n_trials,
        "models": [m[0] for m in MODELS],
        "results": results,
        "consensus_by_family": {k: {"domain": v[0], "count": v[1]}
                                for k, v in consensus_by_family.items()},
        "overall_consensus": {"domain": overall[0], "families": overall[1]},
    }

    evidence_bytes = json.dumps(experiment_data, sort_keys=True, default=str).encode()
    experiment_data["evidence_hash"] = f"sha256:{hashlib.sha256(evidence_bytes).hexdigest()}"

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    outfile = output_dir / f"DA-T3_{ts}.json"
    outfile.write_text(json.dumps(experiment_data, indent=2, default=str))
    print(f"\nEvidence hash: {experiment_data['evidence_hash'][:24]}...")
    print(f"Written to: {outfile}")

    return experiment_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DA-T3 Pairwise Domain Selection")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--domain-a", required=True)
    parser.add_argument("--domain-b", required=True)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--output", default="results/pairwise")
    args = parser.parse_args()

    run_pairwise(args.intent, args.domain_a, args.domain_b,
                 args.trials, Path(args.output))
