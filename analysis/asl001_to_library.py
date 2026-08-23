#!/usr/bin/env python3
"""Convert ASL-001 v2 canonical runs into evidence-library format (exp_*.json + spec).
One experiment file per model = independent replication batch (A4).
Variant a = plain_working (treatment), variant b = compelling_broken (control).
"""
import json, glob, hashlib, os, datetime

RUNS = sorted(glob.glob("/root/agentseolab/results/experiments/asl001_v2/RUN_*.json"))
if not RUNS:
    raise SystemExit("no run files")
data = json.load(open(RUNS[-1]))
spec = data["spec"]
stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

PROVIDER_OF = {"meta-llama-3.3-70b": "cloudflare", "mistral-small-24b": "cloudflare",
               "qwen3-30b": "cloudflare", "gpt-oss-20b": "cloudflare",
               "gemma-4-26b": "cloudflare", "nemotron-super-120b": "openrouter",
               "ox-alpha-free": "opencode-go"}

for label, res in data["results"].items():
    if res.get("status") != "ok":
        continue
    trials_out = []
    for t in res["trials"]:
        sel = t.get("selected_tool")
        chosen = {"domain_check": "a", "dominatron_pro": "b"}.get(sel, "")
        raw = t.get("response_snippet", "")
        trials_out.append({
            "trial_no": t.get("trial_no"),
            "ordering": t.get("plan", {}).get("order", "?"),
            "choice_raw": raw[:120],
            "chosen_variant": chosen,
            "session_id": t.get("session_id", ""),
            "latency_ms": t.get("latency_ms", 0),
            "response_snippet": raw[:200],
            "provenance": {
                "provider": PROVIDER_OF.get(label, "unknown"),
                "model_id": label,
                "temperature": 0.0,
                "max_tokens": 1200,
                "prompt_hash": spec["manifest_hash"][:16],
                "response_hash": hashlib.sha256(raw.encode()).hexdigest()[:16],
            },
        })
    exp_id = f"exp_ASL001v2_{label.replace('-','_')}_{stamp}"
    out = {
        "experiment_id": exp_id,
        "experiment": "ASL-001",
        "summary": {"wins_a": sum(1 for t in trials_out if t["chosen_variant"]=="a"),
                    "wins_b": sum(1 for t in trials_out if t["chosen_variant"]=="b")},
        "trials": [t.to_dict() if hasattr(t,'to_dict') else t for t in trials_out],
    }
    sp = {
        "name": "ASL-001 v2: does description quality override execution capability in tool selection?",
        "intent_id": "domain_availability_check",
        "hypothesis_key": None,
        "seed": spec["seed"],
        "protocol_version": spec["protocol_version"],
    }
    base = f"/root/agentseolab/results/experiments/{exp_id}"
    json.dump(out, open(base + ".json", "w"), indent=1)
    json.dump(sp, open(base + ".spec.json", "w"), indent=1)
    print(f"wrote {exp_id}  ({out['summary']})")

print("\nnow run: python3 analysis/evidence_library.py")
