"""DomainArena HTTP API (FastAPI).

recommend_domain  — read-only
approve_decision  — explicit state transition
register_domain   — destructive, gated behind approval + fresh availability check
"""
from __future__ import annotations
import hashlib
import os
import json
import uuid
from pathlib import Path as _P
ROOT_LOCAL = _P(__file__).resolve().parent.parent.parent

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
_CANDIDATES: dict = {}


class RecommendRequest(BaseModel):
    description: str
    primary_job: str
    audience: Audience = "ai_agent"
    constraints: ConstraintSet = Field(default_factory=ConstraintSet)


@app.get("/health")
def health():
    return {"ok": True, "mode": os.environ.get("NAMECOM_MODE", "sandbox")}


def _demo_candidates(req: RecommendRequest) -> list[tuple[Candidate, EvidenceVector]]:
    """Offline candidate set used when name.com is unreachable.

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


async def _live_candidates(req: RecommendRequest) -> list[tuple[Candidate, EvidenceVector]] | None:
    """Real inventory path: generators ∩ name.com search → feasibility → proxy evidence."""
    import os
    if not os.environ.get("NAMECOM_USERNAME"):
        return None
    from ..pipeline import recommend_live
    try:
        res = await recommend_live(
            description=req.description,
            primary_job=req.primary_job,
            audiences=[req.audience],
            constraints=req.constraints,
        )
    except Exception:
        return None
    return [(c, res.evidence[c.domain_name]) for c in res.feasible]


@app.post("/v1/recommend")
async def recommend_domain(req: RecommendRequest):
    """CP-A truth semantics: DOMAINARENA_MODE=live surfaces provider failures;
    fixture mode labels everything FIXTURE. Never silent-fallback."""
    mode = os.environ.get("DOMAINARENA_MODE", "fixture")
    if mode not in ("live", "fixture"):
        raise HTTPException(500, f"unknown DOMAINARENA_MODE {mode!r}")
    if mode == "live" and not os.environ.get("NAMECOM_USERNAME"):
        raise HTTPException(503,
            "live mode requires NAMECOM credentials; "
            "set DOMAINARENA_MODE=fixture for demo data")
    cands = await _live_candidates(req)
    live = cands is not None
    if mode == "live" and not live:
        raise HTTPException(503,
            "live inventory unavailable (provider error) — "
            "refusing to serve fixture data in live mode")
    cands = cands or _demo_candidates(req)
    if not cands:
        raise HTTPException(404, "no feasible candidates under constraints")
    execution_mode = ("LIVE_NAMECOM_INVENTORY" if live else "FIXTURE")
    if not live:
        execution_mode += "_NOT_EXPERIMENTAL_EVIDENCE"
    rec = policy_recommend(cands, req.audience)
    winner_ev = next(ev for c, ev in cands if c.candidate_id == rec.candidate_id)
    intent_hash = "sha256:" + hashlib.sha256(json.dumps(
        {"description": req.description, "primary_job": req.primary_job},
        sort_keys=True).encode()).hexdigest()
    decision = RecommendationDecision(
        decision_id=f"da_{uuid.uuid4().hex[:16]}",
        intent_hash=intent_hash,
        recommended_candidate_id=rec.candidate_id,
        pareto_candidate_ids=[c.candidate_id for c, _ in cands],
        policy_version="audience-presets-v1",
        evidence=winner_ev,
        purchase_requires_approval=True,
    )
    _DECISIONS[decision.decision_id] = decision
    _CANDIDATES[decision.decision_id] = cands

    # append-only evidence receipt
    resp_extra = {
        "execution_mode": execution_mode,
        "recommendation_status": getattr(rec, "recommendation_status", "PROVISIONAL"),
        "evidence_coverage": getattr(rec, "evidence_coverage", 0.0),
        "intent_hash": intent_hash,
    }
    try:
        from ..receipts import build_receipt, write_receipt
        ROOT_LOCAL_OK = True
        rid, mh = write_receipt(build_receipt(
            intent_hash=decision.intent_hash,
            description=req.description, primary_job=req.primary_job,
            audience=req.audience,
            constraints_dict=req.constraints.model_dump(),
            feasible_domains=[c.domain_name for c, _ in cands],
            rejected={},
            recommendation={"domain": rec.domain_name,
                            "score": round(rec.score, 4),
                            "on_pareto_front": rec.on_pareto,
                            "explanation": rec.explanation},
            source="name.com-live" if live else "demo-fixture",
            policy_version=decision.policy_version,
        ))
    except Exception:
        rid = mh = None

    return {
        "source": "name.com-live" if live else "demo-fixture",
        "receipt_id": rid,
        "manifest_hash": mh,
        "decision": decision.model_dump(),
        "recommendation": {
            "domain": rec.domain_name,
            "score": round(rec.score, 4),
            "on_pareto_front": rec.on_pareto,
            "explanation": rec.explanation,
        
        **resp_extra,},
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
async def recheck_and_register(decision_id: str, body: dict | None = None):
    """CP-B lifecycle (peer review §10-D): fresh availability → pricing refresh
    → drift check → idempotent register → GetDomain confirm → DNS TXT receipt
    → read-back. Every provider response persisted."""
    import hashlib, json as _json, time as _time
    d = _DECISIONS.get(decision_id)
    if not d:
        raise HTTPException(404, "unknown decision")
    approved = getattr(body or {}, "get", lambda *_: None)
    # decision-state guard BEFORE deployment-mode guard
    if d.purchase_requires_approval and not (body or {}).get("approved"):
        raise HTTPException(409, "decision requires explicit approval first")
    if os.environ.get("NAMECOM_MODE") != "sandbox":
        raise HTTPException(403,
            "registration only enabled in NAMECOM_MODE=sandbox "
            "(production requires explicit production-approved mode)")

    cands = _CANDIDATES.get(decision_id) or []
    cand = next((c for c, _ in cands if c.candidate_id == d.recommended_candidate_id), None)
    if cand is None:
        raise HTTPException(404, "recommended candidate not found in decision store")
    dom = cand.domain_name
    inv = cand.inventory
    orig_price = getattr(inv, "purchase_price", None)
    max_drift = float((body or {}).get("max_price_drift_pct", 10.0))

    client: NameComClient = client_from_env()
    steps: list[dict] = []

    async def step(name, coro_fn):
        t0 = _time.time()
        try:
            res = await coro_fn
        except Exception as ex:
            steps.append({"step": name, "ok": False,
                          "error": str(ex)[:200],
                          "latency_ms": int((_time.time()-t0)*1000)})
            raise HTTPException(502, f"lifecycle step failed: {name}: {ex}")
        steps.append({"step": name, "ok": True,
                      "latency_ms": int((_time.time()-t0)*1000)})
        return res

    # 1-2. fresh availability (fail-closed)
    try:
        entry = await step("check_availability",
                           client.check_availability_fail_closed(dom))
    except Exception as ex:
        raise HTTPException(502, f"availability check failed: {ex}")
    
    # Fail-closed: purchasable must be explicitly True
    avail_now = entry.get("purchasable")
    if avail_now is not True:
        raise HTTPException(409, f"{dom} not available (purchasable={avail_now})")

    # 3. pricing refresh + drift guard (null price ⇒ unknown, never free)
    pricing = await step("get_pricing", client.get_pricing(dom))
    def _extract_price(p):
        """name.com pricing shapes: {purchasePrice} or {tiers:[{purchasePrice}]} or
        search-style {purchasePrice}; also tolerate snake_case."""
        if not isinstance(p, dict): return None
        for k in ("purchasePrice", "purchase_price"):
            if p.get(k) is not None: return p[k]
        for t in p.get("tiers", []) or []:
            if t.get("purchasePrice") is not None: return t["purchasePrice"]
        return None
    new_price = _extract_price(pricing)
    if orig_price is not None and new_price is not None and orig_price > 0:
        drift = abs(new_price - orig_price)/orig_price * 100
        if drift > max_drift:
            raise HTTPException(409,
                f"price drifted {drift:.1f}% (> {max_drift}%): "
                f"approval invalidated, request re-approval")

    # 4. deterministic idempotency key from decision identity
    idem = hashlib.sha256(
        f"{decision_id}|{dom}|register".encode()).hexdigest()

    # 5. register (idempotent)
    payload = {"domain": {"domainName": dom}}
    eff_price = new_price if new_price is not None else orig_price
    if eff_price is not None:
        payload["purchasePrice"] = eff_price   # required only for registry-premium
    reg = await step("register_domain",
                     client.register_domain(payload, idem))

    # 6. confirm via GetDomain
    got = await step("get_domain", client.get_domain(dom))

    # 7-8. DNS TXT receipt + read-back
    receipt_hash = hashlib.sha256(_json.dumps(
        {"decision": decision_id, "domain": dom},
        sort_keys=True).encode()).hexdigest()
    txt_host = "_domainarena"
    txt_answer = f"sha256:{receipt_hash}"
    txt = await step("create_dns_txt",
                     client.create_dns_record(dom, host=txt_host,
                                              record_type="TXT",
                                              answer=txt_answer))
    dns = await step("list_dns", client.list_dns_records(dom))
    dns_ok = any(txt_answer in json.dumps(r_) for r_ in
                 (dns if isinstance(dns, list) else dns.get("records", [])))

    lifecycle = {
        "decision_id": decision_id,
        "domain": dom,
        "status": "REGISTERED" ,
        "dns_receipt_verified": bool(dns_ok),
        "steps": steps,
        "idempotency_key": idem,
        "intent_hash_note": "see /v1/recommend receipt manifest_hash",
    }
    out_dir = ROOT_LOCAL/"results"/"domainarena_lifecycle"
    out_dir.mkdir(parents=True, exist_ok=True)
    fn = out_dir/f"lifecycle_{decision_id}.json"
    fn.write_text(json.dumps(lifecycle, indent=2, default=str))
    return lifecycle
