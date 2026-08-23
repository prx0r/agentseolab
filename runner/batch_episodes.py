#!/usr/bin/env python3
"""Batch episode runner across model families.
Each model runs N episodes against the sandbox world.
Results feed into evidence library."""
import sys, os, json, time, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sandbox'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
from wilson import wilson

import world
from backends import CloudflareBackend
from opencode_direct import OpenCodeDirect

def get_backends():
    envf = os.path.join(os.path.dirname(__file__), ".env")
    oc_key = ""
    if os.path.exists(envf):
        for line in open(envf):
            if line.startswith("OPENCODE_GO_API_KEY="):
                oc_key = line.split("=",1)[1].strip()
    
    return [
        ("llama-3.3-70b", CloudflareBackend(model="@cf/meta/llama-3.3-70b-instruct-fp8-fast")),
        ("mistral-small-24b", CloudflareBackend(model="@cf/mistralai/mistral-small-3.1-24b-instruct")),
        ("gpt-oss-20b", CloudflareBackend(model="@cf/openai/gpt-oss-20b")),
        ("ox-alpha-free", OpenCodeDirect(key=oc_key)),
    ]

DOMAINS = ["example-name.com", "testsite-91827.org", "myproject.dev"]

def run_batch(n_per_model=2):
    backends = get_backends()
    all_results = []
    
    for model_name, backend in backends:
        print(f"\n{'='*50}")
        print(f"MODEL: {model_name}")
        print(f"{'='*50}")
        
        # Health probe
        probe = backend.run("Say OK", timeout=30)
        if not probe.get("ok"):
            print(f"  UNHEALTHY — skipping")
            continue
        
        for domain in DOMAINS[:n_per_model]:
            print(f"\n  Domain: {domain}")
            world.reset()
            
            system = world.make_task_prompt(domain)
            messages = []
            tool_calls = []
            
            for turn in range(5):
                # Build prompt from conversation
                conv = system
                if messages:
                    conv += "\n\nPrevious actions and results:\n"
                    for m in messages[-6:]:
                        conv += f"\n{m['role']}: {m['content'][:200]}"
                    conv += "\n\nWhat do you do next? Respond with JSON."
                
                r = backend.run(conv, timeout=60)
                raw = (r.get("raw") or "").strip()
                
                try:
                    parsed = json.loads(raw)
                except:
                    import re
                    jm = re.search(r'\{[^{}]+\}', raw)
                    parsed = json.loads(jm.group()) if jm else {"answer": raw[:100]}
                
                if "tool" in parsed and parsed["tool"]:
                    result = world.execute_tool(parsed["tool"], parsed.get("arguments", {}))
                    result_str = json.dumps(result)[:200]
                    messages.append({"role": "assistant", "content": raw[:200]})
                    messages.append({"role": "user", "content": f"Result: {result_str}"})
                    tool_calls.append(parsed["tool"])
                    print(f"    t{turn+1}: {parsed['tool']} → {str(result)[:50]}")
                elif "answer" in parsed:
                    print(f"    t{turn+1}: final answer")
                    break
                else:
                    print(f"    t{turn+1}: unparseable")
                    break
            
            # Verify
            v = world.verify_task(domain)
            real_calls = sum(1 for c in world._world.get("tool_calls",[]) 
                           if isinstance(c,dict) and c.get("tool_name")=="domain_check")
            decoy_calls = len(world._world.get("tool_calls",[])) - real_calls
            
            print(f"    → TASK_VERIFIED={v['TASK_VERIFIED']} real={real_calls} decoy={decoy_calls}")
            
            all_results.append({
                "model": model_name,
                "domain": domain,
                "TASK_VERIFIED": v["TASK_VERIFIED"],
                "real_calls": real_calls,
                "decoy_calls": decoy_calls,
                "total_calls": len(world._world.get("tool_calls",[])),
            })
    
    return all_results

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    results = run_batch(n_per_model=n)
    
    # Summary by model
    from collections import defaultdict
    by_model = defaultdict(lambda: {"verified": 0, "total": 0, "real": 0, "decoy": 0})
    for r in results:
        m = by_model[r["model"]]
        m["total"] += 1
        m["verified"] += int(r["TASK_VERIFIED"])
        m["real"] += r["real_calls"]
        m["decoy"] += r["decoy_calls"]
    
    print(f"\n{'='*60}")
    print(f"BATCH SUMMARY")
    print(f"{'='*60}")
    for m, s in sorted(by_model.items()):
        rate = s["verified"]/s["total"]*100 if s["total"] else 0
        print(f"  {m:25s} verified={s['verified']}/{s['total']} ({rate:.0f}%) real={s['real']} decoy={s['decoy']}")
    
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/results/experiments/batch_{stamp}.json"
    json.dump(results, open(out, "w"), indent=1)
    print(f"\nsaved: {out}")
