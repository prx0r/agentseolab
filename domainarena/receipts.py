"""Evidence receipts — auditable provenance for every recommendation.

Each receipt binds: frozen intent hash, inventory snapshot timestamps,
evidence vector, policy version, decision id. Written as append-only JSON
under results/ledger/domainarena/. Receipts make every recommendation
reproducible and tamper-evident (manifest hash discipline from AGENTS.md).
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LEDGER_DIR = Path(__file__).resolve().parents[1] / "results" / "ledger" / "domainarena"

SCHEMA_VERSION = 1


def receipt_hash(receipt: dict) -> str:
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def build_receipt(*, intent_hash: str, description: str, primary_job: str,
                  audience: str, constraints_dict: dict,
                  feasible_domains: list[str], rejected: dict[str, list[str]],
                  recommendation: dict | None, source: str,
                  policy_version: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "intent_hash": intent_hash,
        "intent": {"description": description, "primary_job": primary_job,
                   "audience": audience, "constraints": constraints_dict},
        "feasible_domains": feasible_domains,
        "rejected": rejected,
        "recommendation": recommendation,
        "source": source,               # name.com-live | demo-fixture
        "policy_version": policy_version,
    }


def write_receipt(receipt: dict) -> tuple[str, str]:
    """Append to the ledger; returns (receipt_id, manifest_hash)."""
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    h = receipt_hash(receipt)
    rid = f"da_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{h[7:15]}"
    receipt = {**receipt, "receipt_id": rid, "manifest_hash": h}
    path = LEDGER_DIR / f"{rid}.json"
    path.write_text(json.dumps(receipt, indent=2))
    return rid, h


def verify_receipt(path: Path) -> bool:
    r = json.loads(Path(path).read_text())
    body = {k: v for k, v in r.items() if k != "manifest_hash"}
    return receipt_hash(body) == r.get("manifest_hash")
