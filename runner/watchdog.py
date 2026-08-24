#!/usr/bin/env python3
"""Watchdog: every 60s monitor queue, pipeline health, progress, and nudge.

- tails pipeline.log + journal + usage.csv
- detects stalls (no new usage rows in 5 min while a job claims to be alive)
- auto-restarts the pipeline runner if stalled/dead and queue has work
- peer-reviews freshly completed RUN files (position balance, ceiling, parse rate)
- appends findings to results/pipeline/watchdog.log + nudges queue

Run once:    python3 runner/watchdog.py --once
Daemon:      nohup python3 -u runner/watchdog.py > /tmp/opencode/watchdog.log 2>&1 &
Cron:        */1 * * * * /usr/bin/python3 /root/agentseolab/runner/watchdog.py --once
"""
import csv, glob, json, os, subprocess, sys, time, datetime

ROOT = "/root/agentseolab"
QUEUE = f"{ROOT}/experiments/QUEUE.json"
JOURNAL = f"{ROOT}/results/pipeline/journal.jsonl"
WLOG = f"{ROOT}/results/pipeline/watchdog.log"
USAGE = f"{ROOT}/providers/usage.csv"
PIPELINE_LOG = "/tmp/opencode/pipeline.log"
LOCK = "/tmp/opencode/watchdog.lock"


def log(msg):
    os.makedirs(os.path.dirname(WLOG), exist_ok=True)
    line = f"{datetime.datetime.utcnow().isoformat()}Z watchdog {msg}"
    open(WLOG, "a").write(line + "\n")
    print(line, flush=True)


def pipeline_alive():
    try:
        out = subprocess.check_output(["bash","-c","ps aux | grep -E 'pipeline\\.py|tld_v2|naming_v2|verif_exp' | grep -v grep | wc -l"], text=True)
        return int(out.strip()) > 0
    except Exception:
        return False


def last_usage_age_s():
    try:
        rows = list(csv.reader(open(USAGE)))[1:]
        if not rows: return 999
        ts = float(rows[-1][0])
        return time.time() - ts
    except Exception:
        return 999


def queue_has_runnable():
    q = json.load(open(QUEUE))
    for it in sorted(q["items"], key=lambda x: x["priority"]):
        rp = os.path.join(ROOT, it["runner"])
        has_run = bool(glob.glob(f"{ROOT}/results/experiments/{it['id'].lower().replace('-','').replace('_','')}/RUN_*.json"))
        # looser check: any RUN in plausible dirs
        if it["status"] != "DONE" and os.path.exists(rp):
            return True, it["id"]
    return False, None


def peer_review_latest_run():
    """Quick sanity checks on the most recent RUN file."""
    runs = sorted(glob.glob(f"{ROOT}/results/experiments/*/RUN_*.json"))
    if not runs:
        return
    f = runs[-1]
    d = json.load(open(f))
    spec = d.get("spec", {})
    results = d.get("results", {})
    issues = []
    for model, res in results.items():
        trials = res.get("trials", [])
        if not trials: continue
        decided = sum(1 for t in trials if t.get("picked_tld") or t.get("picked") or t.get("picked_target") is not None)
        if not decided:
            issues.append(f"{model}: zero decided (parse failure?)")
        slot_dist = res.get("slot_dist")
        if slot_dist and len(trials) >= 20:
            vals = list(map(int, slot_dist.values())) if slot_dist else []
            if vals and max(vals) - min(vals) > 4:
                issues.append(f"{model}: slot imbalance {slot_dist}")
        # ceiling check for naming
        cells = res.get("cells", {})
        if cells and all(c.get("p") in (1.0, 0.0) for c in cells.values()):
            issues.append(f"{model}: ceiling/floor in all cells {cells}")
    if issues:
        log("peer-review WARN " + os.path.basename(f) + " :: " + " | ".join(issues))
    else:
        log(f"peer-review PASS {os.path.basename(f)}")


def nudge_pipeline():
    log("nudging pipeline --all")
    subprocess.Popen([sys.executable, "-u", f"{ROOT}/runner/pipeline.py", "--all"],
                     stdout=open(PIPELINE_LOG, "a"), stderr=subprocess.STDOUT)


def tick():
    need, nxt = queue_has_runnable()
    alive = pipeline_alive()
    age = last_usage_age_s()
    stalled = alive and age > 360  # 6 min without a call while claiming alive
    dead = not alive and need

    if need:
        log(f"queue runnable={nxt} pipeline_alive={alive} last_call_age={int(age)}s")
    else:
        log(f"queue drained (alive={alive})")
        return

    if stalled:
        log(f"STALL detected (age {int(age)}s) -> killing + restarting")
        subprocess.run(["bash","-c","pkill -f 'tld_v2|naming_v2|verif_exp|pos_dose|pipeline\\.py' || true"])
        time.sleep(3)
        nudge_pipeline()
    elif dead:
        log(f"pipeline dead but {nxt} runnable -> starting")
        nudge_pipeline()
    else:
        # alive and not stalled: nothing to do, but peer-review any fresh completions
        peer_review_latest_run()


def daemon(interval=60):
    # single-instance guard
    if os.path.exists(LOCK):
        try:
            pid = int(open(LOCK).read().strip())
            os.kill(pid, 0)
            print(f"watchdog already running pid {pid}", flush=True)
            return
        except Exception:
            pass
    open(LOCK, "w").write(str(os.getpid()))
    log(f"daemon started pid={os.getpid()} interval={interval}s")
    while True:
        try:
            tick()
        except Exception as e:
            log(f"tick error: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    if "--once" in sys.argv:
        tick()
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 60
        daemon(interval)
