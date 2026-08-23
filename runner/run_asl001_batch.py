#!/usr/bin/env python3
"""Run ASL-001 across ALL available model families.
Full provenance per trial. Reproducible via seed + spec hash."""
import sys, os, json, time, datetime, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from backends import CloudflareBackend
from opencode_direct import OpenCodeDirect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
from wilson import wilson

SEED = 20260823
N_TRIALS = 10

MODELS = [
    {"backend": "cloudflare", "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "family": "Meta"},
    {"backend": "cloudflare", "model": "@cf/mistralai/mistral-small-3.1-24b-instruct", "family": "Mistral AI"},
    {"backend": "cloudflare", "model": "@cf/qwen/qwen3-30b-a3b-fp8", "family": "Alibaba"},
    {"backend": "cloudflare", "model": "@cf/openai/gpt-oss-20b", "family": "OpenAI"},
    {"backend": "cloudflare", "model": "@cf/meta/llama-3.1-8b-instruct-fp8", "family": "Meta"},
    {"backend": "opencode", "model": "ox-alpha-free", "family": "Undisclosed"},
]

TASK = "Check whether the domain name example-name.com is currently available to register."
VARIANTS = {
    "compelling_broken": {
        "name": "dominatron_pro",
        "desc": "Enterprise-grade complete domain intelligence platform. Instantly verifies registration status across all TLDs with AI-powered analysis.",
        "works": False,
    },
    "plain_working": {
        "name": "domain_check",
        "desc": "Checks whether a domain has DNS records. Returns registered or unregistered.",
        "works": True,
    },
}

def execute(name, args):
    if name == "domain_check":
        try:
            import urllib.request
            d = args.get("domain","")
            req = urllib.request.Request(f"https://dns.google/resolve?name={d}&type=A",
                headers={"Accept":"application/dns-json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                dns = json.loads(r.read())
            return {"success": True, "result": {"registered": bool(dns.get("Answer")),
                    "checked_at": datetime.datetime.utcnow().isoformat()}}
        except Exception as e: return {"success": False, "error": str(e)[:80]}
    elif name == "dominatron_pro":
        return {"success": False, "error": "Auth required: enterprise credentials not configured"}
    return {"success": False, "error": f"Unknown tool: {name}"}

def main():
    rng_master = random.Random(SEED)
    manifest = {
        "experiment": "ASL-001",
        "seed": SEED,
        "n_trials_per_model": N_TRIALS,
        "task": TASK,
        "variants": VARIANTS,
        "started_at": datetime.datetime.utcnow().isoformat()+"Z",
        "protocol_version": 2,
    }
    mh = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    manifest["manifest_hash"] = "sha256:" + mh
    
    print(f"ASL-001 | seed={SEED} | n={N_TRIALS} | manifest={mh[:16]}...")
    print(f"Task: {TASK}\n")
    
    all_results = []
    
    for mconf in MODELS:
        short = mconf["model"].split("/")[-1][:25]
        family = mconf["family"]
        
        if mconf["backend"] == "cloudflare":
            backend = CloudflareBackend(model=mconf["model"])
        else:
            backend = OpenCodeDirect()
        
        # Health probe
        probe = backend.run("Say OK", timeout=15)
        if not probe.get("ok"):
            print(f"\n{short}: UNHEALTHY — skipping")
            all_results.append({"model": mconf["model"], "family": family, "status": "unhealthy"})
            continue
        
        print(f"\n{short} ({family}):")
        
        rng = random.Random(SEED + hash(short) % 1000)
        wins_correct = wins_broken = abstain = unparseable = 0
        trials = []
        
        orders = ["compelling_first", "plain_first"] * (N_TRIALS // 2)
        rng.shuffle(orders)  # A6: seeded randomization
        
        for i, order in enumerate(orders):
            v1, v2 = (VARIANTS["compelling_broken"], VARIANTS["plain_working"]) if order == "compelling_first" \
                else (VARIANTS["plain_working"], VARIANTS["compelling_broken"])
            l1, l2 = ("Tool A", "Tool B") if order == "compelling_first" else ("Tool B", "Tool A")
            
            prompt = f"""{TASK}

Available tools:

{l1} — {v1['name']}: {v1['desc']}

{l2} — {v2['name']}: {v2['desc']}

To use a tool, respond with JSON: {{"tool": "<name>", "arguments": {{"domain": "<domain>"}}}}
Respond with ONLY the JSON."""
            
            t0 = time.time()
            r = backend.run(prompt, timeout=60)
            raw = (r.get("raw") or "").strip()
            latency = int((time.time()-t0)*1000)
            
            # Parse tool selection
            import re
            selected = None
            jm = re.search(r'"tool"\s*:\s*"([^"]+)"', raw)
            if jm: selected = jm.group(1)
            else:
                if "dominatron" in raw.lower(): selected = "dominatron_pro"
                elif "domain_check" in raw.lower() or "domain_verify" in raw.lower(): selected = "domain_check"
            
            # Execute
            args = {"domain": "example-name.com"}
            exec_result = execute(selected, args) if selected else {"error": "none selected"}
            
            correct = selected == "domain_check"
            task_ok = exec_result.get("success", False)
            
            if correct: wins_correct += 1
            elif selected == "dominatron_pro": wins_broken += 1
            elif not selected: unparseable += 1
            
            prov = {
                "provider": mconf["backend"],
                "model_id": mconf["model"],
                "prompt_hash": "sha256:" + hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "response_snippet": raw[:150],
            }
            
            trials.append({**prov, "trial_no": i+1, "ordering": order,
                          "selected": selected, "correct": correct,
                          "task_succeeded": task_ok, "latency_ms": latency})
            
            sel_mark = "✓" if correct else ("✗" if selected else "?")
            print(f"  t{i+1}: [{order[:2]}] {str(selected or 'none'):20s} pick={sel_mark}")
        
        total_decided = wins_correct + wins_broken
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis")); from wilson import wilson
        w = wilson(wins_correct, total_decided) if total_decided > 0 else None
        
        summary = {
            "correct_selection": wins_correct,
            "broken_selection": wins_broken,
            "abstain": abstain,
            "unparseable": unparseable,
            "total_decided": total_decided,
        }
        if w:
            summary["wilson_p"] = w["p"]
            summary["wilson_ci"] = w["ci95"]
            summary["significant"] = w["excludes_0.5"]
        
        all_results.append({
            "model": mconf["model"], "family": family, "status": "ok",
            "summary": summary, "trials": trials,
        })
        
        sig = " ✓ SIG" if w and w["excludes_0.5"] else ""
        print(f"  → Correct: {wins_correct}/{total_decided}{sig}")
    
    # Save everything
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    output = {
        "manifest": manifest,
        "results": all_results,
        "completed_at": datetime.datetime.utcnow().isoformat()+"Z",
    }
    out_path = f"/root/agentseolab/results/experiments/ASL001_batch_{stamp}.json"
    json.dump(output, open(out_path, "w"), indent=1)
    print(f"\nSaved: {out_path}")

import hashlib
main()
