#!/usr/bin/env python3
"""Generate RESULTS.md and per-experiment status docs from the canonical ledger.
Markdown is DERIVED. Never hand-edit generated files; edit results/ledger/evidence.json.

Also exports ExperimentReceipts: one immutable machine-readable receipt per run,
consumable by Hydra as EvidenceClaimV1 inputs (finalbuilds2/contracts/hypotheses/).
"""
import json, os, datetime, hashlib

ROOT = "/root/agentseolab"
LEDGER = f"{ROOT}/results/ledger/evidence.json"
RESULTS_MD = f"{ROOT}/RESULTS.md"
RECEIPTS_DIR = f"{ROOT}/results/receipts"


def load():
    return json.load(open(LEDGER))


def gen_results_md(lib):
    lines = [
        "<!-- GENERATED from results/ledger/evidence.json — do not hand-edit -->",
        f"# RESULTS — evidence ledger snapshot ({lib['updated'][:10]})",
        "",
    ]
    counts = {}
    for h in lib["hypotheses"]:
        counts[h["status"]] = counts.get(h["status"], 0) + 1
    summary = " · ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    lines += [f"**Status: {summary}**", ""]
    for h in lib["hypotheses"]:
        lines += [f"## {h['id']} — {h['status']}",
                  f"{h['statement']}",
                  f"*Protocol v{h.get('protocol_version','?')} · {h['verdict']}*", ""]
        for r in h.get("runs", []):
            if isinstance(r, dict) and "p_working" in r:
                star = "*" if r.get("sig") else " "
                lines.append(f"- `{r['run_id']}` {r['model']:24s} n={r['n_decided']:<4}"
                             f" p={r['p_working']:<6} CI95={r['ci95']} {star}")
            elif isinstance(r, str):
                lines.append(f"- {r}")
        lines.append("")
    if lib.get("open_questions"):
        lines += ["## Open questions", ""]
        lines += [f"- {q}" for q in lib["open_questions"]]
    open(RESULTS_MD, "w").write("\n".join(lines) + "\n")
    print(f"wrote {RESULTS_MD}")


def receipt_for_run(run, hyp_id, statement, verdict):
    payload = {
        "schema_version": 1,
        "receipt_id": f"ASLR-{hashlib.sha256(json.dumps(run, sort_keys=True).encode()).hexdigest()[:12]}",
        "experiment": hyp_id,
        "claim": statement,
        "outcome": verdict,
        "quantities": {
            "n_decided": run.get("n_decided"),
            "p_effect": run.get("p_working", run.get("p_correct")),
            "ci95": run.get("ci95"),
            "significant": run.get("sig", False),
        },
        "source": {
            "lab": "agentseolab",
            "model": run.get("model"),
            "family": run.get("family"),
            "provider": run.get("provider"),
            "protocol_version": 2,
            "manifest_ref": "results/experiments/asl001_v2/PREREG_20260823-072124.json",
        },
        "extracted_at": datetime.datetime.utcnow().isoformat() + "Z",
        "supports_hypothesis_ids": [],
        "challenges_hypothesis_ids": ["H-ASL001a"] if hyp_id == "H-ASL001b" else [],
    }
    return payload


def export_receipts(lib):
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    n = 0
    for h in lib["hypotheses"]:
        for r in h.get("runs", []):
            if isinstance(r, dict) and "n_decided" in r:
                rec = receipt_for_run(r, h["id"], h["statement"], h["verdict"])
                path = f"{RECEIPTS_DIR}/{rec['receipt_id']}.json"
                json.dump(rec, open(path, "w"), indent=1)
                n += 1
    # bundle for Hydra ingestion
    bundle = [json.load(open(f"{RECEIPTS_DIR}/{f}"))
              for f in sorted(os.listdir(RECEIPTS_DIR)) if f.endswith(".json")]
    json.dump(bundle, open(f"{RECEIPTS_DIR}/hydra_bundle.json", "w"), indent=1)
    print(f"exported {n} receipts + hydra_bundle.json")


if __name__ == "__main__":
    lib = load()
    gen_results_md(lib)
    export_receipts(lib)
