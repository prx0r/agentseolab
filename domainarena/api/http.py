"""DomainArena HTTP API (FastAPI).

All lifecycle operations go through DomainService.
API key auth: set DOMAINARENA_API_KEY env var to require key on mutating endpoints.
"""
from __future__ import annotations
import os
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field

from ..models import Audience, ConstraintSet
from ..service import get_service, DecisionStatus

app = FastAPI(title="DomainArena", version="0.2.0")


def _verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    """Verify API key if DOMAINARENA_API_KEY is set. No-op if unset (local dev)."""
    required = os.environ.get("DOMAINARENA_API_KEY")
    if required and x_api_key != required:
        raise HTTPException(401, "Invalid or missing X-Api-Key header")


class RecommendRequest(BaseModel):
    description: str
    primary_job: str
    audience: Audience = "ai_agent"
    constraints: ConstraintSet = Field(default_factory=ConstraintSet)


@app.get("/health")
def health():
    return {"ok": True, "mode": os.environ.get("NAMECOM_MODE", "sandbox")}


@app.post("/v1/recommend", dependencies=[Depends(_verify_api_key)])
async def recommend_domain(req: RecommendRequest):
    """Recommend a domain. Returns decision + candidates."""
    svc = get_service()
    mode = os.environ.get("DOMAINARENA_MODE", "fixture")

    if mode not in ("live", "fixture"):
        raise HTTPException(400, f"Invalid DOMAINARENA_MODE={mode!r} (must be 'live' or 'fixture')")

    if mode == "live" and not os.environ.get("NAMECOM_USERNAME"):
        raise HTTPException(503, "live mode requires Name.com credentials (NAMECOM_USERNAME)")

    try:
        ds, cands = await svc.recommend_async(
            description=req.description,
            primary_job=req.primary_job,
            audience=req.audience,
            constraints=req.constraints,
            mode=mode,
        )
    except ValueError as e:
        raise HTTPException(503 if mode == "live" else 400, str(e))

    return {
        "source": "name.com-live" if mode == "live" else "demo-fixture",
        "decision": {
            "decision_id": ds.decision_id,
            "intent_hash": ds.intent_hash,
            "recommended_domain": ds.recommended_domain,
            "status": ds.status.value,
            "purchase_requires_approval": True,
        },
        "recommendation": {
            "domain": ds.recommended_domain,
            "candidate_id": ds.recommended_candidate_id,
        },
        "candidates": [
            {"domain": c.domain_name, "price": c.inventory.purchase_price}
            for c, _ in cands
        ],
    }


@app.get("/v1/decisions/{decision_id}")
def get_decision(decision_id: str):
    """Get decision state."""
    svc = get_service()
    try:
        ds = svc.get_decision(decision_id)
    except KeyError:
        raise HTTPException(404, "unknown decision")
    return {
        "decision_id": ds.decision_id,
        "domain": ds.recommended_domain,
        "status": ds.status.value,
        "approved": ds.status == DecisionStatus.APPROVED,
        "has_approval_token": ds.approval_token is not None,
        "preparation": ds.preparation,
        "registration": ds.registration,
        "dns_receipt": ds.dns_receipt,
        "verification": ds.verification,
        "api_trace": ds.api_trace[-20:],
    }


class ApproveBody(BaseModel):
    approve: bool


@app.post("/v1/decisions/{decision_id}/approve", dependencies=[Depends(_verify_api_key)])
def approve_decision(decision_id: str, body: ApproveBody):
    """Approve or reject a decision."""
    svc = get_service()
    try:
        if body.approve:
            return svc.approve(decision_id)
        else:
            return svc.reject(decision_id)
    except (KeyError, ValueError) as e:
        raise HTTPException(409, str(e))


class PrepareBody(BaseModel):
    max_price_drift_pct: float = 10.0


@app.post("/v1/decisions/{decision_id}/prepare-registration")
async def prepare_registration(decision_id: str, body: PrepareBody | None = None):
    """Fresh availability + pricing check before purchase."""
    svc = get_service()
    try:
        return await svc.prepare_registration_async(
            decision_id,
            max_price_drift_pct=(body or PrepareBody()).max_price_drift_pct,
        )
    except KeyError:
        raise HTTPException(404, "unknown decision")
    except ValueError as e:
        raise HTTPException(409, str(e))


class RegisterBody(BaseModel):
    approval_token: str
    max_price_drift_pct: float = 10.0


@app.post("/v1/decisions/{decision_id}/register", dependencies=[Depends(_verify_api_key)])
async def register_domain(decision_id: str, body: RegisterBody):
    """Register domain after approval. Idempotent."""
    svc = get_service()
    try:
        return await svc.register_async(
            decision_id,
            body.approval_token,
            body.max_price_drift_pct,
        )
    except KeyError:
        raise HTTPException(404, "unknown decision")
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post("/v1/decisions/{decision_id}/configure-dns", dependencies=[Depends(_verify_api_key)])
async def configure_dns(decision_id: str):
    """Create DNS TXT receipt and verify."""
    svc = get_service()
    try:
        return await svc.configure_dns_async(decision_id)
    except KeyError:
        raise HTTPException(404, "unknown decision")
    except ValueError as e:
        raise HTTPException(409, str(e))
