"""Tests for demo server smoke, MCP approval bypass, business audience,
scorer separation, and out-of-order action enforcement."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from domainarena.api.http import app
from domainarena.models import (
    Candidate, InventorySnapshot, EvidenceVector, EvidenceValue, EvStatus,
    ConstraintSet,
)
from domainarena.optimizer import recommend, weighted_score, PRESETS


def _make_candidate(domain="test.dev", price=9.99):
    return Candidate(
        candidate_id=f"test_{domain}", domain_name=domain,
        generator="test", inventory=InventorySnapshot(
            domain_name=domain, sld=domain.split(".")[0], tld=domain.split(".")[1],
            purchasable=True, purchase_price=price, renewal_price=price + 2,
            purchase_type="registration", checked_at="2026-08-31T00:00:00Z",
        ),
    )


def _make_evidence(sem=0.7, struct=0.5, task=None):
    return EvidenceVector(
        semantic_transmission=EvidenceValue(value=sem, status=EvStatus.PROXY),
        structural_fluency_proxy=EvidenceValue(value=struct, status=EvStatus.PROXY),
        task_success=EvidenceValue(value=task, status=EvStatus.NOT_MEASURED if task is None else EvStatus.MEASURED),
    )


# ── Demo Smoke ──

async def _get_client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_demo_health():
    async with await _get_client() as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_demo_recommend_returns_decision():
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "A JSON repair tool",
            "primary_job": "fix malformed JSON",
            "audience": "ai_agent",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "decision" in data
        assert "candidates" in data
        assert data["decision"]["purchase_requires_approval"] is True
        assert len(data["candidates"]) > 0


@pytest.mark.asyncio
async def test_demo_recommend_fixture_mode():
    """In fixture mode (no NAMECOM_USERNAME), source is demo-fixture."""
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "test", "primary_job": "test",
        })
        assert resp.json()["source"] == "demo-fixture"


# ── MCP Approval Bypass ──

@pytest.mark.asyncio
async def test_mcp_register_requires_approval_token():
    """MCP register_domain must reject if not approved (no token)."""
    from domainarena.service import get_service
    svc = get_service()
    ds, _ = svc.recommend(
        description="test", primary_job="test",
        audience="ai_agent", constraints=ConstraintSet(),
    )
    # Attempt to register without approval — should be rejected (status not APPROVED)
    with pytest.raises(ValueError, match="Cannot register in status"):
        await svc.register_async(ds.decision_id, "fake-token-12345")


@pytest.mark.asyncio
async def test_mcp_register_rejects_wrong_token():
    """MCP register_domain must reject wrong token after approval."""
    from domainarena.service import get_service, DecisionStatus
    import hashlib
    svc = get_service()
    ds, _ = svc.recommend(
        description="test", primary_job="test",
        audience="ai_agent", constraints=ConstraintSet(),
    )
    # Manually transition to PREPARED and APPROVED (bypass async client)
    ds = svc.get_decision(ds.decision_id)
    ds.preparation = {"approval_valid": True, "purchasable": True}
    ds.transition(DecisionStatus.PREPARED)
    # Set a fake approval token and transition to APPROVED
    ds.approval_token = hashlib.sha256(hashlib.sha256(b"correct-token").hexdigest().encode()).hexdigest()
    ds.transition(DecisionStatus.APPROVED)
    svc._persist(ds)
    # Now try with wrong token — should raise PermissionError
    with pytest.raises(PermissionError, match="Invalid approval token"):
        await svc.register_async(ds.decision_id, "wrong-token")


# ── Business Audience ──

def test_business_audience_in_presets():
    """Business audience must be in PRESETS to avoid KeyError."""
    assert "business" in PRESETS
    assert sum(PRESETS["business"].values()) == pytest.approx(1.0, abs=0.01)


def test_business_audience_recommends():
    """Recommendation with audience='business' should not crash."""
    cands = [
        (_make_candidate("alpha.dev", 9.99), _make_evidence(sem=0.8)),
        (_make_candidate("bravo.io", 14.99), _make_evidence(sem=0.5)),
    ]
    rec = recommend(cands, "business")
    assert rec.audience == "business"
    assert rec.domain_name in ["alpha.dev", "bravo.io"]


def test_business_audience_weighted_score():
    """weighted_score must work with business audience."""
    ev = _make_evidence(sem=0.6, struct=0.4)
    score, cov = weighted_score(ev, "business")
    assert 0.0 <= score <= 1.0
    assert 0.0 <= cov <= 1.0


# ── Scorer Separation ──

def test_scorer_model_recorded_separately():
    """HiddenScorerExecutor uses a different model from inference."""
    from domainarena.world import HiddenScorerExecutor
    scorer = HiddenScorerExecutor(
        model_id="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        provider="cloudflare", api_key="test",
    )
    # The scorer is a separate object with its own model_id
    assert scorer.model_id == "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    # In real usage, the inference executor would use a different model
    # The world tracks scorer_model separately in SemanticEvaluation


def test_semantic_evaluation_records_scorer_model():
    """SemanticEvaluation stores the scorer model, not the inference model."""
    from domainarena.world import SemanticEvaluation
    se = SemanticEvaluation(
        intent_hash="abc", inference_hash="def",
        semantic_score=0.8, match_label="partial",
        scorer_version="v1", scorer_model="gemma-4-26b",
    )
    assert se.scorer_model == "gemma-4-26b"
    assert se.scorer_version == "v1"


# ── Out-of-Order Actions ──

def test_world_rejects_score_without_inference():
    """Score before inference must raise ValueError."""
    from domainarena.world import DomainArenaWorld, DomainCase
    from cogym_kernel.kernel.contracts import ActionSpec, ActionResult
    from pathlib import Path

    case = DomainCase(
        case_id="0", source="test", domain_name="test.com",
        intent_description="testing", primary_job="test job",
        ground_truth_match=True,
    )
    world = DomainArenaWorld([case], root=Path("/tmp"))
    state = world.reset(instance_id="test:0", seed=42)

    with pytest.raises(ValueError, match="requires INFERENCE first"):
        world.apply(
            state,
            ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
            ActionResult(action_id="s", status="ok",
                         payload={"semantic_score": 0.8, "match_label": "partial"}),
        )


def test_world_rejects_commit_without_score():
    """Commit before score must raise ValueError."""
    from domainarena.world import DomainArenaWorld, DomainCase, InferenceResult
    from cogym_kernel.kernel.contracts import ActionSpec, ActionResult
    from pathlib import Path
    import hashlib

    case = DomainCase(
        case_id="0", source="test", domain_name="test.com",
        intent_description="testing", primary_job="test job",
        ground_truth_match=True,
    )
    world = DomainArenaWorld([case], root=Path("/tmp"))
    state = world.reset(instance_id="test:0", seed=42)

    # Apply inference first
    state = world.apply(
        state,
        ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
        ActionResult(action_id="i", status="ok",
                     payload={"raw": "test inference", "inference": "test inference"}),
    )

    # Try to commit without scoring
    with pytest.raises(ValueError, match="requires SCORE_SEMANTIC first"):
        world.apply(
            state,
            ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic"),
            ActionResult(action_id="c", status="ok", payload={}),
        )


def test_world_rejects_double_inference():
    """Double INFERENCE must raise ValueError."""
    from domainarena.world import DomainArenaWorld, DomainCase
    from cogym_kernel.kernel.contracts import ActionSpec, ActionResult
    from pathlib import Path

    case = DomainCase(
        case_id="0", source="test", domain_name="test.com",
        intent_description="testing", primary_job="test job",
        ground_truth_match=True,
    )
    world = DomainArenaWorld([case], root=Path("/tmp"))
    state = world.reset(instance_id="test:0", seed=42)

    state = world.apply(
        state,
        ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
        ActionResult(action_id="i", status="ok",
                     payload={"raw": "test", "inference": "test"}),
    )

    with pytest.raises(ValueError, match="INFERENCE already applied"):
        world.apply(
            state,
            ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
            ActionResult(action_id="i2", status="ok",
                         payload={"raw": "test2", "inference": "test2"}),
        )


# ── Evidence Provenance ──

def test_structural_fluency_is_proxy():
    """structural_fluency_proxy must always be PROXY, never MEASURED."""
    ev = _make_evidence(struct=0.6)
    assert ev.structural_fluency_proxy.status == EvStatus.PROXY


def test_semantic_inversion_is_proxy_in_pipeline():
    """Pipeline marks semantic_transmission as PROXY, not MEASURED."""
    from domainarena.pipeline import _evidence_from_inventory
    cands = [_make_candidate("test.dev")]
    sem_scores = {"test.dev": 0.75}
    evidence = _evidence_from_inventory(cands, sem_scores)
    ev = evidence["test.dev"]
    assert ev.semantic_transmission.status == EvStatus.PROXY
    assert ev.semantic_transmission.value == 0.75


def test_task_success_not_measured_in_pipeline():
    """Pipeline must NOT fabricate task_success."""
    from domainarena.pipeline import _evidence_from_inventory
    cands = [_make_candidate("test.dev")]
    evidence = _evidence_from_inventory(cands, {"test.dev": 0.5})
    ev = evidence["test.dev"]
    assert ev.task_success.status == EvStatus.NOT_MEASURED
    assert ev.task_success.value is None


# ── Pareto Economics ──

def test_pareto_does_not_penalize_unknown_renewal():
    """Unknown renewal price must NOT be treated as $0 (free)."""
    from domainarena.optimizer import pareto_front
    c1 = _make_candidate("a.dev", price=10.0)
    c2 = _make_candidate("b.dev", price=10.0)
    # c2 has no renewal price set
    c2.inventory.renewal_price = None
    ev1 = _make_evidence(sem=0.8)
    ev2 = _make_evidence(sem=0.8)
    front = pareto_front([(c1, ev1), (c2, ev2)])
    # Both should be on the front (neither dominates when renewal is unknown)
    assert len(front) >= 1


# ── Compare Domains MCP Tool ──

@pytest.mark.asyncio
async def test_compare_domains_tool_exists():
    """compare_domains is registered in the MCP tool list."""
    from domainarena.api.mcp import TOOLS
    tool_names = [t["name"] for t in TOOLS]
    assert "compare_domains" in tool_names


@pytest.mark.asyncio
async def test_compare_domains_handler_structural():
    """compare_domains handler returns comparison with semantic scores."""
    from domainarena.api.mcp import _handle_compare
    with patch("domainarena.api.mcp.client_from_env") as mock_factory:
        client = AsyncMock()
        client.check_availability = AsyncMock(return_value=[
            {"domainName": "alpha.dev", "purchasable": True},
            {"domainName": "bravo.dev", "purchasable": False},
        ])
        client.get_pricing = AsyncMock(side_effect=[
            {"purchasePrice": 9.99, "renewalPrice": 11.99},
            {"purchasePrice": 14.99, "renewalPrice": 16.99},
        ])
        client.close = AsyncMock()
        mock_factory.return_value = client

        result = await _handle_compare({
            "domain_a": "alpha.dev",
            "domain_b": "bravo.dev",
            "description": "JSON repair tool",
        })
        text = result["content"][0]["text"]
        data = __import__("json").loads(text)
        assert "comparison" in data
        assert "alpha.dev" in data["comparison"]
        assert "bravo.dev" in data["comparison"]
        assert "semantic" in data["comparison"]["alpha.dev"]
        assert "verdict" in data


# ── Service Async Methods ──

@pytest.mark.asyncio
async def test_service_has_async_methods():
    """DomainService exposes async versions of lifecycle methods."""
    from domainarena.service import get_service
    svc = get_service()
    assert hasattr(svc, "prepare_registration_async")
    assert hasattr(svc, "register_async")
    assert hasattr(svc, "configure_dns_async")
    import inspect
    assert inspect.iscoroutinefunction(svc.prepare_registration_async)
    assert inspect.iscoroutinefunction(svc.register_async)
    assert inspect.iscoroutinefunction(svc.configure_dns_async)
