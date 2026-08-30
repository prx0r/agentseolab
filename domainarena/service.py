"""DomainArena unified service — single source of truth for all lifecycle operations.

HTTP API, MCP server, and demo UI all call this service.
No duplicated logic. One state model. One approval flow.
"""
from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .models import (
    Audience, Candidate, ConstraintSet, EvidenceVector, EvidenceValue,
    EvStatus, InventorySnapshot, RecommendationDecision,
)
from .optimizer import recommend as policy_recommend
from .providers.namecom import NameComClient, NameComError, client_from_env


# ── Decision state machine ─────────────────────────────────────────

class DecisionStatus(str, Enum):
    RECOMMENDED = "RECOMMENDED"
    PREPARED = "PREPARED"
    APPROVED = "APPROVED"
    REGISTERED = "REGISTERED"
    DNS_CONFIGURED = "DNS_CONFIGURED"
    VERIFIED = "VERIFIED"
    UNAVAILABLE = "UNAVAILABLE"
    PRICE_DRIFTED = "PRICE_DRIFTED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    ERROR = "ERROR"


@dataclass
class DecisionState:
    """Immutable decision record with full lifecycle tracking."""
    decision_id: str
    intent_hash: str
    recommended_domain: str
    recommended_candidate_id: str
    pareto_candidate_ids: list[str]
    policy_version: str
    evidence: EvidenceVector
    status: DecisionStatus = DecisionStatus.RECOMMENDED
    approval_token: str | None = None
    preparation: dict[str, Any] | None = None
    registration: dict[str, Any] | None = None
    dns_receipt: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    api_trace: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def transition(self, new_status: DecisionStatus) -> None:
        """Validate and execute state transition."""
        VALID_TRANSITIONS = {
            DecisionStatus.RECOMMENDED: {
                DecisionStatus.PREPARED, DecisionStatus.UNAVAILABLE,
                DecisionStatus.PRICE_DRIFTED, DecisionStatus.PROVIDER_ERROR,
            },
            DecisionStatus.PREPARED: {
                DecisionStatus.APPROVED, DecisionStatus.UNAVAILABLE,
                DecisionStatus.PRICE_DRIFTED, DecisionStatus.ERROR,
            },
            DecisionStatus.APPROVED: {
                DecisionStatus.REGISTERED, DecisionStatus.UNAVAILABLE,
                DecisionStatus.PRICE_DRIFTED, DecisionStatus.ERROR,
            },
            DecisionStatus.REGISTERED: {
                DecisionStatus.DNS_CONFIGURED, DecisionStatus.VERIFIED,
                DecisionStatus.ERROR,
            },
            DecisionStatus.DNS_CONFIGURED: {
                DecisionStatus.VERIFIED, DecisionStatus.ERROR,
            },
        }
        allowed = VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {self.status.value} → {new_status.value} "
                f"(allowed: {[s.value for s in allowed]})"
            )
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc).isoformat()


# ── DomainService ──────────────────────────────────────────────────

