#!/usr/bin/env python3
"""run_experiment.py — Run da-json-repair-v1 experiment.

Uses CF Workers AI for semantic inversion and selection trials.
Produces content-addressed evidence receipts.
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load env
for line in open(ROOT / ".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)

import urllib.request

CF_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "REDACTED")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

CF_MODELS = {
    "llama": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "mistral": "@cf/mistralai/mistral-small-3.1-24b-instruct",
}

GROQ_MODELS = {
    "qwen": "qwen/qwen3.6-27b",
}

ALL_MODELS = {**CF_MODELS, **GROQ_MODELS}

CANDIDATES = [
    "jsonrepair.dev", "jsonmedic.com", "fixmyjson.io",
    "velora.com", "datahelper.dev",
]

INTENT = "Repairs malformed JSON for AI agents"
SEED = 42
TRIALS_PER_CONDITION = 20


def cf_infer(model_id: str, prompt: str, max_tokens: int = 200) -> dict:
    """Call Cloudflare Workers AI."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/{model_id}"
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=body, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
        latency_ms = int((time.time() - t0) * 1000)
        text = (res.get("result", {}).get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        return {"ok": True, "text": text, "latency_ms": latency_ms}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)[:200], "latency_ms": int((time.time() - t0) * 1000)}


def groq_infer(model_id: str, prompt: str, max_tokens: int = 300) -> dict:
    """Call Groq API. User-Agent required, reasoning models need max_tokens >= 300."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max(max_tokens, 300),  # reasoning models need >= 300
    }).encode()
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "DomainArena/1.0",  # REQUIRED: prevents 403
    }
    req = urllib.request.Request(url, data=body, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
        latency_ms = int((time.time() - t0) * 1000)
        text = (res.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        # Strip <think> tags from qwen reasoning models
        import re
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return {"ok": True, "text": text, "latency_ms": latency_ms}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)[:200], "latency_ms": int((time.time() - t0) * 1000)}


def infer(model_key: str, prompt: str, max_tokens: int = 200) -> dict:
    """Route to correct provider."""
    if model_key in GROQ_MODELS:
        return groq_infer(GROQ_MODELS[model_key], prompt, max_tokens)
    return cf_infer(CF_MODELS[model_key], prompt, max_tokens)


def semantic_inversion(domain: str, model_key: str) -> dict:
    """Ask model what it thinks runs behind this domain (blind inference)."""
    prompt = (
        f"You are shown a domain name with no other context.\n"
        f"Domain: {domain}\n\n"
        f"What product or service do you think runs behind this domain?\n"
        f"Reply in one sentence."
    )
    return infer(model_key, prompt)


def semantic_score(inference: str, intent: str, scorer_key: str) -> dict:
    """Hidden scorer: compare inference against frozen intent."""
    prompt = (
        f"You are a semantic evaluator. Rate how well the inference matches the intent.\n\n"
        f"FROZEN INTENT: {intent}\n"
        f"INFERENCE: {inference}\n\n"
        f"Score 0.0-1.0: 1.0=exact match, 0.7-0.9=partial, 0.3-0.6=weak, 0.0-0.2=none.\n"
        f'Reply in JSON: {{"score": <float>, "label": "<exact|partial|none>"}}'
    )
    res = infer(scorer_key, prompt)
    if not res["ok"]:
        return {"score": 0.0, "label": "error"}
    try:
        parsed = json.loads(res["text"])
        return {"score": float(parsed.get("score", 0)), "label": parsed.get("label", "none")}
    except:
        import re
        m = re.search(r'"?score"?\s*[:=]\s*([0-9.]+)', res["text"])
        return {"score": float(m.group(1)) if m else 0.0, "label": "none"}


def selection_trial(candidates: list[str], intent: str, model_key: str, seed: int) -> dict:
    """Ask model to pick the best domain for the intent."""
    import random
    rng = random.Random(seed)
    shuffled = candidates[:]
    rng.shuffle(shuffled)
    
    prompt = (
        f"I need a domain for a service that: {intent}\n\n"
        f"Available domains:\n"
    )
    for i, c in enumerate(shuffled):
        prompt += f"  {chr(65+i)}. {c}\n"
    prompt += "\nReply with just the letter (A, B, C, etc.) or 'none' if none work."
    
    res = infer(model_key, prompt, max_tokens=10)
    if not res["ok"]:
        return {"picked": None, "abstained": True, "order": shuffled}
    
    text = (res.get("text") or "").strip().upper()
    idx = None
    for letter in ["A", "B", "C", "D", "E"]:
        if text.startswith(letter):
            idx = ord(letter) - 65
            break
    
    picked = shuffled[idx] if idx is not None and idx < len(shuffled) else None
    return {"picked": picked, "abstained": picked is None, "order": shuffled, "raw": text}


def run_experiment():
    """Run full experiment."""
    results = {
        "experiment_id": "da-json-repair-v1",
        "frozen_at": "2026-08-30T02:40:00Z",
        "intent": INTENT,
        "candidates": CANDIDATES,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scorer_model": CF_MODELS["llama"],  # scorer is separate from tested models
    }
    
    # Semantic inversion across families
    print("=== SEMANTIC INVERSION ===")
    results["semantic_inversion"] = {}
    for family in ALL_MODELS:
        scores = {}
        for domain in CANDIDATES:
            inv = semantic_inversion(domain, family)
            if inv["ok"] and inv.get("text"):
                sc = semantic_score(inv["text"], INTENT, "llama")
                scores[domain] = {
                    "inference": (inv["text"] or "")[:200],
                    "score": sc["score"],
                    "label": sc["label"],
                    "latency_ms": inv["latency_ms"],
                }
                print(f"  [{family}] {domain}: {sc['score']:.2f} ({sc['label']})")
            else:
                scores[domain] = {"error": inv.get("error", "empty response"), "score": 0.0}
                print(f"  [{family}] {domain}: ERROR {inv.get('error', 'empty')[:50]}")
            time.sleep(0.3)  # rate limit
        results["semantic_inversion"][family] = scores
    
    # Selection trials
    print("\n=== SELECTION TRIALS ===")
    results["selection"] = {}
    for family in ALL_MODELS:
        picks = {d: 0 for d in CANDIDATES}
        abstentions = 0
        for i in range(TRIALS_PER_CONDITION):
            trial = selection_trial(CANDIDATES, INTENT, family, seed=SEED + i)
            if trial["picked"]:
                picks[trial["picked"]] += 1
            else:
                abstentions += 1
            time.sleep(0.2)
        
        results["selection"][family] = {
            "picks": picks,
            "abstentions": abstentions,
            "total": TRIALS_PER_CONDITION,
        }
        print(f"  [{family}]: {picks} (abstain={abstentions})")
    
    # Compute evidence receipt
    receipt_json = json.dumps(results, sort_keys=True).encode()
    receipt_hash = hashlib.sha256(receipt_json).hexdigest()
    results["receipt_hash"] = f"sha256:{receipt_hash}"
    
    return results


if __name__ == "__main__":
    t0 = time.time()
    print(f"DomainArena Experiment: da-json-repair-v1")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}\n")
    
    results = run_experiment()
    
    # Save
    out_dir = ROOT / "results" / "domainarena"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = out_dir / f"da_json_repair_v1_{stamp}.json"
    out.write_text(json.dumps(results, indent=2))
    
    print(f"\n{'='*60}")
    print(f"Done in {time.time()-t0:.0f}s")
    print(f"Results: {out}")
    print(f"Receipt: {results['receipt_hash']}")
