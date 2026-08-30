"""E2E mock test for the full DomainArena lifecycle via HTTP API.

Tests the complete flow:
1. Recommend domain (fixture mode)
2. Get decision state
3. Prepare registration (mocked service)
4. Approve decision
5. Register domain (mocked service)
6. Configure DNS (mocked service)

The service layer uses asyncio.run() internally which conflicts with async
test context, so we mock the service methods for prepare/register/DNS.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from domainarena.api.http import app
from domainarena.service import get_service, DecisionStatus


@pytest.fixture
def mock_service():
    """Mock the DomainService async lifecycle methods."""
    svc = get_service()
    original_prepare_async = svc.prepare_registration_async
    original_register_async = svc.register_async
    original_configure_dns_async = svc.configure_dns_async

    async def fake_prepare_async(decision_id, max_price_drift_pct=10.0):
        ds = svc.get_decision(decision_id)
        ds.preparation = {
            "approval_valid": True, "purchasable": True,
            "status": "PREPARED", "domain": ds.recommended_domain,
        }
        ds.transition(DecisionStatus.PREPARED)
        svc._persist(ds)
        return ds.preparation

    async def fake_register_async(decision_id, approval_token, max_price_drift_pct=10.0):
        ds = svc.get_decision(decision_id)
        if ds.status != DecisionStatus.APPROVED:
            raise ValueError(f"Cannot register in status {ds.status.value}")
        if not ds.approval_token:
            raise ValueError("No approval token")
        import hmac
        if not hmac.compare_digest(ds.approval_token, approval_token):
            raise PermissionError("Invalid approval token")
        ds.registration = {"decision_id": decision_id, "domain": ds.recommended_domain}
        ds.transition(DecisionStatus.REGISTERED)
        svc._persist(ds)
        return ds.registration

    async def fake_configure_dns_async(decision_id):
        ds = svc.get_decision(decision_id)
        import hashlib
        receipt_hash = hashlib.sha256(f"{decision_id}|{ds.recommended_domain}".encode()).hexdigest()
        ds.dns_receipt = {"receipt_hash": receipt_hash, "dns_receipt_verified": True}
        ds.transition(DecisionStatus.DNS_CONFIGURED)
        svc._persist(ds)
        return {**ds.dns_receipt, "status": "DNS_CONFIGURED"}

    svc.prepare_registration_async = fake_prepare_async
    svc.register_async = fake_register_async
    svc.configure_dns_async = fake_configure_dns_async
    yield svc
    svc.prepare_registration_async = original_prepare_async
    svc.register_async = original_register_async
    svc.configure_dns_async = original_configure_dns_async


async def _get_client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_full_lifecycle(mock_service):
    """Test the complete recommend → prepare → approve → register → DNS flow."""
    async with await _get_client() as ac:
        # 1. Recommend
        resp = await ac.post("/v1/recommend", json={
            "description": "A JSON repair tool",
            "primary_job": "fix malformed JSON",
            "audience": "developer",
        })
        assert resp.status_code == 200
        data = resp.json()
        decision_id = data["decision"]["decision_id"]
        assert data["source"] == "demo-fixture"
        assert data["decision"]["purchase_requires_approval"] is True

        # 2. Get decision
        resp = await ac.get(f"/v1/decisions/{decision_id}")
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "RECOMMENDED"

        # 3. Prepare registration (mocked)
        resp = await ac.post(f"/v1/decisions/{decision_id}/prepare-registration")
        assert resp.status_code == 200
        prep = resp.json()
        assert prep["status"] == "PREPARED"

        # 4. Approve
        resp = await ac.post(f"/v1/decisions/{decision_id}/approve",
                            json={"approve": True})
        assert resp.status_code == 200
        approval_data = resp.json()
        assert approval_data["approved"] is True
        approval_token = approval_data["approval_token"]
        assert len(approval_token) == 32

        # 5. Register (mocked)
        resp = await ac.post(f"/v1/decisions/{decision_id}/register",
                            json={"approval_token": approval_token})
        assert resp.status_code == 200

        # 6. Configure DNS (mocked)
        resp = await ac.post(f"/v1/decisions/{decision_id}/configure-dns")
        assert resp.status_code == 200
        dns = resp.json()
        assert dns["dns_receipt_verified"] is True


@pytest.mark.asyncio
async def test_approve_generates_token(mock_service):
    """Approval generates a valid token after preparation."""
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "test", "primary_job": "test",
        })
        decision_id = resp.json()["decision"]["decision_id"]

        # Prepare first (required for approval)
        await ac.post(f"/v1/decisions/{decision_id}/prepare-registration")

        # Approve
        resp = await ac.post(f"/v1/decisions/{decision_id}/approve",
                            json={"approve": True})
        token = resp.json()["approval_token"]
        assert len(token) == 32


@pytest.mark.asyncio
async def test_reject_clears_token(mock_service):
    """Rejecting clears the approval token."""
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "test", "primary_job": "test",
        })
        decision_id = resp.json()["decision"]["decision_id"]

        # Prepare first
        await ac.post(f"/v1/decisions/{decision_id}/prepare-registration")

        # Approve then reject
        await ac.post(f"/v1/decisions/{decision_id}/approve",
                     json={"approve": True})
        resp = await ac.post(f"/v1/decisions/{decision_id}/approve",
                            json={"approve": False})
        assert resp.json()["approved"] is False


@pytest.mark.asyncio
async def test_register_rejects_wrong_token(mock_service):
    """Registration fails with wrong approval token."""
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "test", "primary_job": "test",
        })
        decision_id = resp.json()["decision"]["decision_id"]

        # Prepare + approve
        await ac.post(f"/v1/decisions/{decision_id}/prepare-registration")
        await ac.post(f"/v1/decisions/{decision_id}/approve",
                     json={"approve": True})

        resp = await ac.post(f"/v1/decisions/{decision_id}/register",
                            json={"approval_token": "wrong-token"})
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_register_rejects_no_token(mock_service):
    """Registration fails without approval token."""
    async with await _get_client() as ac:
        resp = await ac.post("/v1/recommend", json={
            "description": "test", "primary_job": "test",
        })
        decision_id = resp.json()["decision"]["decision_id"]

        resp = await ac.post(f"/v1/decisions/{decision_id}/register",
                            json={"approval_token": ""})
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_health(mock_service):
    """Health endpoint works."""
    async with await _get_client() as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_unknown_decision_404(mock_service):
    """Unknown decision returns 404."""
    async with await _get_client() as ac:
        resp = await ac.get("/v1/decisions/nonexistent")
        assert resp.status_code == 404


# ── Persistence roundtrip ──

def test_persist_roundtrip_preserves_decision_basis():
    """_persist() must save decision_basis and _load() must restore it."""
    import tempfile, json
    from domainarena.service import DomainService, DecisionStatus
    from domainarena.models import EvidenceVector, EvidenceValue, EvStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        svc = DomainService()
        svc._store_dir = __import__("pathlib").Path(tmpdir)

        # Create a decision with known decision_basis
        ds, _ = svc.recommend(
            description="test desc", primary_job="test job",
            audience="ai_agent")
        basis = {"description": "test desc", "primary_job": "test job",
                 "audience": "ai_agent", "custom_key": "custom_value"}
        ds.decision_basis = basis
        svc._persist(ds)

        # Clear in-memory cache and reload from disk
        did = ds.decision_id
        del svc._decisions[did]
        loaded = svc._load(did)

        assert loaded is not None
        assert loaded.decision_basis == basis
        assert loaded.decision_basis["custom_key"] == "custom_value"


def test_persist_roundtrip_preserves_evidence():
    """_persist() must save evidence and _load() must restore it."""
    import tempfile
    from domainarena.service import DomainService
    from domainarena.models import EvStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        svc = DomainService()
        svc._store_dir = __import__("pathlib").Path(tmpdir)

        ds, _ = svc.recommend(
            description="test", primary_job="test",
            audience="ai_agent")
        # The evidence should have structural_fluency_proxy set (from _fixture_candidates)
        orig_ev = ds.evidence
        assert orig_ev.structural_fluency_proxy.value is not None
        orig_val = orig_ev.structural_fluency_proxy.value

        svc._persist(ds)
        did = ds.decision_id
        del svc._decisions[did]
        loaded = svc._load(did)

        assert loaded is not None
        assert loaded.evidence.structural_fluency_proxy.value == orig_val
        assert loaded.evidence.structural_fluency_proxy.status == EvStatus.PROXY


def test_reject_transitions_to_rejected():
    """reject() must transition RECOMMENDED → REJECTED."""
    from domainarena.service import get_service
    svc = get_service()
    ds, _ = svc.recommend(
        description="test", primary_job="test",
        audience="ai_agent")
    result = svc.reject(ds.decision_id)
    assert result["status"] == "REJECTED"
    ds2 = svc.get_decision(ds.decision_id)
    assert ds2.status == DecisionStatus.REJECTED
