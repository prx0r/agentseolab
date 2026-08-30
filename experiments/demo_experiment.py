"""DomainArena Demo Experiment — focused, reproducible, hackathon-ready.

Runs a controlled candidate experiment for a single product intent:
1. Search name.com for real available domains
2. Run semantic inversion across 2-3 model families
3. Produce evidence hashes
4. Generate recommendation with full audit trail

Usage:
    python -m experiments.demo_experiment --intent "A JSON repair tool" --job "fix malformed JSON"

Requires: NAMECOM_USERNAME, NAMECOM_TOKEN, CF_ACCOUNT_ID, CF_TOKEN env vars.
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

# ── Config ──────────────────────────────────────────────────────────

MODELS = [
    ("meta-llama-3.3-70b", "cloudflare"),
    ("mistral-small-24b", "cloudflare"),
    ("qwen3-30b", "cloudflare"),
]

N_TRIALS_PER_MODEL = 10
TEMPERATURE = 0
SEED = 20260831


# ── Semantic Inversion ──────────────────────────────────────────────

def semantic_inversion_prompt(domain: str) -> str:
    return (
        "You are shown a domain name with no other context.\n"
        f"Domain: {domain}\n\n"
        "What product or service do you think runs behind this domain?\n"
        "Reply in one sentence."
    )


def call_cloudflare(model_id: str, prompt: str) -> dict:
    """Call Cloudflare Workers AI."""
    import urllib.request
    account_id = os.environ.get("CF_ACCOUNT_ID", "")
    api_token = os.environ.get("CF_TOKEN", "")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_id}"
    body = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 200}
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.loads(r.read())
    latency_ms = int((time.time() - t0) * 1000)
    msg = (res.get("result", {}).get("choices") or [{}])[0].get("message", {})
    return {"text": msg.get("content", ""), "latency_ms": latency_ms}


def compute_similarity(intent: str, inference: str) -> float:
    """Simple keyword overlap similarity (deterministic, no API needed)."""
    intent_words = set(intent.lower().split())
    inference_words = set(inference.lower().split())
    if not intent_words or not inference_words:
        return 0.0
    overlap = intent_words & inference_words
    return len(overlap) / max(len(intent_words), 1)


# ── Main ────────────────────────────────────────────────────────────

def run_demo_experiment(intent: str, primary_job: str, output_dir: Path):
    """Run the demo experiment and write results."""
    print(f"\n{'='*60}")
    print(f"DomainArena Demo Experiment")
    print(f"{'='*60}")
    print(f"Intent: {intent}")
    print(f"Job: {primary_job}")
    print(f"Seed: {SEED}")
    print(f"Models: {[m[0] for m in MODELS]}")
    print(f"Trials per model: {N_TRIALS_PER_MODEL}")
    print(f"{'='*60}\n")
    
    # 1. Search name.com for candidates
    print("[1/4] Searching name.com for candidates...")
    try:
        from domainarena.providers.namecom import client_from_env
        client = client_from_env()
        import asyncio
        
        keywords = primary_job.split()[:3]  # Use first 3 words as keywords
        all_candidates = []
        for kw in keywords:
            try:
                results = asyncio.run(client.search(kw, ["com", "dev", "io"]))
                all_candidates.extend(results)
            except Exception as e:
                print(f"  Warning: search for '{kw}' failed: {e}")
        asyncio.run(client.close())
        
        # Deduplicate and filter
        seen = set()
        candidates = []
        for c in all_candidates:
            if c.domain_name not in seen and c.purchasable:
                seen.add(c.domain_name)
                candidates.append(c)
        
        if not candidates:
            print("  No live candidates found, using fixtures")
            candidates = _fixture_candidates()
        else:
            print(f"  Found {len(candidates)} available domains")
    except Exception as e:
        print(f"  Name.com unavailable ({e}), using fixtures")
        candidates = _fixture_candidates()
    
    # Select top candidates (by name length, shorter is better for demo)
    candidates.sort(key=lambda c: len(c.domain_name))
    selected = candidates[:5]
    print(f"  Selected: {[c.domain_name for c in selected]}")
    
    # 2. Run semantic inversion across models
    print("\n[2/4] Running semantic inference across model families...")
    results = []
    for model_id, provider in MODELS:
        print(f"  Model: {model_id}")
        for trial in range(N_TRIALS_PER_MODEL):
            # Randomize candidate order per trial
            rng = random.Random(SEED + trial)
            trial_candidates = list(selected)
            rng.shuffle(trial_candidates)
            
            for slot, cand in enumerate(trial_candidates):
                prompt = semantic_inversion_prompt(cand.domain_name)
                try:
                    if provider == "cloudflare":
                        resp = call_cloudflare(model_id, prompt)
                    else:
                        resp = {"text": "unknown", "latency_ms": 0}
                    
                    inference = resp["text"].strip()
                    similarity = compute_similarity(intent, inference)
                    
                    results.append({
                        "trial": trial,
                        "model": model_id,
                        "provider": provider,
                        "domain": cand.domain_name,
                        "slot": slot,
                        "inference": inference,
                        "similarity": round(similarity, 4),
                        "latency_ms": resp["latency_ms"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as e:
                    print(f"    Error: {e}")
                    results.append({
                        "trial": trial, "model": model_id, "provider": provider,
                        "domain": cand.domain_name, "slot": slot,
                        "inference": "", "similarity": 0.0,
                        "latency_ms": 0, "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
        
        # Report per-model stats
        model_results = [r for r in results if r["model"] == model_id]
        avg_sim = sum(r["similarity"] for r in model_results) / max(len(model_results), 1)
        print(f"    Avg similarity: {avg_sim:.3f} ({len(model_results)} trials)")
    
    # 3. Aggregate results
    print("\n[3/4] Aggregating results...")
    summary = {}
    for model_id, _ in MODELS:
        model_results = [r for r in results if r["model"] == model_id]
        domain_scores = {}
        for r in model_results:
            dom = r["domain"]
            if dom not in domain_scores:
                domain_scores[dom] = []
            domain_scores[dom].append(r["similarity"])
        
        avg_by_domain = {d: sum(s)/len(s) for d, s in domain_scores.items()}
        best_domain = max(avg_by_domain, key=avg_by_domain.get) if avg_by_domain else None
        
        summary[model_id] = {
            "n_trials": len(model_results),
            "avg_similarity": sum(r["similarity"] for r in model_results) / max(len(model_results), 1),
            "best_domain": best_domain,
            "best_score": avg_by_domain.get(best_domain, 0) if best_domain else 0,
            "domain_scores": avg_by_domain,
        }
        print(f"  {model_id}: best={best_domain} (score={summary[model_id]['best_score']:.3f})")
    
    # Cross-model consensus
    all_best = [s["best_domain"] for s in summary.values() if s["best_domain"]]
    consensus = max(set(all_best), key=all_best.count) if all_best else None
    consensus_count = all_best.count(consensus) if consensus else 0
    print(f"\n  Cross-model consensus: {consensus} ({consensus_count}/{len(MODELS)} models)")
    
    # 4. Write results with evidence hash
    print("\n[4/4] Writing results...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    experiment_data = {
        "experiment": "DEMO-001",
        "protocol_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "primary_job": primary_job,
        "seed": SEED,
        "models": [m[0] for m in MODELS],
        "n_trials_per_model": N_TRIALS_PER_MODEL,
        "candidates": [c.domain_name for c in selected],
        "summary": summary,
        "consensus": consensus,
        "consensus_count": consensus_count,
        "results": results,
    }
    
    # Compute evidence hash
    evidence_bytes = json.dumps(experiment_data, sort_keys=True, default=str).encode()
    evidence_hash = hashlib.sha256(evidence_bytes).hexdigest()
    experiment_data["evidence_hash"] = f"sha256:{evidence_hash}"
    
    # Write to file
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    outfile = output_dir / f"DEMO-001_{ts}.json"
    outfile.write_text(json.dumps(experiment_data, indent=2, default=str))
    
    print(f"  Evidence hash: sha256:{evidence_hash[:16]}...")
    print(f"  Written to: {outfile}")
    print(f"\n{'='*60}")
    print(f"Experiment complete!")
    print(f"  Consensus domain: {consensus}")
    print(f"  Evidence hash: sha256:{evidence_hash[:16]}...")
    print(f"{'='*60}\n")
    
    return experiment_data


def _fixture_candidates():
    """Fallback fixture candidates when name.com is unavailable."""
    from domainarena.models import InventorySnapshot
    now = datetime.now(timezone.utc).isoformat()
    fixtures = [
        ("jsonrepair.dev", 9.99, 11.99),
        ("factprobe.dev", 12.99, 14.99),
        ("velora.com", 10.44, 12.88),
    ]
    return [
        InventorySnapshot(
            domain_name=dom, sld=dom.split(".")[0], tld=dom.split(".")[-1],
            purchasable=True, purchase_price=price, renewal_price=renew,
            purchase_type="registration", checked_at=now,
        )
        for dom, price, renew in fixtures
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DomainArena Demo Experiment")
    parser.add_argument("--intent", default="A JSON repair tool for fixing malformed JSON")
    parser.add_argument("--job", default="fix malformed JSON")
    parser.add_argument("--output", default="results/demo_experiment")
    args = parser.parse_args()
    
    run_demo_experiment(args.intent, args.job, Path(args.output))