class DomainService:
    """Single source of truth for all lifecycle operations.
    
    HTTP, MCP, and demo UI all call this service.
    """

    def __init__(self):
        self._decisions: dict[str, DecisionState] = {}
        self._candidates: dict[str, list[tuple[Candidate, EvidenceVector]]] = {}
        self._store_dir = Path(os.environ.get(
            "DOMAINARENA_STORE", "results/decisions"))
        self._store_dir.mkdir(parents=True, exist_ok=True)

    def _persist(self, decision: DecisionState) -> None:
        """Persist decision to disk."""
        fn = self._store_dir / f"{decision.decision_id}.json"
        data = {
            "decision_id": decision.decision_id,
            "intent_hash": decision.intent_hash,
            "recommended_domain": decision.recommended_domain,
            "recommended_candidate_id": decision.recommended_candidate_id,
            "pareto_candidate_ids": decision.pareto_candidate_ids,
            "policy_version": decision.policy_version,
            "status": decision.status.value,
            "approval_token": decision.approval_token,
            "preparation": decision.preparation,
            "registration": decision.registration,
            "dns_receipt": decision.dns_receipt,
            "verification": decision.verification,
            "api_trace": decision.api_trace[-20:],
            "created_at": decision.created_at,
            "updated_at": decision.updated_at,
        }
        fn.write_text(json.dumps(data, indent=2, default=str))

    def _load(self, decision_id: str) -> DecisionState | None:
        """Load decision from disk if not in memory."""
        if decision_id in self._decisions:
            return self._decisions[decision_id]
        fn = self._store_dir / f"{decision_id}.json"
        if not fn.exists():
            return None
        data = json.loads(fn.read_text())
        ds = DecisionState(
            decision_id=data["decision_id"],
            intent_hash=data["intent_hash"],
            recommended_domain=data["recommended_domain"],
            recommended_candidate_id=data["recommended_candidate_id"],
            pareto_candidate_ids=data["pareto_candidate_ids"],
            policy_version=data["policy_version"],
            evidence=EvidenceVector(),  # simplified for load
            status=DecisionStatus(data["status"]),
            approval_token=data.get("approval_token"),
            preparation=data.get("preparation"),
            registration=data.get("registration"),
            dns_receipt=data.get("dns_receipt"),
            verification=data.get("verification"),
            api_trace=data.get("api_trace", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
        self._decisions[decision_id] = ds
        return ds

    def _log_api(self, decision: DecisionState, method: str,
                 endpoint: str, status: int, latency_ms: int) -> None:
        decision.api_trace.append({
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "latency_ms": latency_ms,
        })

    # ── Public API ─────────────────────────────────────────────────

    def recommend(
        self,
        description: str,
        primary_job: str,
        audience: Audience = "ai_agent",
        constraints: ConstraintSet | None = None,
        live_candidates: list[tuple[Candidate, EvidenceVector]] | None = None,
    ) -> tuple[DecisionState, list[tuple[Candidate, EvidenceVector]]]:
        """Run recommendation pipeline. Returns decision + candidates."""
        if constraints is None:
            constraints = ConstraintSet()

        # Use live candidates if provided, otherwise fixtures
        if live_candidates is not None:
            cands = live_candidates
        else:
            cands = self._fixture_candidates(constraints)

        if not cands:
            raise ValueError("No feasible candidates under constraints")

        # Run optimizer
        rec = policy_recommend(cands, audience)

        # Build decision
        intent_hash = "sha256:" + hashlib.sha256(json.dumps(
            {"description": description, "primary_job": primary_job},
            sort_keys=True).encode()).hexdigest()

        ds = DecisionState(
            decision_id=f"da_{uuid.uuid4().hex[:16]}",
            intent_hash=intent_hash,
            recommended_domain=rec.domain_name,
            recommended_candidate_id=rec.candidate_id,
            pareto_candidate_ids=[c.candidate_id for c, _ in cands],
            policy_version="audience-presets-v1",
            evidence=next(ev for c, ev in cands if c.candidate_id == rec.candidate_id),
        )

        self._decisions[ds.decision_id] = ds
        self._candidates[ds.decision_id] = cands
        self._persist(ds)

        return ds, cands

    def get_decision(self, decision_id: str) -> DecisionState:
        """Get decision by ID."""
        ds = self._load(decision_id)
        if ds is None:
            raise KeyError(f"Unknown decision: {decision_id}")
        return ds

    def prepare_registration(
        self,
        decision_id: str,
        max_price_drift_pct: float = 10.0,
    ) -> dict:
        """Fresh availability + pricing check. Does NOT register. Sync wrapper."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError(
                "prepare_registration() cannot be called from a running event loop. "
                "Use prepare_registration_async() instead."
            )
        return asyncio.run(
            self.prepare_registration_async(decision_id, max_price_drift_pct))

    async def prepare_registration_async(
        self,
        decision_id: str,
        max_price_drift_pct: float = 10.0,
    ) -> dict:
        """Fresh availability + pricing check. Does NOT register. Async version."""
        ds = self.get_decision(decision_id)
        dom = ds.recommended_domain
        t0 = time.time()

        client = client_from_env()
        try:
            entry = await client.check_availability_fail_closed(dom)
            self._log_api(ds, "POST", "checkAvailability", 200,
                         int((time.time() - t0) * 1000))

            purchasable = entry.get("purchasable")
            if purchasable is not True:
                ds.transition(DecisionStatus.UNAVAILABLE)
                self._persist(ds)
                return {
                    "status": "UNAVAILABLE", "domain": dom,
                    "purchasable": purchasable,
                }

            t1 = time.time()
            pricing = await client.get_pricing(dom)
            self._log_api(ds, "GET", f"domains/{dom}:getPricing", 200,
                         int((time.time() - t1) * 1000))

            new_price = self._extract_price(pricing)
            renewal_price = None
            if isinstance(pricing, dict):
                renewal_price = pricing.get("renewalPrice") or pricing.get("renewal_price")

            orig_price = None
            cands = self._candidates.get(decision_id) or []
            cand = next((c for c, _ in cands if c.domain_name == dom), None)
            if cand:
                orig_price = cand.inventory.purchase_price

            price_drift_pct = None
            approval_valid = True
            if orig_price is not None and new_price is not None and orig_price > 0:
                price_drift_pct = abs(new_price - orig_price) / orig_price * 100
                if price_drift_pct > max_price_drift_pct:
                    approval_valid = False
                    ds.transition(DecisionStatus.PRICE_DRIFTED)

            if approval_valid and ds.status == DecisionStatus.RECOMMENDED:
                ds.transition(DecisionStatus.PREPARED)

            ds.preparation = {
                "domain": dom,
                "purchasable": True,
                "purchase_price": new_price,
                "renewal_price": renewal_price,
                "original_price": orig_price,
                "price_drift_pct": round(price_drift_pct, 2) if price_drift_pct else None,
                "approval_valid": approval_valid,
            }
            self._persist(ds)

            return {
                "decision_id": decision_id,
                "domain": dom,
                "status": ds.status.value,
                "purchasable": True,
                "purchase_price": new_price,
                "renewal_price": renewal_price,
                "original_price": orig_price,
                "price_drift_pct": round(price_drift_pct, 2) if price_drift_pct else None,
                "approval_valid": approval_valid,
                "requires_approval": ds.status != DecisionStatus.APPROVED,
            }
        except NameComError as e:
            ds.transition(DecisionStatus.PROVIDER_ERROR)
            self._persist(ds)
            return {
                "status": "PROVIDER_ERROR", "domain": dom,
                "error": str(e),
            }
        finally:
            await client.close()

    def approve(self, decision_id: str) -> dict:
        """Approve decision for registration. Returns approval token.
        Decision must be in PREPARED status (prepare_registration called first)."""
        ds = self.get_decision(decision_id)
        if ds.status != DecisionStatus.PREPARED:
            raise ValueError(f"Cannot approve in status {ds.status.value} (must be PREPARED)")

        token = hashlib.sha256(
            f"{decision_id}|{ds.recommended_domain}|approve|{uuid.uuid4().hex}".encode()
        ).hexdigest()[:32]

        ds.approval_token = token
        ds.transition(DecisionStatus.APPROVED)
        self._persist(ds)

        return {
            "decision_id": decision_id,
            "approved": True,
            "approval_token": token,
        }

    def reject(self, decision_id: str) -> dict:
        """Reject decision. Clears approval token."""
        ds = self.get_decision(decision_id)
        ds.approval_token = None
        self._persist(ds)
        return {"decision_id": decision_id, "approved": False}

    def register(
        self,
        decision_id: str,
        approval_token: str,
        max_price_drift_pct: float = 10.0,
    ) -> dict:
        """Register domain after approval. Sync wrapper."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError(
                "register() cannot be called from a running event loop. "
                "Use register_async() instead."
            )
        return asyncio.run(
            self.register_async(decision_id, approval_token, max_price_drift_pct))

    async def register_async(
        self,
        decision_id: str,
        approval_token: str,
        max_price_drift_pct: float = 10.0,
    ) -> dict:
        """Register domain after approval. Validates everything. Async version."""
        ds = self.get_decision(decision_id)

        # Must be approved
        if ds.status != DecisionStatus.APPROVED:
            raise ValueError(f"Cannot register in status {ds.status.value}")
        if not ds.approval_token:
            raise ValueError("No approval token")
        if not hmac.compare_digest(ds.approval_token, approval_token):
            raise PermissionError("Invalid approval token")

        # Must have fresh preparation
        if not ds.preparation:
            raise ValueError("No preparation record")
        if not ds.preparation.get("approval_valid"):
            raise ValueError("Preparation expired or price drifted")

        dom = ds.recommended_domain
        if os.environ.get("NAMECOM_MODE") != "sandbox":
            raise PermissionError("Registration only enabled in sandbox mode")

        client = client_from_env()
        t0 = time.time()
        steps = []

        try:
            # 1. Re-verify availability (fail-closed)
            entry = await client.check_availability_fail_closed(dom)
            self._log_api(ds, "POST", "checkAvailability", 200,
                         int((time.time() - t0) * 1000))
            steps.append({"step": "check_availability", "ok": True})

            if entry.get("purchasable") is not True:
                raise ValueError(f"{dom} no longer available")

            # 2. Re-verify pricing
            t1 = time.time()
            pricing = await client.get_pricing(dom)
            self._log_api(ds, "GET", f"domains/{dom}:getPricing", 200,
                         int((time.time() - t1) * 1000))
            steps.append({"step": "get_pricing", "ok": True})

            current_price = self._extract_price(pricing)
            if current_price is None:
                raise ValueError("Cannot verify current price")

            # 3. Register (idempotent)
            idem = hashlib.sha256(
                f"{decision_id}|{dom}|register".encode()).hexdigest()
            payload = {"domain": {"domainName": dom}}
            if current_price is not None:
                payload["purchasePrice"] = current_price

            t2 = time.time()
            reg = await client.register_domain(payload, idem)
            self._log_api(ds, "POST", "domains", 200,
                         int((time.time() - t2) * 1000))
            steps.append({"step": "register_domain", "ok": True})

            # 4. Confirm via GetDomain
            t3 = time.time()
            got = await client.get_domain(dom)
            self._log_api(ds, "GET", f"domains/{dom}", 200,
                         int((time.time() - t3) * 1000))
            steps.append({"step": "get_domain", "ok": True})

            ds.registration = {
                "domain": dom,
                "order_id": reg.get("orderId"),
                "idempotency_key": idem,
                "confirmation": got,
            }
            ds.transition(DecisionStatus.REGISTERED)
            self._persist(ds)

            return {
                "decision_id": decision_id,
                "domain": dom,
                "status": "REGISTERED",
                "steps": steps,
                "idempotency_key": idem,
            }
        except Exception as e:
            ds.transition(DecisionStatus.ERROR)
            self._persist(ds)
            raise
        finally:
            await client.close()

    def configure_dns(self, decision_id: str) -> dict:
        """Create DNS TXT receipt record. Sync wrapper."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError(
                "configure_dns() cannot be called from a running event loop. "
                "Use configure_dns_async() instead."
            )
        return asyncio.run(self.configure_dns_async(decision_id))

    async def configure_dns_async(self, decision_id: str) -> dict:
        """Create DNS TXT receipt record. Async version."""
        ds = self.get_decision(decision_id)
        if ds.status != DecisionStatus.REGISTERED:
            raise ValueError(f"Cannot configure DNS in status {ds.status.value}")

        dom = ds.recommended_domain
        receipt_hash = hashlib.sha256(json.dumps(
            {"decision": decision_id, "domain": dom},
            sort_keys=True).encode()).hexdigest()
        txt_host = "_domainarena"
        txt_answer = f"sha256:{receipt_hash}"

        client = client_from_env()
        try:
            t0 = time.time()
            await client.create_dns_record(
                dom, host=txt_host, record_type="TXT", answer=txt_answer)
            self._log_api(ds, "POST", f"domains/{dom}/records", 200,
                         int((time.time() - t0) * 1000))

            t1 = time.time()
            records = await client.list_dns_records(dom)
            self._log_api(ds, "GET", f"domains/{dom}/records", 200,
                         int((time.time() - t1) * 1000))

            dns_ok = any(txt_answer in json.dumps(r) for r in records)

            ds.dns_receipt = {
                "host": txt_host,
                "type": "TXT",
                "answer": txt_answer,
                "records": records,
                "verified": dns_ok,
            }
            ds.transition(DecisionStatus.DNS_CONFIGURED)
            if dns_ok:
                ds.transition(DecisionStatus.VERIFIED)
            self._persist(ds)

            return {
                "decision_id": decision_id,
                "domain": dom,
                "status": ds.status.value,
                "dns_receipt_verified": dns_ok,
                "receipt_hash": f"sha256:{receipt_hash}",
            }
        finally:
            await client.close()

    def _extract_price(self, pricing: dict) -> float | None:
        """Extract purchase price from name.com pricing response."""
        if not isinstance(pricing, dict):
            return None
        for k in ("purchasePrice", "purchase_price"):
            if pricing.get(k) is not None:
                return pricing[k]
        for t in pricing.get("tiers", []) or []:
            if t.get("purchasePrice") is not None:
                return t["purchasePrice"]
        return None

    def _fixture_candidates(
        self, constraints: ConstraintSet
    ) -> list[tuple[Candidate, EvidenceVector]]:
        """Offline fixture candidates."""
        now = datetime.now(timezone.utc).isoformat()
        seeds = [
            ("jsonrepair.dev", 9.99, 11.99),
            ("factprobe.dev", 12.99, 14.99),
            ("velora.com", 10.44, 12.88),
        ]
        out = []
        for i, (dom, price, renew) in enumerate(seeds):
            if constraints.max_purchase_price and price > constraints.max_purchase_price:
                continue
            sld, _, tld = dom.partition(".")
            cand = Candidate(
                candidate_id=f"seed_{i}", domain_name=dom, generator="seed",
                inventory=InventorySnapshot(
                    domain_name=dom, sld=sld, tld=tld, purchasable=True,
                    purchase_price=price, renewal_price=renew,
                    purchase_type="registration", checked_at=now),
            )
            ev = EvidenceVector(
                semantic_transmission=0.6,
                task_success=0.0,  # NOT_MEASURED — no execution trial
                pairwise_strength=0.4,
            )
            out.append((cand, ev))
        return out


# Singleton
_service: DomainService | None = None


def get_service() -> DomainService:
    global _service
    if _service is None:
        _service = DomainService()
    return _service
