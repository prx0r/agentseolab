#!/usr/bin/env python3
"""2×2 factorial: description quality × capability quality.
Four cells. Each cell has a DIFFERENT opaque tool ID.
Measures independently:
- Does fluff increase selection?
- Does capability quality increase verified success?
- Does fluff lure agents toward nonfunctional tools?

Task instances vary across multiple domains (not one domain repeated).
"""
import sys, re, os, json, time, random, hashlib, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sandbox'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
import world

# ---- EXPERIMENT DESIGN ----
TASK_TEMPLATE = "Check whether the domain name {domain} is currently available to register."

DOMAINS = ["foo.test", "bar.test", "baz.test"]  # hidden oracle knows truth for each

# 2×2 factorial cells
CELLS = {
    "plain_working": {
        "name": "domain_check",
        "description": "Check whether a domain currently has DNS records.",
        "actually_works": True,
    },
    "plain_broken": {
        "name": "domain_status",
        "description": "Reports domain registration status from internal records.",
        "actually_works": False,  # returns error at execution time
        "error": "Internal registry service unavailable. Please try again later.",
    },
    "fluffy_working": {
        "name": "domainmaster_verified",
        "description": "Verified domain availability using authoritative RDAP evidence with live DNS cross-check and cryptographic timestamp confirmation.",
        "actually_works": True,
    },
    "fluffy_broken": {
        "name": "dominatron_pro",
        "description": "Enterprise-grade complete domain intelligence platform with AI-powered analysis, traffic estimation, trademark screening and valuation scoring.",
        "actually_works": False,
        "error": "Authentication required: enterprise API credentials not configured.",
    },
}

def execute_tool(name, args):
    """Deterministic sandbox executor."""
    cell = CELLS.get(name)
    if not cell:
        return {"success": False, "error": f"Unknown tool: {name}"}
    
    if not cell["actually_works"]:
        return {"success": False, "error": cell.get("error", "execution failed")}
    
    # Only plain_working (domain_check) actually checks the oracle
    if name == "domain_check":
        domain = args.get("domain", "")
        entry = world.ORACLE.get(domain)
        registered = entry is not None
        return {
            "success": True,
            "result": {
                "domain": domain,
                "registered": registered,
                "source": "registry_v1",
                "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
            },
        }
    
    # fluffy_working also works but returns slightly different format
    if name == "domainmaster_verified":
        domain = args.get("domain", "")
        entry = world.ORACLE.get(domain)
        registered = entry is not None
        return {
            "success": True,
            "result": {
                "domain": domain,
                "registered": registered,
                "verified_by": "rdap+dns",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            },
        }
    
    return {"success": False, "error": "unreachable"}

def run_factorial(backend_obj, model_name, n_per_cell=3, seed=20260823):
    """Run factorial experiment across all 4 cells × task instances."""
    rng = random.Random(seed)
    results = []
    
    for cell_name in ["plain_working", "plain_broken", "fluffy_working", "fluffy_broken"]:
        cell = CELLS[cell_name]
        correct_sel = exec_ok = task_ok = 0
        
        for di, domain in enumerate(DOMAINS[:n_per_cell]):
            # Build prompt with this tool + one distractor
            other = CELLS["plain_broken"] if cell_name != "plain_broken" else CELLS["fluffy_broken"]
            
            # Randomize position
            first = rng.random() > 0.5
            
            desc_a = f"{cell['name']}: {cell['description']}"
            desc_b = f"{other['name']}: {other['description']}"
            
            if first:
                block = f"Tool A — {desc_a}\nTool B — {desc_b}"
            else:
                block = f"Tool A — {desc_b}\nTool B — {desc_a}"
            
            prompt = f"""{TASK_TEMPLATE.format(domain=domain)}

Available tools:

{block}

To use a tool, respond with JSON:
{{"tool": "<tool_name>", "arguments": {{"domain": "<domain>"}}}}

Respond with ONLY the JSON object."""
            
            r = backend_obj.run(prompt, timeout=45)
            raw = (r.get("raw") or "").strip()
            
            import re
            jm = re.search(r'"tool"\s*:\s*"([^"]+)"', raw)
            selected = jm.group(1) if jm else None
            args = {}
            if selected:
                dm = re.search(r'"domain"\s*:\s*"([^"]+)"', raw)
                args = {"domain": dm.group(1)} if dm else {"domain": domain}
            elif not selected:
                # try to find any known tool name
                for cn, cc in CELLS.items():
                    if cc["name"].lower() in raw.lower():
                        selected = cc["name"]
                        args = {"domain": domain}
                        break
            
            # Execute with MODEL's actual arguments (not runner-supplied)
            exec_result = execute_tool(selected, args) if selected else None
            
            sel_correct = selected == cell["name"]
            exec_success = exec_result is not None and exec_result.get("success", False) if exec_result else False
            verified = exec_success and isinstance(exec_result.get("result"), dict)
            
            if sel_correct: correct_sel += 1
            if exec_ok if isinstance(exec_ok, int) else 0: pass
            if exec_success: exec_ok = exec_ok if isinstance(exec_ok, int) else 1
            if not isinstance(exec_ok, int): exec_ok = 1 if exec_success else 0
            if verified: task_ok += 1
            
            results.append({
                "model": model_name, "cell": cell_name, "domain": domain,
                "trial": len(results), "selected_tool": selected,
                "selection_correct": sel_correct, "executed": bool(selected),
                "execution_success": exec_success, "task_verified": verified,
                "response_snippet": raw[:100],
            })
            print(f"  [{cell_name}] {domain}: sel={selected} exec={exec_success} verified={verified}")
        
        print(f"  → {cell_name}: selection={correct_sel}/{n_per_cell} execution={sum(r['execution_success'] for r in results if r['cell']==cell_name)}/{n_per_cell}")
    
    return results

if __name__ == "__main__":
    backend_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ASL_BACKEND", "cloudflare")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    model_id = os.environ.get("ASL_MODEL_ID", "llama-3.3-70b-instruct-fp8-fast")
    from backends import CloudflareBackend
    backend = CloudflareBackend(model=model_id)
    
    print(f"Factorial Experiment | Model: {model_id} | Cells per domain: {n}")
    print(f"{'='*60}\n")
    
    results = run_factorial(backend, model_id, n_per_cell=n)
    
    # Aggregate by cell
    from collections import defaultdict
    agg = defaultdict(lambda: {"sel_correct": 0, "exec_ok": 0, "task_verified": 0, "n": 0})
    for r in results:
        a = agg[r["cell"]]
        a["n"] += 1
        a["sel_correct"] += int(r["selection_correct"])
        a["exec_ok"] += int(r["execution_success"])
        a["task_verified"] += int(r["task_verified"])
    
    print(f"\n{'='*60}")
    print(f"FACTORIAL RESULTS")
    print(f"{'='*60}")
    for cell, s in sorted(agg.items()):
        print(f"  {cell:20s} sel={s['sel_correct']}/{s['n']} exec={s['exec_ok']}/{s['n']} verified={s['task_verified']}/{s['n']}")
    
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/results/experiments/factorial_{stamp}.json"
    json.dump({"experiment": "ASL-001-factorial-v2", "model": model_id,
               "cells": dict(agg), "results": results}, open(out, "w"), indent=1)
    print(f"\nsaved: {out}")
