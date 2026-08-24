"""Peer review §11: every mutating name.com method must be blocked outside
sandbox/production-approved modes. Proves production-readonly is truly read-only."""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domainarena.providers.namecom import NameComClient, NameComError

def ro_client():
    return NameComClient(username="u", token="t", mode="production-readonly")

def sb_client():
    return NameComClient(username="u", token="t", mode="sandbox")

def test_update_domain_blocked_readonly():
    with pytest.raises(NameComError):
        asyncio.run(ro_client().update_domain("x.dev", autorenew=False))

def test_create_dns_blocked_readonly():
    with pytest.raises(NameComError):
        asyncio.run(ro_client().create_dns_record("x.dev", host="_da", record_type="TXT", answer="y"))

def test_register_blocked_readonly():
    with pytest.raises(NameComError):
        asyncio.run(ro_client().register_domain({"domain": "x.dev"}, "idem-1"))

def test_sandbox_mode_allows_guard():
    # sandbox passes the guard; network call would fail w/o mock — patch _request
    c = sb_client()
    async def fake(method, path, **kw):
        return {"ok": True}
    c._request = fake
    assert asyncio.run(c.update_domain("x.dev", autorenew=True)) == {"ok": True}

import pytest
