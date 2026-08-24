#!/usr/bin/env python3
"""Agent loop: wake every 60s, review state, act autonomously.

Each tick:
  1. Read queue + git status + recent results + watchdog log
  2. Ask the cheapest capable model to decide ONE next action
  3. Execute that action (run experiment / write runner / fix bug / commit)
  4. Log to results/agent_loop/tick_*.json + journal

Run:  nohup bash -c 'cd /root/agentseolab && python3 -u runner/agent_loop.py' > /tmp/opencode/agent_loop.log 2>&1 &
Stop: pkill -f agent_loop.py; rm /tmp/opencode/agent_loop.lock
"""
import os, sys, json, time, subprocess, datetime, glob, textwrap
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k,v = line.strip().split("=",1); os.environ.setdefault(k,v)

ROOT="/root/agentseolab"
LOCK="/tmp/opencode/agent_loop.lock"
LOGDIR=f"{ROOT}/results/agent_loop"

SYSTEM_PROMPT = """You are the AgentSEOLab autonomous builder. Every 60s you wake, review state, and take ONE concrete action.

Rules (from AGENTS.md):
- Cheapest free models only. Rotate families. Never claim REPLICATED without 2 families.
- ONE variable per experiment. Neutral names, seeded shuffle, fresh session, temp=0, prereg hash.
- Wilson CI, BH correction for >5 cells. No manual promotion.
- Prefer editing existing files over creating new ones unless necessary.

You must output ONLY JSON: {"action": "run|write|fix|commit|wait", "reason": "...", "command": "shell command or file to write", "details": "..."}

Actions:
- run: shell command to run an experiment (e.g. "python3 -u runner/verif_experiment.py 12")
- write: create a new runner file (provide filePath + content in details)
- fix: edit an existing file to fix a bug
- commit: git commit current changes
- wait: nothing to do, pipeline already running
"""

def snapshot():
    q = json.load(open(f"{ROOT}/experiments/QUEUE.json"))
    queue = [(it["id"], it["status"], os.path.exists(f"{ROOT}/{it['runner']}")) for it in sorted(q["items"], key=lambda x: x["priority"])]
    git_status = subprocess.run(["git","status","--short"], capture_output=True, text=True, cwd=ROOT).stdout[:800]
    journal = open(f"{ROOT}/results/pipeline/journal.jsonl").read()[-800:] if os.path.exists(f"{ROOT}/results/pipeline/journal.jsonl") else ""
    recent_runs = sorted(glob.glob(f"{ROOT}/results/experiments/*/RUN_*.json"))[-3:]
    run_summ = []
    for f in recent_runs:
        try:
            d=json.load(open(f)); run_summ.append(f"{os.path.basename(f)}: {list(d.get('results',{}).keys())[:3]}")
        except: pass
    pipeline_alive = int(subprocess.run(["bash","-c","ps aux | grep -E 'pipeline\\.py|tld_v2|naming_v2|verif_exp' | grep -v grep | wc -l"], capture_output=True, text=True).stdout.strip() or "0") > 0
    return {"queue":queue, "git_status":git_status, "journal_tail":journal[-600:], "recent_runs":run_summ, "pipeline_alive":pipeline_alive}

def call_llm(prompt):
    """Ask cheapest free model for next action."""
    import urllib.request
    # Try CF llama-8b (fastest/cheapest) first
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/@cf/meta/llama-3.1-8b-instruct-fp8"
    body = json.dumps({"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],"max_tokens":600,"temperature":0.2}).encode()
    req = urllib.request.Request(url, data=body, headers={"Authorization":f"Bearer {os.environ['CF_TOKEN']}","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d=json.loads(r.read())
            res=d.get("result",{})
            text=(res.get("choices",[{}])[0].get("message",{}).get("content") or res.get("response") or "").strip()
            # extract JSON
            import re
            m=re.search(r'\{.*\}', text, re.DOTALL)
            if m: return json.loads(m.group(0))
            return {"action":"wait","reason":f"unparseable: {text[:100]}"}
    except Exception as e:
        return {"action":"wait","reason":f"llm error: {e}"}

def execute(decision):
    action = decision.get("action","wait")
    cmd = decision.get("command","")
    details = decision.get("details","")
    reason = decision.get("reason","")
    log(f"decision: {action} - {reason}")

    if action == "wait":
        return
    if action == "run" and cmd:
        log(f"RUN: {cmd}")
        # run in background if it's a long experiment
        subprocess.Popen(cmd, shell=True, cwd=ROOT)
    elif action == "write" and cmd:
        # cmd is filePath, details is content
        path = cmd if cmd.startswith("/") else f"{ROOT}/{cmd}"
        open(path,"w").write(details)
        log(f"WROTE {path}")
    elif action == "fix" and cmd:
        log(f"FIX: {cmd}")
        subprocess.run(cmd, shell=True, cwd=ROOT)
    elif action == "commit":
        subprocess.run(["bash","-c","git add -A && git diff --cached --quiet || git commit -q -m 'agent-loop: autonomous tick'"], cwd=ROOT)
        log("committed")
    else:
        log(f"unknown action {action}")

def log(msg):
    ts=datetime.datetime.utcnow().isoformat()+"Z"
    line=f"{ts} {msg}"
    print(line, flush=True)
    os.makedirs(LOGDIR, exist_ok=True)
    open(f"{LOGDIR}/agent.log","a").write(line+"\n")

def tick():
    snap=snapshot()
    prompt = f"State snapshot:\n{json.dumps(snap, indent=2)}\n\nDecide ONE next action. If pipeline is alive, usually wait. If queue has READY items and pipeline dead, run the highest priority READY item. If runners missing for SPECIFIED items, write them. Keep it to one action."
    decision=call_llm(prompt)
    # If pipeline alive, don't block — do PARALLEL work instead
    if snap["pipeline_alive"] and decision.get("action")=="run":
        log(f"pipeline busy — asking LLM for parallel work instead")
        prompt2 = f"Pipeline is busy running an experiment. Do PARALLEL work instead: write a missing runner, add analysis, fix a bug, or improve docs. State: {json.dumps(snap, indent=2)[:1200]}\nOutput JSON with action write/fix/commit (not run/wait)."
        decision = call_llm(prompt2)
        if decision.get("action") in ("run","wait"):
            decision={"action":"wait","reason":"no parallel work identified"}
    # safety: validate file writes are inside repo
    if decision.get("action")=="write":
        path=decision.get("command","")
        if ".." in path or path.startswith("/etc") or path.startswith("/root/."):
            log(f"blocked unsafe write: {path}")
            return
    os.makedirs(LOGDIR, exist_ok=True)
    tick_file=f"{LOGDIR}/tick_{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    json.dump({"snapshot":snap,"decision":decision}, open(tick_file,"w"), indent=2)
    execute(decision)

def daemon(interval=60):
    if os.path.exists(LOCK):
        try:
            pid=int(open(LOCK).read().strip()); os.kill(pid,0)
            print(f"agent_loop already running pid {pid}"); return
        except: pass
    open(LOCK,"w").write(str(os.getpid()))
    log(f"agent_loop daemon pid={os.getpid()} interval={interval}s")
    while True:
        try: tick()
        except Exception as e: log(f"tick error: {e}")
        time.sleep(interval)

if __name__=="__main__":
    if "--once" in sys.argv: tick()
    else: daemon(int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 60)
