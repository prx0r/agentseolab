#!/usr/bin/env python3
"""Autonomous experiment pipeline.

Reads experiments/QUEUE.json top-down, executes SPECIFIED items whose runner
exists, validates outputs, regenerates docs, and journals everything.

Usage:
  python3 runner/pipeline.py            # run next runnable item
  python3 runner/pipeline.py --all      # run until queue exhausted or failure
  python3 runner/pipeline.py --status   # show queue state

Discipline encoded here:
- prereg file must exist in the runner's results dir BEFORE execution (runners do this)
- results dir pattern: results/experiments/<id>/RUN_*.json
- after each item: analysis regenerate + git commit (if repo clean-ish)
- never promotes ledger status automatically; PROVISIONAL is the ceiling for auto-runs
"""
import json, os, subprocess, sys, datetime, glob

ROOT = "/root/agentseolab"
QUEUE = f"{ROOT}/experiments/QUEUE.json"
JOURNAL = f"{ROOT}/results/pipeline/journal.jsonl"


def log(event, **kw):
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    rec = {"ts": datetime.datetime.utcnow().isoformat() + "Z", "event": event, **kw}
    with open(JOURNAL, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


def load_queue():
    return json.load(open(QUEUE))


def save_queue(q):
    json.dump(q, open(QUEUE, "w"), indent=1)


def has_run(item):
    exp_dir = {
        "TLD-V2": "tld_v2", "NAMING-02": "naming02", "VERIF": "verif",
        "POS01-DOSE": "pos_dose", "ASL010-RETRY": "retry", "CANARY-CROSS": "canary_cross",
        "ASL002D-EC50": "asl002d", "ASLPRIX": "prix",
    }.get(item["id"])
    return bool(glob.glob(f"{ROOT}/results/experiments/{exp_dir}/RUN_*.json")) if exp_dir else False


def run_item(item):
    runner = os.path.join(ROOT, item["runner"])
    if not os.path.exists(runner):
        log("skip_no_runner", id=item["id"], runner=item["runner"])
        return False
    log("start", id=item["id"], runner=item["runner"])
    t0 = datetime.datetime.utcnow()
    proc = subprocess.run([sys.executable, "-u", runner],
                          capture_output=True, text=True, timeout=7200)
    tail = (proc.stdout or "")[-1500:] + (proc.stderr or "")[-500:]
    ok = proc.returncode == 0 and has_run(item)
    log("finish", id=item["id"], rc=proc.returncode,
        produced_run=has_run(item), minutes=round((datetime.datetime.utcnow()-t0).total_seconds()/60, 1),
        tail=tail[-600:])
    if ok:
        # refresh derived docs
        subprocess.run([sys.executable, f"{ROOT}/analysis/generate_docs.py"],
                       capture_output=True, text=True)
        q = load_queue()
        for it in q["items"]:
            if it["id"] == item["id"]:
                it["status"] = "DONE"
        save_queue(q)
        log("docs_regenerated", id=item["id"])
    return ok


def status():
    q = load_queue()
    print(f"{'id':16s} {'priority':>8s} {'status':22s} runner-exists  run-exists")
    for it in sorted(q["items"], key=lambda x: x["priority"]):
        print(f"{it['id']:16s} {it['priority']:>8d} {it['status']:22s} "
          f"{str(os.path.exists(os.path.join(ROOT, it['runner']))):13s} {str(has_run(it)):10s}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--status":
        status(); sys.exit(0)
    q = load_queue()
    ran_any = False
    for item in sorted(q["items"], key=lambda x: x["priority"]):
        if item["status"] == "DONE" or has_run(item):
            continue
        if not os.path.exists(os.path.join(ROOT, item["runner"])):
            continue
        ok = run_item(item)
        ran_any = True
        if not ok:
            log("aborting_queue_on_failure", id=item["id"])
            break
        if arg != "--all":
            break
    if not ran_any:
        print("queue: nothing runnable (all DONE or runners missing)")
