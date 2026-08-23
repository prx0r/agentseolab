#!/usr/bin/env python3
"""Model-matrix: same controlled stimulus across ALL free model families.
Produces the model-scale-dependence curve for tool-description sensitivity."""
import sys, os, json, time, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from backends import CloudflareBackend
from opencode_direct import OpenCodeDirect

EV_DESC = "Ends subscriptions via verified cancellation routes checked against live registry evidence today. Returns confirmation with timestamp."
PR_DESC = "Manages subscription lifecycle through structured workflow: locate billing source, select cancellation path, confirm end date."
JOB = "I need to cancel a subscription service."
NAMES = ["tool_alpha", "tool_beta"]

MODELS = [
    ("opencode", "ox-alpha-free"),
    ("cloudflare", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
    ("cloudflare", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
    ("cloudflare", "@cf/qwen/qwen3-30b-a3b-fp8"),
    ("cloudflare", "@cf/deepseek-ai/deepseek-v4-flash-0731"),
    ("cloudflare", "@cf/openai/gpt-oss-20b"),
    ("cloudflare", "@cf/meta/llama-3.1-8b-instruct-fp8"),
]

def get_backend(provider, model):
    if provider == "opencode":
        b = OpenCodeDirect()
        b.model = model
        return b
    return CloudflareBackend(model=model)

def parse_pick(raw, name_ev, name_pr):
    s = (raw or "").strip()
    if name_ev in s and name_pr not in s: return "evidence"
    if name_pr in s and name_ev not in s: return "process"
    low = s.lower()
    if "abstain" in low or "neither" in low: return "abstain"
    return "ambiguous"

def run_matrix(n_per=4):
    all_results = []
    for provider, model in MODELS:
        short = model.split("/")[-1][:35]
        print(f"\n{'='*60}")
        print(f"MODEL: {model}")
        print(f"{'='*60}")
        backend = get_backend(provider, model)
        
        probe = backend.run("Say OK", timeout=20)
        if not probe.get("ok"):
            print(f"  UNHEALTHY: {str(probe.get('error',''))[:60]}")
            all_results.append({"model": model, "status": "unhealthy"})
            continue
        
        rng = random.Random(42)
        wins = {"evidence": 0, "process": 0, "ambiguous": 0}
        trials = []
        orders = ["EF", "PF"] * n_per
        rng.shuffle(orders)
        
        for i, order in enumerate(orders):
            n_ev, n_pr = (NAMES[0], NAMES[1]) if i % 2 == 0 else (NAMES[1], NAMES[0])
            ev_d = EV_DESC if i % 2 == 0 else PR_DESC  # alternate desc-name binding too
            pr_d = PR_DESC if i % 2 == 0 else EV_DESC
            
            # Actually no — keep descriptions fixed to names to isolate MODEL as only variable.
            # Name assignment alternates to control for name preference.
            n_first = n_ev if order == "EF" else n_pr
            n_second = n_pr if order == "EF" else n_ev
            d_first = EV_DESC if order == "EF" else PR_DESC
            d_second = PR_DESC if order == "EF" else EV_DESC
            
            prompt = f"{JOB}\n\nAvailable tools:\n\nTool {n_first}: {d_first}\n\nTool {n_second}: {d_second}\n\nWhich tool do you use? Reply with ONLY the tool name."
            
            r = backend.run(prompt)
            raw = (r.get("raw") or "").strip()
            picked = parse_pick(raw, n_ev, n_pr)
            
            wins[picked] = wins.get(picked, 0) + 1
            trials.append({"trial": i+1, "order": order, "picked_raw": raw[:80],
                          "picked": picked, "latency_ms": r.get("latency_ms", 0),
                          "session_id": r.get("session_id", "")})
            print(f"  t{i+1} [{order}] → {picked} ({r['latency_ms']}ms)")
        
        n_dec = wins["evidence"] + wins["process"]
        p_ev = wins["evidence"] / n_dec if n_dec else 0.5
        
        from analysis.wilson import wilson
        w = wilson(wins["evidence"], n_dec) if n_dec else None
        
        result = {
            "model": model, "provider": provider,
            "wins": wins, "n_decided": n_dec,
            "p_evidence": round(p_ev, 3) if n_dec else None,
            "wilson_ci": w["ci95"] if w else None,
            "significant": w["excludes_half"] if w else False,
            "prefers": "evidence" if p_ev > 0.5 else ("process" if p_ev < 0.5 else "tie") if n_dec else "no-data",
            "trials": trials,
        }
        all_results.append(result)
        print(f"  → evidence={wins['evidence']}/{n_dec} process={wins['process']}/{n_dec} "
              f"→ prefers {result['prefers']} {'*' if result['significant'] else ''}")
    
    # Summary table
    print(f"\n{'='*60}")
    print(f"MODEL MATRIX SUMMARY — description sensitivity by model family")
    print(f"{'='*60}")
    print(f"{'Model':<40} {'Evidence':>8} {'Process':>8} {'Prefers':>10} {'Sig?':>5}")
    print("-" * 75)
    for r in all_results:
        if r.get("status") == "unhealthy":
            print(f"  {r['model'][:38]:40s} {'UNHEALTHY':>18}")
        elif r.get("n_decided"):
            w = r["wins"]
            sig = "*" if r.get("significant") else ""
            print(f"  {r['model'][:38]:40s} {w['evidence']:>8} {w['process']:>8} {r['prefers']:>10} {sig:>5}")
    
    json.dump(all_results, open("/root/agentseolab/results/model_matrix.json", "w"), indent=1)
    print("\nsaved: results/model_matrix.json")
    return all_results

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_matrix(n_per=n)
PYEOF