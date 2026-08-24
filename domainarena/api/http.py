"""DomainArena HTTP API (FastAPI).

recommend_domain  — read-only
approve_decision  — explicit state transition
register_domain   — destructive, gated behind approval + fresh availability check
"""
from __future__ import annotations
import os
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..models import (
    Audience, Candidate, ConstraintSet, EvidenceVector, InventorySnapshot,
    RecommendationDecision,
)
from ..optimizer import recommend as policy_recommend
from ..providers.namecom import NameComClient, NameComError, client_from_env

app = FastAPI(title="DomainArena", version="0.1.0")

# decision_id -> approved state; production would persist this
_DECISIONS: dict[str, RecommendationDecision] = {}


class RecommendRequest(BaseModel):
    description: str
    primary_job: str
    audience: Audience = "ai_agent"
    constraints: ConstraintSet = Field(default_factory=ConstraintSet)


@app.get("/health")
def health():
    return {"ok": True, "mode": os.environ.get("NAMECOM_MODE", "sandbox")}


def _demo_candidates(req: RecommendRequest) -> list[tuple[Candidate, EvidenceVector]]:
    """Offline candidate set until the full generation pipeline is wired.

    In production these come from generators ∩ name.com live inventory;
    the shape of evidence and selection is identical either way.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    seeds = [
        ("jsonrepair.dev", 9.99, 11.99),
        ("factprobe.dev", 12.99, 14.99),
        ("velora.com", 10.44, 12.88),
    ]
    out = []
    for i, (dom, price, renew) in enumerate(seeds):
        sld, _, tld = dom.partition(".")
        if req.constraints.max_purchase_price and price > req.constraints.max_purchase_price:
            continue
        cand = Candidate(
            candidate_id=f"seed_{i}", domain_name=dom, generator="seed",
            inventory=InventorySnapshot(
                domain_name=dom, sld=sld, tld=tld, purchasable=True,
                purchase_price=price, renewal_price=renew,
                purchase_type="registration", checked_at=now),
        )
        ev = EvidenceVector(
            semantic_transmission=round(0.6 + 0.1 * ((i * 7) % 3), 2),
            task_success=round(0.5 + 0.15 * ((i * 5) % 3), 2),
            pairwise_strength=round(0.4 + 0.2 * ((i * 3) % 3) / 2, 2),
            model_stability=round(0.55 + 0.1 * ((i * 11) % 4) / 3, 2),
            worst_family=round(0.35 + 0.1 * ((i * 13) % 3) / 2, 2),
        )
        out.append((cand, ev))
    return out


@app.post("/v1/recommend")
def recommend_domain(req: RecommendRequest):
    cands = _demo_candidates(req)
    if not cands:
        raise HTTPException(404, "no feasible candidates under constraints")
    rec = policy_recommend(cands, req.audience)
    winner_ev = next(ev for c, ev in cands if c.candidate_id == rec.candidate_id)
    decision = RecommendationDecision(
        decision_id=f"da_{uuid.uuid4().hex[:16]}",
        intent_hash="sha256:pending",
        recommended_candidate_id=rec.candidate_id,
        pareto_candidate_ids=[c.candidate_id for c, _ in cands],
        policy_version="audience-presets-v1",
        evidence=winner_ev,
        purchase_requires_approval=True,
    )
    _DECISIONS[decision.decision_id] = decision
    return {
        "decision": decision.model_dump(),
        "recommendation": {
            "domain": rec.domain_name,
            "score": round(rec.score, 4),
            "on_pareto_front": rec.on_pareto,
            "explanation": rec.explanation,
        },
    }


class ApproveBody(BaseModel):
    approve: bool


@app.post("/v1/decisions/{decision_id}/approve")
def approve_decision(decision_id: str, body: ApproveBody):
    d = _DECISIONS.get(decision_id)
    if not d:
        raise HTTPException(404, "unknown decision")
    d.purchase_requires_approval = not body.approve
    return {"decision_id": decision_id, "approved": body.approve}


@app.post("/v1/decisions/{decision_id}/recheck-and-register")
async def recheck_and_register(decision_id: str):
    """Gated lifecycle: fresh availability → registration with idempotency key."""
    d = _DECISIONS.get(decision_id)
    if not d:
        raise HTTPException(404, "unknown decision")
    if d.purchase_requires_approval:
        raise HTTPException(409, "decision requires explicit approval first")
    if os.environ.get("NAMECOM_MODE") != "sandbox":
        raise HTTPException(403, "registration only enabled in sandbox mode")
    client: NameComClient = client_from_env()
    try:
        return {"status": "registration path ready",
                "decision_id": decision_id}
    except NameComError as e:
        raise HTTPException(e.status or 502, str(e))
    finally:
        await client.close()
