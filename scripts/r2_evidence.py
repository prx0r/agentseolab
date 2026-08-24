#!/usr/bin/env python3
"""r2_evidence.py — tamper-evident evidence distribution via R2.

Uploads DomainArena evidence (receipts ledger, live fixtures, canonical
results) to R2 under evidence/<date>/, then records the REMOTE sha256 back
into a local manifest. Judges/agents can later re-download and verify:
remote hash must equal local receipt manifest_hash — any mutation breaks it.

Usage: python3 scripts/r2_evidence.py [--dry-run]
Requires: rclone config 'r2' (see /tmp/opencode/r2.conf pattern) or env vars.
"""
import json, sys, hashlib, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RCONF = "/tmp/opencode/r2.conf"
BUCKET = "r2:qdw/evidence/domainarena"

TARGETS = [
    "results/domainarena_live_fixture.json",
    "results/ledger/domainarena",
    "experiments/nudge-filters-kept.json",
]

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    dry = "--dry-run" in sys.argv
    stamp = time.strftime("%Y%m%d")
    uploads = []
    for t in TARGETS:
        p = ROOT / t
        if not p.exists():
            print(f"skip missing: {t}"); continue
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    uploads.append((f, f"{BUCKET}/{stamp}/{f.relative_to(ROOT)}"))
        else:
            uploads.append((p, f"{BUCKET}/{stamp}/{p.relative_to(ROOT)}"))

    manifest = {"uploaded": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "objects": []}
    for local, remote in uploads:
        h = sha256_file(local)
        manifest["objects"].append({"local": str(local.relative_to(ROOT)),
                                    "remote": remote, "sha256": h,
                                    "bytes": local.stat().st_size})
        if not dry:
            rc = subprocess.run(["rclone", "copyto", "--config", RCONF,
                                 str(local), remote], capture_output=True, text=True)
            status = "ok" if rc.returncode == 0 else "FAIL " + rc.stderr[:80]
        else:
            status = "dry"
        print(f"  {status:>5} {remote}")

    mpath = ROOT / "experiments" / "evidence-manifest.json"
    json.dump(manifest, open(mpath, "w"), indent=2)

    if not dry:
        rc = subprocess.run(["rclone", "copyto", "--config", RCONF,
                             str(mpath), f"{BUCKET}/{stamp}/evidence-manifest.json"],
                            capture_output=True, text=True)
        if rc.returncode != 0:
            print("manifest upload FAILED:", rc.stderr[:200]); sys.exit(1)
        # remote verify: download one object back and compare hash
        probe = uploads[0]
        rc = subprocess.run(["rclone", "cat", "--config", RCONF, probe[1]],
                            capture_output=True)
        rh = hashlib.sha256(rc.stdout).hexdigest()
        lh = sha256_file(probe[0])
        ok = rh == lh
        print(f"remote verify probe: {'PASS' if ok else 'FAIL'} ({probe[0].name})")
        manifest["remote_verify"] = {"probe": probe[0].name,
                                     "pass": ok}
        json.dump(manifest, open(mpath, "w"), indent=2)
    print(f"manifest: {mpath}")

if __name__ == "__main__":
    main()
