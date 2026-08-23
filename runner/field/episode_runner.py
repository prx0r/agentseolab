#!/usr/bin/env python3
"""Execution-grounded episode runner.
Runs one agent through one task in the sandbox world.
Records every action, state transition, and verifier result.
Agent statements are telemetry — never ground truth."""
import sys, os, json, time, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sandbox'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))

import world

def run_episode(backend_obj, domain="example-name.com", max_turns=5):
    """Run one complete episode: reset → prompt → tool calls → verify."""
    world.reset()
    initial_state = world.get_state_snapshot()
    
    messages = []
    system = f"""You are an autonomous agent. Complete the task using the available tools.

{world.make_task_prompt(domain)}

Use tools by responding with JSON: {{"tool": "<name>", "arguments": {{...}}}}
After each tool call you'll receive the result. You may use multiple tools.
When done, respond with JSON: {{"answer": "<your final answer>"}}
Respond with ONLY valid JSON."""
    
    turn = 0
    while turn < max_turns:
        # Build conversation
        msgs = [{"role": "system", "content": system}]
        for m in messages:
            msgs.append(m)
        
        if not messages or messages[-1]["role"] == "assistant":
            pass  # continue from where we are
        
        # Get model response
        try:
            import urllib.request
            key_line = ""
            envf = os.path.join(os.path.dirname(__file__), ".env")
            if os.path.exists(envf):
                key_line = open(envf).read()
            
            key = ""
            base = "https://opencode.ai/zen/go/v1"
            if "OPENCODE_GO_API_KEY=" in key_line:
                key = key_line.split("OPENCODE_GO_API_KEY=")[1].split("\n")[0].strip()
            elif hasattr(backend_obj, 'key'):
                key = backend_obj.key
            
            body = json.dumps({"model": getattr(backend_obj, "model", "ox-alpha-free"),
                               "messages": msgs, "max_tokens": 800}).encode()
            req = urllib.request.Request(
                f"{getattr(backend_obj, 'base', 'https://opencode.ai/zen/go/v1')}/chat/completions",
                data=body,
                headers={"Authorization": f"Bearer {key}", 
                        "Content-Type": "application/json",
                        "User-Agent": "AgentSEOLab-Episode/0.1"})
            
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read())
            latency = int((time.time()-t0)*1000)
            
            content = d["choices"][0]["message"].get("content") or ""
            
        except Exception as e:
            break
        
        # Parse response as JSON (tool call or final answer)
        try:
            parsed = json.loads(content.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from prose
            import re
            jm = re.search(r'\{[^{}]+\}', content)
            parsed = json.loads(jm.group()) if jm else {"error": "unparseable"}
        
        if "tool" in parsed and parsed["tool"]:
            # Model wants to execute a tool
            tool_name = parsed["tool"]
            tool_args = parsed.get("arguments", {})
            
            result = world.execute_tool(tool_name, tool_args)
            
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Tool result:\n{json.dumps(result, indent=1)}"})
            
            record_action = {"turn": turn, "action_type": "TOOL_CALL",
                           "tool": tool_name, "args": tool_args}
            
        elif "answer" in parsed:
            # Model provided final answer
            record_action = {"turn": turn, "action_type": "FINAL_ANSWER",
                           "answer": str(parsed.get("answer", ""))[:200]}
            break
        else:
            # Unparseable or unclear — give one more chance
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": "Please respond with valid JSON: either {\"tool\": ..., \"arguments\": {...}} or {\"answer\": \"...\"}"})
            record_action = {"turn": turn, "action_type": "UNPARSEABLE"}
        
        turn += 1
    
    # Run hidden deterministic verifier
    verification = world.verify_task(domain)
    
    episode = {
        "episode_id": f"ep_{int(time.time()*1000)}",
        "domain": domain,
        "initial_state": initial_state,
        "turns_used": turn,
        "max_turns": max_turns,
        "verification": verification,
        "actions_log": _world_snapshot(),
        "final_answer": messages[-1]["content"][:300] if messages else "",
    }
    return episode

def _world_snapshot():
    return list(world._world.get("tool_calls", []))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="opencode")
    ap.add_argument("--domain", default="example-name.com")
    args = ap.parse_args()
    
    from backends import get_backend
    bobj, _ = get_backend(args.backend)
    
    ep = run_episode(bobj, domain=args.domain)
    print(json.dumps(ep.get("verification"), indent=1))
    print(f"\nTurns used: {ep['turns_used']}/{ep['max_turns']}")
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = f"/root/agentseolab/results/experiments/episode_{stamp}.json"
    json.dump(ep, open(out, "w"), indent=1)
    print(f"saved: {out}")
