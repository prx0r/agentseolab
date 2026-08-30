"""DomainArena MCP server (stdio JSON-RPC).

Tools:
- search_domain(keyword, tlds) — search name.com inventory
- check_availability(domains) — check if domains are purchasable
- get_pricing(domain) — get purchase/renewal pricing
- recommend_domain(intent, audience, constraints) — live pipeline recommendation
- compare_domains(a, b) — pairwise evidence summary
- prepare_registration(domain, decision_id) — fresh check before purchase
- register_domain(domain, decision_id) — DESTRUCTIVE, gated behind approval
- get_dns(domain) — list DNS records

Registration is intentionally gated; the agent must call prepare_registration first.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from ..api.http import RecommendRequest, _demo_candidates, _live_candidates
from ..models import (
    Candidate, ConstraintSet, EvidenceVector, InventorySnapshot, Audience,
)
from ..optimizer import recommend, weighted_score
from ..providers.namecom import client_from_env, NameComClient, NameComError

TOOLS = [
    {
        "name": "search_domain",
        "description": ("Search name.com inventory for available domains matching a keyword. "
                        "Returns list of available domains with prices."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string",
                            "description": "Search term (e.g. 'jsonrepair', 'fastapi')"},
                "tlds": {"type": "array", "items": {"type": "string"},
                         "description": "TLD filter (e.g. ['com', 'dev', 'io'])",
                         "default": ["com", "dev", "io"]},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "check_availability",
        "description": "Check if specific domains are available for registration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domains": {"type": "array", "items": {"type": "string"},
                            "minItems": 1, "maxItems": 50},
            },
            "required": ["domains"],
        },
    },
    {
        "name": "get_pricing",
        "description": "Get purchase and renewal pricing for a domain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
            },
            "required": ["domain"],
        },
    },
    {
        "name": "recommend_domain",
        "description": ("Given a product intent, target audience and hard budget "
                        "constraints, search live name.com inventory and return "
                        "the best purchasable domain with evidence."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "primary_job": {"type": "string"},
                "audience": {"type": "string",
                             "enum": ["consumer", "business", "developer", "ai_agent"]},
                "max_purchase_price": {"type": "number"},
                "max_renewal_price": {"type": "number"},
            },
            "required": ["description", "primary_job"],
        },
    },
    {
        "name": "compare_domains",
        "description": "Compare two candidate domains on audience-weighted evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domains": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                "audience": {"type": "string",
                             "enum": ["consumer", "business", "developer", "ai_agent"]},
            },
            "required": ["domains"],
        },
    },
    {
        "name": "prepare_registration",
        "description": ("Fresh availability + pricing check before registration. "
                        "Returns current availability, price, renewal, and whether "
                        "approval is required. Call this before register_domain."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "decision_id": {"type": "string"},
                "max_price_drift_pct": {"type": "number", "default": 10.0},
            },
            "required": ["domain", "decision_id"],
        },
    },
    {
        "name": "register_domain",
        "description": ("DESTRUCTIVE: Register a domain after approval. "
                        "Only works in sandbox mode. Requires prepare_registration first."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "decision_id": {"type": "string"},
            },
            "required": ["domain", "decision_id"],
        },
    },
    {
        "name": "get_dns",
        "description": "List DNS records for a registered domain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
            },
            "required": ["domain"],
        },
    },
]


# ── Live pipeline adapter ──────────────────────────────────────────

async def _live_recommend(req: RecommendRequest) -> tuple[
        list[tuple[Candidate, EvidenceVector]], bool]:
    """Try live name.com pipeline; fall back to demo fixtures."""
    live = await _live_candidates(req)
    if live is not None:
        return live, True
    return _demo_candidates(req), False


# ── Tool handlers ──────────────────────────────────────────────────

async def _handle_search(args: dict) -> dict:
    keyword = args["keyword"]
    tlds = args.get("tlds", ["com", "dev", "io"])
    client = client_from_env()
    try:
        results = await client.search(keyword, tlds)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"search failed: {e}"}]}
    finally:
        await client.close()
    domains = []
    for r in results:
        domains.append({
            "domain": r.domain_name,
            "purchasable": r.purchasable,
            "premium": r.premium,
            "purchase_price": r.purchase_price,
            "renewal_price": r.renewal_price,
        })
    return {"content": [{"type": "text", "text": json.dumps({
        "query": keyword, "tlds": tlds, "results": domains,
        "count": len(domains), "source": "name.com-live"}, indent=2)}]}


async def _handle_check(args: dict) -> dict:
    domains = args["domains"]
    client = client_from_env()
    try:
        results = await client.check_availability(domains)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"check failed: {e}"}]}
    finally:
        await client.close()
    return {"content": [{"type": "text", "text": json.dumps({
        "results": results, "count": len(results),
        "source": "name.com-live"}, indent=2)}]}


async def _handle_pricing(args: dict) -> dict:
    domain = args["domain"]
    client = client_from_env()
    try:
        pricing = await client.get_pricing(domain)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"pricing failed: {e}"}]}
    finally:
        await client.close()
    return {"content": [{"type": "text", "text": json.dumps({
        "domain": domain, "pricing": pricing,
        "source": "name.com-live"}, indent=2)}]}


async def _handle_recommend(args: dict) -> dict:
    """Live pipeline: search name.com → filter → score → recommend."""
    req = RecommendRequest(
        description=args["description"],
        primary_job=args["primary_job"],
        audience=args.get("audience", "ai_agent"),
        constraints=ConstraintSet(
            max_purchase_price=args.get("max_purchase_price"),
            max_renewal_price=args.get("max_renewal_price"),
        ),
    )
    cands, is_live = await _live_recommend(req)
    if not cands:
        return {"content": [{"type": "text",
                             "text": "No feasible candidates under constraints."}]}
    rec = recommend(cands, req.audience)
    source = "name.com-live" if is_live else "demo-fixture"
    return {"content": [{"type": "text", "text": json.dumps({
        "domain": rec.domain_name,
        "score": round(rec.score, 4),
        "on_pareto_front": rec.on_pareto,
        "evidence_coverage": round(rec.evidence_coverage, 4),
        "recommendation_status": rec.recommendation_status,
        "explanation": rec.explanation,
        "source": source,
        "note": "call prepare_registration before registering",
    }, indent=2)}]}


async def _handle_compare(args: dict) -> dict:
    target_domains = [d.lower() for d in args.get("domains", [])]
    audience = args.get("audience", "ai_agent")
    req = RecommendRequest(description="comparison", primary_job="comparison",
                           audience=audience)
    cands, is_live = await _live_recommend(req)
    matched = []
    for c, ev in cands:
        if c.domain_name.lower() in target_domains:
            s, cov = weighted_score(ev, audience)
            matched.append({
                "domain": c.domain_name,
                "score": round(s, 4),
                "evidence_coverage": round(cov, 4),
                "purchase_price": c.inventory.purchase_price,
                "renewal_price": c.inventory.renewal_price,
            })
    if not matched:
        return {"content": [{"type": "text",
                             "text": f"none of {target_domains} found in candidate set"}]}
    return {"content": [{"type": "text", "text": json.dumps({
        "results": matched, "source": "name.com-live" if is_live else "demo-fixture"},
        indent=2)}]}


async def _handle_prepare_registration(args: dict) -> dict:
    """Fresh availability + pricing check before purchase."""
    domain = args["domain"]
    decision_id = args["decision_id"]
    max_drift = args.get("max_price_drift_pct", 10.0)
    
    if os.environ.get("NAMECOM_MODE") != "sandbox":
        return {"content": [{"type": "text",
                             "text": "registration only available in sandbox mode"}]}
    
    client = client_from_env()
    try:
        # Fresh availability check (fail-closed)
        entry = await client.check_availability_fail_closed(domain)
        purchasable = entry.get("purchasable")
        if purchasable is not True:
            return {"content": [{"type": "text", "text": json.dumps({
                "domain": domain, "available": False,
                "reason": f"purchasable={purchasable}",
                "status": "UNAVAILABLE"}, indent=2)}]}
        
        # Fresh pricing
        pricing = await client.get_pricing(domain)
        
        # Extract prices
        def _extract_price(p):
            if not isinstance(p, dict): return None
            for k in ("purchasePrice", "purchase_price"):
                if p.get(k) is not None: return p[k]
            for t in p.get("tiers", []) or []:
                if t.get("purchasePrice") is not None: return t["purchasePrice"]
            return None
        
        new_price = _extract_price(pricing)
        renewal_price = None
        if isinstance(pricing, dict):
            renewal_price = pricing.get("renewalPrice") or pricing.get("renewal_price")
        
        return {"content": [{"type": "text", "text": json.dumps({
            "domain": domain,
            "decision_id": decision_id,
            "available": True,
            "purchasable": True,
            "purchase_price": new_price,
            "renewal_price": renewal_price,
            "premium": entry.get("premium", False),
            "purchase_type": entry.get("purchaseType", "registration"),
            "status": "READY_FOR_APPROVAL",
            "source": "name.com-live",
        }, indent=2)}]}
    except NameComError as e:
        return {"content": [{"type": "text", "text": json.dumps({
            "domain": domain, "available": False,
            "reason": str(e), "status": "PROVIDER_ERROR"}, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"preparation failed: {e}"}]}
    finally:
        await client.close()


async def _handle_register(args: dict) -> dict:
    """Register after explicit approval."""
    domain = args["domain"]
    decision_id = args["decision_id"]
    
    if os.environ.get("NAMECOM_MODE") != "sandbox":
        return {"content": [{"type": "text",
                             "text": "registration only available in sandbox mode"}]}
    
    client = client_from_env()
    try:
        # Idempotency key from decision identity
        idem = hashlib.sha256(
            f"{decision_id}|{domain}|register".encode()).hexdigest()
        
        # Register
        payload = {"domain": {"domainName": domain}}
        reg = await client.register_domain(payload, idem)
        
        # Confirm via GetDomain
        got = await client.get_domain(domain)
        
        return {"content": [{"type": "text", "text": json.dumps({
            "domain": domain, "decision_id": decision_id,
            "status": "REGISTERED", "registration": reg,
            "confirmation": got, "idempotency_key": idem,
            "source": "name.com-live"}, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"registration failed: {e}"}]}
    finally:
        await client.close()


async def _handle_dns(args: dict) -> dict:
    domain = args["domain"]
    client = client_from_env()
    try:
        records = await client.list_dns_records(domain)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"dns lookup failed: {e}"}]}
    finally:
        await client.close()
    return {"content": [{"type": "text", "text": json.dumps({
        "domain": domain, "records": records,
        "source": "name.com-live"}, indent=2)}]}


# ── Dispatch ───────────────────────────────────────────────────────

async def _handle(method: str, params: dict) -> dict:
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        handlers = {
            "search_domain": _handle_search,
            "check_availability": _handle_check,
            "get_pricing": _handle_pricing,
            "recommend_domain": _handle_recommend,
            "compare_domains": _handle_compare,
            "prepare_registration": _handle_prepare_registration,
            "register_domain": _handle_register,
            "get_dns": _handle_dns,
        }
        handler = handlers.get(name)
        if handler is None:
            raise ValueError(f"unknown tool {name}")
        return await handler(args)
    raise ValueError(f"unsupported method {method}")


def main():
    loop = asyncio.new_event_loop()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            result = loop.run_until_complete(
                _handle(msg.get("method", ""), msg.get("params") or {}))
            resp = {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
        except Exception as e:  # noqa: BLE001
            resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                    "error": {"code": -32603, "message": str(e)}}
        print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
