#!/usr/bin/env python3
"""Extract the validated pilot field trace from scout session 20260823_023900_f63b4b.

The probe run (probe_field_run.py, 126s, exit 0) used the Appendix-A prompt.
This re-runs extraction against the frozen F-001 intent and ingests it.
"""
import json
import subprocess
import sys

sys.path.insert(0, "/root/agentseolab/runner")

SESSION = "20260823_023900_f63b4b"
PROFILE = "scout"
OUT = "/root/agentseolab/runs/field/20260823T024100Z_scout_f001pilot"

r = subprocess.run([
    "python3", "/root/agentseolab/runner/field.py", "extract",
    "--profile", PROFILE,
    "--session", SESSION,
    "--intent-id", "intent_f001domainavail7c31",
    "--intent-hash", "bb97d40ad01a9f4a21af5326afc9fbc6b31066bb7d0b5afa213aac9d94f93b86",
    "--out", OUT,
    "--model", "mimo-v2.5",
    "--provider", "opencode-go",
    "--network-environment", "live-web-browser+curl; google blocked(captcha), ddg reachable",
], capture_output=True, text=True)
print("extract rc:", r.returncode)
print(r.stdout)
if r.returncode != 0:
    print(r.stderr)
    sys.exit(1)

trace = json.load(open(OUT + "/trace_raw.json"))
print("\n=== event stream ===")
for e in trace["events"]:
    p = e["payload"]
    brief = {k: (v if not isinstance(v, (list, dict)) else
                 f"<{type(v).__name__} len={len(v)}>") for k, v in list(p.items())[:4]}
    print(f"{e['seq']:3d} {e['event_type']:16s} {json.dumps(brief)[:150]}")

print("\n=== ingest ===")
r = subprocess.run([
    "python3", "/root/agentseolab/runner/field.py", "ingest",
    "--trace", OUT,
    "--db", "/root/agentseolab/lab.db",
], capture_output=True, text=True)
print("ingest rc:", r.returncode)
print(r.stdout)
if r.returncode != 0:
    print(r.stderr)
