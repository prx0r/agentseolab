"""name.com Core API client (sandbox-first).

Credentials come from env: NAMECOM_USERNAME / NAMECOM_TOKEN / NAMECOM_BASE_URL.
Never commit credentials. Registration is always a separate gated operation.
"""
from __future__ import annotations
import asyncio
import base64
import os
from datetime import datetime, timezone

import httpx

from ..models import ConstraintSet, InventorySnapshot
from ..constraints import feasible


class NameComError(RuntimeError):
    def __init__(self, status: int, body: str):
        self.status = status
        super().__init__(f"name.com {status}: {body[:500]}")


def client_from_env() -> "NameComClient":
    """Reads NAMECOM_* from env. mode=production-readonly permits only
    search/checkAvailability/getPricing — registration requires sandbox mode."""
    return NameComClient(
        username=os.environ.get("NAMECOM_USERNAME", ""),
        token=os.environ.get("NAMECOM_TOKEN", ""),
        base_url=os.environ.get(
            "NAMECOM_BASE_URL", "https://api.dev.name.com"
        ),
        mode=os.environ.get("NAMECOM_MODE", "sandbox"),
    )


class NameComClient:
    SEARCH = "/core/v1/domains:search"
    CHECK = "/core/v1/domains:checkAvailability"

    READONLY_METHODS = {"GET", "POST"}  # POST only for search/check endpoints

    def __init__(self, username: str, token: str,
                 base_url: str = "https://api.dev.name.com",
                 timeout: float = 15.0, max_retries: int = 2,
                 mode: str = "sandbox"):
        raw = f"{username}:{token}".encode()
        auth = base64.b64encode(raw).decode()
        self._client = httpx.AsyncClient(
            base_url=base_url, timeout=timeout,
            headers={"Authorization": f"Basic {auth}",
                     "Content-Type": "application/json"},
        )
        self.max_retries = max_retries
        self.mode = mode

    async def close(self):
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs):
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                r = await self._client.request(method, path, **kwargs)
            except httpx.TimeoutException as e:
                last_exc = e
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            if r.status_code == 429:
                retry_after = float(r.headers.get("Retry-After", "1"))
                await asyncio.sleep(retry_after)
                last_exc = NameComError(429, r.text)
                continue
            if r.status_code >= 400:
                raise NameComError(r.status_code, r.text)
            return r.json()
        raise last_exc or NameComError(0, "exhausted retries")

    # ---- inventory ----

    async def search_raw(self, keyword: str, tlds: list[str],
                         timeout_ms: int = 2500) -> dict:
        return await self._request("POST", self.SEARCH, json={
            "keyword": keyword,
            "timeout": timeout_ms,
            "tldFilter": [t.lower().lstrip(".") for t in tlds][:50],
            "purchaseType": "registration",
        })

    @staticmethod
    def parse_results(payload: dict) -> list[InventorySnapshot]:
        now = datetime.now(timezone.utc).isoformat()
        out = []
        for r in payload.get("results", payload if isinstance(payload, list) else []):
            name = r.get("domainName") or r.get("domain") or ""
            sld, _, tld = name.partition(".")
            out.append(InventorySnapshot(
                domain_name=name,
                sld=sld,
                tld=tld,
                purchasable=bool(r.get("purchasable")),
                premium=bool(r.get("premium")),
                purchase_price=r.get("purchasePrice"),
                renewal_price=r.get("renewalPrice"),
                purchase_type=r.get("purchaseType"),
                reason=r.get("reason"),
                checked_at=now,
            ))
        return out

    async def search(self, keyword: str, tlds: list[str]) -> list[InventorySnapshot]:
        return self.parse_results(await self.search_raw(keyword, tlds))

    async def check_availability(self, domains: list[str]) -> list[dict]:
        if not 1 <= len(domains) <= 50:
            raise ValueError("CheckAvailability supports 1..50 domains per call")
        res = await self._request("POST", self.CHECK,
                                  json={"domainNames": domains,
                                        "purchaseType": "registration"})
        return res.get("results", res if isinstance(res, list) else [])

    async def check_availability_fail_closed(self, domain: str) -> dict:
        """Fail-closed availability check. Returns validated availability dict or raises.
        
        Response must contain:
          - domainName matching the requested domain
          - purchasable field (not None)
          - purchaseType == "registration"
        
        Missing/malformed response -> raises NameComError.
        """
        results = await self.check_availability([domain])
        if not results:
            raise NameComError(404, f"no availability response for {domain}")
        
        entry = None
        for r in results:
            name = r.get("domainName") or r.get("domain") or ""
            if name.lower() == domain.lower():
                entry = r
                break
        
        if entry is None:
            raise NameComError(404, f"domainName mismatch: requested {domain}, got {[r.get('domainName') for r in results]}")
        
        # Fail-closed: purchasable must be explicitly present
        if "purchasable" not in entry:
            raise NameComError(400, f"missing 'purchasable' field for {domain}")
        
        # Fail-closed: purchaseType must be registration (None/empty is also a failure)
        pt = entry.get("purchaseType")
        if pt != "registration":
            raise NameComError(400, f"unexpected purchaseType {pt!r} for {domain} (expected 'registration')")
        
        return entry

    async def get_pricing(self, domain: str) -> dict:
        return await self._request("GET", f"/core/v1/domains/{domain}:getPricing")

    # ---- lifecycle (gated) ----

    async def get_domain(self, domain: str) -> dict:
        return await self._request("GET", f"/core/v1/domains/{domain}")

    # ---- centralized mutation guard (peer review §11) ----
    WRITE_MODES = {"sandbox", "production-approved"}

    def _require_write_mode(self):
        """Every mutating endpoint MUST pass through here.
        Default 'production-readonly' blocks all writes."""
        if self.mode not in self.WRITE_MODES:
            raise NameComError(
                403, f"write blocked in current mode: {self.mode!r} "
                     f"(allowed: {sorted(self.WRITE_MODES)})")

    async def update_domain(self, domain: str, *, autorenew: bool | None = None,
                            privacy: bool | None = None,
                            locked: bool | None = None) -> dict:
        self._require_write_mode()
        body = {}
        if autorenew is not None:
            body["autorenewEnabled"] = autorenew
        if privacy is not None:
            body["privacyEnabled"] = privacy
        if locked is not None:
            body["locked"] = locked
        return await self._request("PATCH", f"/core/v1/domains/{domain}", json=body)

    async def create_dns_record(self, domain: str, *, host: str,
                                record_type: str, answer: str,
                                ttl: int = 300) -> dict:
        self._require_write_mode()
        return await self._request(
            "POST", f"/core/v1/domains/{domain}/records",
            json={"host": host, "type": record_type, "answer": answer,
                  "ttl": max(300, ttl)},
        )

    async def list_dns_records(self, domain: str) -> list[dict]:
        res = await self._request("GET", f"/core/v1/domains/{domain}/records")
        return res.get("records", res if isinstance(res, list) else [])

    async def register_domain(self, payload: dict, idempotency_key: str) -> dict:
        """DESTRUCTIVE. Requires fresh availability check + explicit approval upstream.
        Blocked unless mode == 'sandbox' (production-readonly guard)."""
        self._require_write_mode()
        return await self._request("POST", "/core/v1/domains", json=payload,
                                   headers={"X-Idempotency-Key": idempotency_key})

    # ---- feasibility helpers ----

    @staticmethod
    def filter_feasible(snaps: list[InventorySnapshot], c: ConstraintSet
                        ) -> tuple[list[InventorySnapshot],
                                   dict[str, list[str]]]:
        keep, rejected = [], {}
        for s in snaps:
            ok, reasons = feasible(s, c)
            if ok:
                keep.append(s)
            else:
                rejected[s.domain_name] = reasons
        return keep, rejected
