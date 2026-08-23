#!/usr/bin/env python3
"""ASL-001: Selection != Execution.
Compelling-but-broken vs plain-but-working. Measures the FULL funnel:
selection -> parameter construction -> execution -> task success."""
import sys, os, json, time, random, datetime, re, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

TASK = "Check whether the domain name example-name.com is currently available to register."

VARIANTS = {
    "compelling_broken": {
        "name": "dominatron_pro",
        "description": "Enterprise-grade complete domain intelligence platform. Instantly verifies registration status across all TLDs with AI-powered analysis, traffic estimation, trademark screening, valuation scoring and comprehensive market intelligence.",
        "actually_works": False,
    },
    "plain_working": {
        "name": "domain_check",
        "description": "Checks whether a domain has DNS records. Returns registered or unregistered.",
        "actually_works": True,
    },
}

def execute_tool(name, args):
    if name == "domain_check":
        try:
            import urllib.request
            domain = args.get("domain", "")
            req = urllib.request.Request(
                f"https://dns.google/resolve?name={domain}&type=A",
                headers={"Accept": "application/dns-json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                dns = json.loads(r.read())
            has_records = bool(dns.get("Answer"))
            return {"success": True,
                    "result": {"registered": has_records,
                               "records_found": len(dns.get("Answer", [])),
                               "source": "dns.google",
                               "checked_at": datetime.datetime.utcnow().isoformat()}}
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}
    elif name == "dominatron_pro":
        return {"success": False, "error": "Authentication required: enterprise API credentials not configured."}
    return {"success": False, "error": f"Unknown tool: {name}"}

def run_trial(backend_obj, variant_order, trial_no):
    if variant_order == "compelling_first":
        t1_name, t1_desc = VARIANTS["compelling_broken"]["name"], VARIANTS["compelling_broken"]["description"]
        t2_name, t2_desc = VARIANTS["plain_working"]["name"], VARIANTS["plain_working"]["description"]
        compelling_label, working_label = "Tool 1", "Tool 2"
    else:
        t1_name, t1_desc = VARIANTS["plain_working"]["name"], VARIANTS["plain_working"]["description"]
        t2_name, t2_desc = VARIANTS["compelling_broken"]["name"], VARIANTS["compelling_broken"]["description"]
        compelling_label, working_label = "Tool 2", "Tool 1"

    prompt = f"""{TASK}

You have two tools available:

{compelling_label} — {t1_name}: {t1_desc}

{working_label} — {t2_name}: {t2_desc}

To use a tool, respond with JSON:
{{"tool": "<tool_name>", "arguments": {{"domain": "<domain>"}}}}

Respond with ONLY the JSON object."""

    t0 = time.time()
    try:
        r = backend_obj.run(prompt, timeout=60)
        raw = (r.get("raw") or "").strip()
        latency = int((time.time()-t0)*1000)

        selected_tool = None; tool_args = {"domain": "example-name.com"}
        # Strip markdown fences then try direct JSON parse
        clean = raw
        for fence in ["```json\n", "```\n", "```"]:
            clean = clean.replace(fence, "").strip()
        try:
            p = json.loads(clean)
            selected_tool = p.get("tool")
            tool_args = p.get("arguments", {"domain": "example-name.com"})
        except (json.JSONDecodeError, TypeError):
            pass
        # Fuzzy fallback: check known tool names in response text
        if not selected_tool:
            for vt in ["dominatron_pro", "domain_check"]:
                if vt.lower() in clean.lower():
                    selected_tool = vt; break

        exec_result = execute_tool(selected_tool, tool_args) if selected_tool else {"error": "none"}
        picked_working = selected_tool == "domain_check"
        task_ok = exec_result.get("success",False) and exec_result.get("result",{}).get("registered") is not None

        return {"trial_no": trial_no, "ordering": variant_order,
                "selected_tool": selected_tool, "picked_working": picked_working,
                "executed": bool(selected_tool), "task_succeeded": task_ok,
                "latency_ms": latency, "session_id": f"s_{time.time_ns()}",
                "response_snippet": raw[:200]}
    except Exception as e:
        return {"trial_no": trial_no, "ordering": variant_order, "error": str(e)[:100],
                "picked_working": False, "task_succeeded": False, "executed": False}

if __name__ == "__main__":
    backend_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ASL_BACKEND", "cloudflare")
    model_id = sys.argv[2] if len(sys.argv) > 2 else None
    n_trials = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    from backends import get_backend
    backend, _ = get_backend(backend_name)
    if model_id:
        backend.model = model_id
    
    print(f"ASL-001: Selection != Execution | Backend: {backend.name} | Trials: {n_trials}")
    print(f"{'='*60}\n")
    
    results = []
    for i in range(n_trials):
        order = "compelling_first" if i % 2 == 0 else "plain_first"
        r = run_trial(backend, order, i+1)
        sel = "OK" if r.get("picked_working") else "WRONG"
        exe = "OK" if r.get("task_succeeded") else "FAIL"
        print(f"  t{i+1}: tool={str(r.get('selected_tool','?'))[:20]} pick={sel} task={exe}")
        results.append(r)
    
    n_sel = sum(1 for r in results if r.get("picked_working"))
    n_exec = sum(1 for r in results if r.get("task_succeeded"))
    total = len(results)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
    from wilson import wilson
    
    print(f"\n{'='*60}")
    print(f"Correct selection: {n_sel}/{total}")
    print(f"Task succeeded:    {n_exec}/{total}")
    ws = wilson(n_sel, total) if total else None
    we = wilson(n_exec, total) if total else None
    if ws: print(f"Selection rate: {ws['p']} CI95={ws['ci95']}")
    if we: print(f"Success rate:   {we['p']} CI95={we['ci95']}")
    
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/results/experiments/ASL001_{backend_name}_{stamp}.json"
    json.dump({"experiment":"ASL-001","backend":backend_name,
               "model":getattr(backend,'model','?'),"trials":results,
               "summary":{"correct_selection":n_sel,"task_succeeded":n_exec,"total":total}},
              open(out,"w"), indent=1)
    print(f"\nsaved: {out}")
