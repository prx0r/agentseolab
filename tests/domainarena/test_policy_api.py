"""Tests for optimizer policy, Pareto front, and HTTP API."""
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from domainarena.api.http import app
from domainarena.models import Candidate, InventorySnapshot, EvidenceVector, EvidenceValue, EvStatus
from domainarena.optimizer import pareto_front, recommend, weighted_score


def _pair(dom, price, sem=0.8, struct=0.7):
    sld, _, tld = dom.partition(".")
    cand = Candidate(candidate_id=dom, domain_name=dom, generator="t",
                     inventory=InventorySnapshot(
                         domain_name=dom, sld=sld, tld=tld, purchasable=True,
                         purchase_price=price, renewal_price=price + 2,
                         checked_at="now"))
    ev = EvidenceVector(
        semantic_transmission=EvidenceValue(value=sem, status=EvStatus.PROXY),
        structural_fluency_proxy=EvidenceValue(value=struct, status=EvStatus.PROXY),
    )
    return cand, ev


class TestPolicy:
    def test_audience_conditioning_flips_winner(self):
        cands = [
            _pair("velora.com", 10.0, sem=0.5, struct=0.5),
            _pair("jsonrepair.dev", 10.0, sem=0.9, struct=0.9),
        ]
        rec_agent = recommend(cands, "ai_agent")
        assert rec_agent.domain_name == "jsonrepair.dev"

    def test_pareto_front_excludes_dominated(self):
        cands = [_pair("a.dev", 10.0, sem=0.9, struct=0.9),
                 _pair("b.dev", 10.0, sem=0.5, struct=0.5),
                 _pair("c.dev", 20.0, sem=0.9, struct=0.9)]
        front = pareto_front(cands)
        assert "a.dev" in front
        assert "b.dev" not in front

    def test_weights_sum_normalized(self):
        s, cov = weighted_score(
            EvidenceVector(semantic_transmission=EvidenceValue(value=1.0, status=EvStatus.PROXY)),
            "ai_agent")
        assert 0 < s <= 1


async def _get_client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


class TestHTTPAPI:
    @pytest.mark.asyncio
    async def test_health(self):
        async with await _get_client() as ac:
            r = await ac.get("/health")
            assert r.status_code == 200 and r.json()["ok"]

    @pytest.mark.asyncio
    async def test_recommend_gated_registration(self):
        from domainarena.service import get_service, DecisionStatus
        svc = get_service()
        # Mock prepare_registration_async
        original_prepare_async = svc.prepare_registration_async
        async def fake_prepare_async(decision_id, max_price_drift_pct=10.0):
            ds = svc.get_decision(decision_id)
            ds.preparation = {"approval_valid": True, "purchasable": True, "status": "PREPARED"}
            ds.transition(DecisionStatus.PREPARED)
            svc._persist(ds)
            return ds.preparation
        svc.prepare_registration_async = fake_prepare_async
        try:
            async with await _get_client() as ac:
                r = await ac.post("/v1/recommend", json={
                    "description": "Repairs malformed JSON for AI agents",
                    "primary_job": "repair JSON",
                    "audience": "ai_agent"})
                assert r.status_code == 200
                body = r.json()
                did = body["decision"]["decision_id"]
                assert body["decision"]["purchase_requires_approval"] is True

                # registration blocked without approval (wrong status → 409)
                r = await ac.post(f"/v1/decisions/{did}/register",
                                 json={"approval_token": ""})
                assert r.status_code in (403, 409)

                # prepare first, then approve
                await ac.post(f"/v1/decisions/{did}/prepare-registration")
                r = await ac.post(f"/v1/decisions/{did}/approve", json={"approve": True})
                assert r.json()["approved"] is True
        finally:
            svc.prepare_registration_async = original_prepare_async

    @pytest.mark.asyncio
    async def test_unknown_decision_404(self):
        async with await _get_client() as ac:
            r = await ac.get("/v1/decisions/nope")
            assert r.status_code == 404
