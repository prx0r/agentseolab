import json

import httpx
import pytest
import respx

from domainarena.constraints import feasible
from domainarena.models import ConstraintSet
from domainarena.providers.namecom import (
    NameComClient,
    NameComError,
    client_from_env,
)

BASE = "https://api.dev.name.com"

SEARCH_RESPONSE = {
    "results": [
        {"domainName": "jsonrepair.dev", "purchasable": True, "sld": "jsonrepair",
         "tld": "dev", "premium": False, "purchasePrice": 9.99,
         "renewalPrice": 11.99, "purchaseType": "registration"},
        {"domainName": "velora.ai", "purchasable": True, "sld": "velora",
         "tld": "ai", "premium": True, "purchasePrice": 70.0,
         "renewalPrice": 80.0, "purchaseType": "registration"},
        {"domainName": "taken.com", "purchasable": False, "sld": "taken",
         "tld": "com", "purchaseType": "registration", "reason": "unavailable"},
    ]
}


def _client():
    return NameComClient("testuser", "testtoken", base_url=BASE)


@pytest.mark.asyncio
@respx.mock
async def test_search_parses_inventory_snapshots():
    respx.post(f"{BASE}/core/v1/domains:search").mock(
        return_value=httpx.Response(200, json=SEARCH_RESPONSE))
    c = _client()
    try:
        snaps = await c.search("jsonrepair", ["dev", "ai", "com"])
    finally:
        await c.close()
    assert [s.domain_name for s in snaps] == ["jsonrepair.dev", "velora.ai", "taken.com"]
    assert snaps[1].premium and snaps[1].purchase_price == 70.0

    keep, rejected = c.filter_feasible(snaps, ConstraintSet(max_purchase_price=20))
    assert [s.domain_name for s in keep] == ["jsonrepair.dev"]
    assert "premium" in rejected["velora.ai"]
    assert set(rejected["taken.com"]) == {"not_purchasable", "purchase_budget"}


@pytest.mark.asyncio
@respx.mock
async def test_search_sends_tld_filter_and_registration_type():
    route = respx.post(f"{BASE}/core/v1/domains:search").mock(
        return_value=httpx.Response(200, json={"results": []}))
    c = _client()
    try:
        await c.search("kw", [".DEV", "io"])
    finally:
        await c.close()
    body = json.loads(route.calls[0].request.content)
    assert body["tldFilter"] == ["dev", "io"]
    assert body["purchaseType"] == "registration"


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status", [401, 429, 500])
async def test_error_contract(status):
    respx.post(f"{BASE}/core/v1/domains:search").mock(
        return_value=httpx.Response(status, json={"message": "err"}))
    c = NameComClient("u", "t", base_url=BASE, max_retries=0)
    try:
        with pytest.raises(NameComError) as ei:
            await c.search("kw", ["dev"])
        assert ei.value.status == status
    finally:
        await c.close()


@pytest.mark.asyncio
@respx.mock
async def test_check_availability_bounds():
    respx.post(f"{BASE}/core/v1/domains:checkAvailability").mock(
        return_value=httpx.Response(200, json={"results": []}))
    c = _client()
    try:
        with pytest.raises(ValueError):
            await c.check_availability([f"d{i}.com" for i in range(51)])
        await c.check_availability(["a.dev"])
    finally:
        await c.close()


@pytest.mark.asyncio
@respx.mock
async def test_register_uses_idempotency_key():
    route = respx.post(f"{BASE}/core/v1/domains").mock(
        return_value=httpx.Response(201, json={"domainName": "x.dev"}))
    c = _client()
    try:
        await c.register_domain({"domain": {"name": "x.dev"}}, idempotency_key="idem-123")
    finally:
        await c.close()
    req = route.calls[0].request
    assert req.headers.get("X-Idempotency-Key") == "idem-123"


@pytest.mark.asyncio
@respx.mock
async def test_dns_receipt_roundtrip():
    create = respx.post(f"{BASE}/core/v1/domains/x.dev/records").mock(
        return_value=httpx.Response(201, json={"host": "_domainarena"}))
    listing = respx.get(f"{BASE}/core/v1/domains/x.dev/records").mock(
        return_value=httpx.Response(200, json={"records": [
            {"host": "_domainarena", "type": "TXT", "answer": "decision=da_test"}]}))
    c = _client()
    try:
        await c.create_dns_record("x.dev", host="_domainarena", record_type="TXT",
                                  answer="decision=da_test")
        records = await c.list_dns_records("x.dev")
    finally:
        await c.close()
    body = json.loads(create.calls[0].request.content)
    assert body == {"host": "_domainarena", "type": "TXT",
                    "answer": "decision=da_test", "ttl": 300}
    assert records[0]["answer"] == "decision=da_test"


def test_client_from_env_defaults_to_sandbox(monkeypatch):
    monkeypatch.delenv("NAMECOM_BASE_URL", raising=False)
    c = client_from_env()
    assert str(c._client.base_url).rstrip("/") == BASE


@pytest.mark.asyncio
async def test_timeout_retries_then_raises():
    with respx.mock:
        respx.post(f"{BASE}/core/v1/domains:search").mock(side_effect=httpx.TimeoutException("t"))
        c = NameComClient("u", "t", base_url=BASE, max_retries=1)
        with pytest.raises(httpx.TimeoutException):
            await c.search("kw", ["dev"])
        await c.close()
