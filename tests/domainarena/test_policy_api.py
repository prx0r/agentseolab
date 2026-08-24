import pytest
from fastapi.testclient import TestClient

from domainarena.api.http import app, _DECISIONS
from domainarena.models import Candidate, EvidenceVector
from domainarena.optimizer import pareto_front, recommend, weighted_score


def _pair(dom, price, sem=0.8, stab=0.7):
    sld, _, tld = dom.partition(".")
    cand = Candidate(candidate_id=dom, domain_name=dom, generator="t",
                     inventory=__import__("domainarena.models", fromlist=["InventorySnapshot"]).InventorySnapshot(
                         domain_name=dom, sld=sld, tld=tld, purchasable=True,
                         purchase_price=price, renewal_price=price + 2,
                         checked_at="now"))
    ev = EvidenceVector(semantic_transmission=sem, model_stability=stab)
    return cand, ev


class TestPolicy:
    def test_audience_conditioning_flips_winner(self):
        # consumer weights human_recall; agent_api weights task_success/stability
        cands = [
            _pair("velora.com", 10.0, sem=0.5, stab=0.5),
            _pair("jsonrepair.dev", 10.0, sem=0.9, stab=0.9),
        ]
        rec_agent = recommend(cands, "agent_api")
        assert rec_agent.domain_name == "jsonrepair.dev"

    def test_pareto_front_excludes_dominated(self):
        cands = [_pair("a.dev", 10.0, sem=0.9, stab=0.9),
                 _pair("b.dev", 10.0, sem=0.5, stab=0.5),
                 _pair("c.dev", 20.0, sem=0.9, stab=0.9)]
        front = pareto_front(cands)
        assert "a.dev" in front
        assert "b.dev" not in front

    def test_weights_sum_normalized(self):
        s = weighted_score(EvidenceVector(semantic_transmission=1.0), "agent_api")
        assert 0 < s <= 1


@pytest.fixture
def client():
    _DECISIONS.clear()
    return TestClient(app)


class TestHTTPAPI:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["ok"]

    def test_recommend_gated_registration(self, client):
        r = client.post("/v1/recommend", json={
            "description": "Repairs malformed JSON for AI agents",
            "primary_job": "repair JSON",
            "audience": "ai_agent"})
        assert r.status_code == 200
        body = r.json()
        did = body["decision"]["decision_id"]
        assert body["decision"]["purchase_requires_approval"] is True

        # registration blocked without approval
        r = client.post(f"/v1/decisions/{did}/recheck-and-register")
        assert r.status_code == 409

        r = client.post(f"/v1/decisions/{did}/approve", json={"approve": True})
        assert r.json()["approved"] is True

    def test_unknown_decision_404(self, client):
        assert client.post("/v1/decisions/nope/approve",
                           json={"approve": True}).status_code == 404
