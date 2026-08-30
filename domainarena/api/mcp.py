"""DomainArena MCP server — calls DomainService for all operations.

Registration is approval-gated: must call prepare_registration first,
then approve, then register with the approval token.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys

from ..service import get_service, DecisionStatus
from ..models import ConstraintSet
from ..providers.namecom import client_from_env, NameComError

TOOLS = [
    {
        "name": "search_domain",
        "description": "Search name.com inventory for available domains.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string"},
                "tlds": {"type": "array", "items": {"type": "string"},
                         "default": ["com", "dev", "io"]},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "check_availability",
        "description": "Check if domains are available for registration.",
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
            "properties": {"domain": {"type": "string"}},
            "required": ["domain"],
        },
    },
    {
        "name": "recommend_domain",
        "description": "Search live inventory and recommend the best domain with evidence.",
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
        "name": "prepare_registration",
        "description": "Fresh availability + pricing check. Returns decision_id for approval.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "max_price_drift_pct": {"type": "number", "default": 10.0},
            },
            "required": ["decision_id"],
        },
    },
    {
        "name": "approve_domain",
        "description": "Approve a domain for registration. Returns approval_token needed for register_domain.",
        "inputSchema": {
            "type": "object",
            "properties": {"decision_id": {"type": "string"}},
            "required": ["decision_id"],
        },
    },
    {
        "name": "register_domain",
        "description": "DESTRUCTIVE: Register a domain. Requires approval_token from approve_domain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision_id": {"type": "string"},
                "approval_token": {"type": "string"},
            },
            "required": ["decision_id", "approval_token"],
        },
    },
    {
        "name": "configure_dns",
        "description": "Create DNS TXT receipt for registered domain.",
        "inputSchema": {
            "type": "object",
            "properties": {"decision_id": {"type": "string"}},
            "required": ["decision_id"],
        },
    },
    {
        "name": "compare_domains",
        "description": "Pairwise comparison of two domains: availability, pricing, and semantic fit against an intent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_a": {"type": "string", "description": "First domain (e.g. jsonrepair.dev)"},
                "domain_b": {"type": "string", "description": "Second domain (e.g. fixjson.com)"},
                "description": {"type": "string", "description": "Product/service intent description"},
            },
            "required": ["domain_a", "domain_b", "description"],
        },
    },
]


async def _handle_search(args: dict) -> dict:
    client = client_from_env()
    try:
        results = await client.search(
            args["keyword"], args.get("tlds", ["com", "dev", "io"]))
        domains = [{"domain": r.domain_name, "purchasable": r.purchasable,
                     "price": r.purchase_price, "renewal": r.renewal_price}
                    for r in results]
        return {"content": [{"type": "text", "text": json.dumps({
            "query": args["keyword"], "results": domains,
            "count": len(domains), "source": "name.com-live"}, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"search failed: {e}"}]}
    finally:
        await client.close()


async def _handle_check(args: dict) -> dict:
    client = client_from_env()
    try:
        results = await client.check_availability(args["domains"])
        return {"content": [{"type": "text", "text": json.dumps({
            "results": results, "count": len(results),
            "source": "name.com-live"}, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"check failed: {e}"}]}
    finally:
        await client.close()


async def _handle_pricing(args: dict) -> dict:
    client = client_from_env()
    try:
        pricing = await client.get_pricing(args["domain"])
        return {"content": [{"type": "text", "text": json.dumps({
            "domain": args["domain"], "pricing": pricing,
            "source": "name.com-live"}, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"pricing failed: {e}"}]}
    finally:
        await client.close()


async def _handle_recommend(args: dict) -> dict:
    svc = get_service()
    try:
        constraints = ConstraintSet(
            max_purchase_price=args.get("max_purchase_price"),
            max_renewal_price=args.get("max_renewal_price"),
        )
        mode = "live" if os.environ.get("NAMECOM_USERNAME") else "fixture"
        ds, cands = await svc.recommend_async(
            description=args["description"],
            primary_job=args["primary_job"],
            audience=args.get("audience", "ai_agent"),
            constraints=constraints,
            mode=mode,
        )
        return {"content": [{"type": "text", "text": json.dumps({
            "decision_id": ds.decision_id,
            "domain": ds.recommended_domain,
            "status": ds.status.value,
            "source": "name.com-live" if mode == "live" else "fixture",
            "next_step": "call prepare_registration with this decision_id",
        }, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"recommendation failed: {e}"}]}


async def _handle_prepare(args: dict) -> dict:
    svc = get_service()
    try:
        result = await svc.prepare_registration_async(
            args["decision_id"],
            args.get("max_price_drift_pct", 10.0),
        )
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    except (KeyError, ValueError) as e:
        return {"content": [{"type": "text", "text": f"preparation failed: {e}"}]}


async def _handle_approve(args: dict) -> dict:
    svc = get_service()
    try:
        result = svc.approve(args["decision_id"])
        return {"content": [{"type": "text", "text": json.dumps({
            **result,
            "next_step": "call register_domain with this approval_token",
        }, indent=2)}]}
    except (KeyError, ValueError) as e:
        return {"content": [{"type": "text", "text": f"approval failed: {e}"}]}


async def _handle_register(args: dict) -> dict:
    """Register with approval token. Rejects if not prepared/approved."""
    svc = get_service()
    try:
        result = await svc.register_async(
            args["decision_id"],
            args["approval_token"],
        )
        return {"content": [{"type": "text", "text": json.dumps({
            **result,
            "next_step": "call configure_dns to create evidence receipt",
        }, indent=2)}]}
    except (KeyError, ValueError) as e:
        return {"content": [{"type": "text", "text": f"registration rejected: {e}"}]}
    except PermissionError as e:
        return {"content": [{"type": "text", "text": f"registration denied: {e}"}]}


async def _handle_dns(args: dict) -> dict:
    svc = get_service()
    try:
        result = await svc.configure_dns_async(args["decision_id"])
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    except (KeyError, ValueError) as e:
        return {"content": [{"type": "text", "text": f"dns configuration failed: {e}"}]}


async def _handle_compare(args: dict) -> dict:
    """Pairwise comparison: availability, pricing, and semantic fit."""
    domain_a = args["domain_a"]
    domain_b = args["domain_b"]
    description = args["description"]
    client = client_from_env()
    try:
        # Check availability for both
        check_results = await client.check_availability([domain_a, domain_b])
        avail = {}
        for r in check_results:
            name = r.get("domainName") or r.get("domain") or ""
            avail[name.lower()] = r

        # Get pricing for both
        pricing = {}
        for dom in [domain_a, domain_b]:
            try:
                p = await client.get_pricing(dom)
                pricing[dom] = {
                    "purchase": p.get("purchasePrice"),
                    "renewal": p.get("renewalPrice"),
                }
            except Exception:
                pricing[dom] = {"purchase": None, "renewal": None, "error": "pricing unavailable"}

        # Semantic comparison via offline heuristic
        from ..arena.semantic_inversion import score_inference, _tokenize
        intent_tokens = _tokenize(description)

        def _domain_score(domain: str) -> dict:
            sld = domain.split(".")[0]
            import re
            words = re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", sld.lower()))
            score = score_inference(description, " ".join(words), words)
            return {"inferred_concepts": words, "semantic_score": round(score, 3)}

        sem_a = _domain_score(domain_a)
        sem_b = _domain_score(domain_b)

        a_avail = avail.get(domain_a.lower(), {})
        b_avail = avail.get(domain_b.lower(), {})

        return {"content": [{"type": "text", "text": json.dumps({
            "comparison": {
                domain_a: {
                    "available": a_avail.get("purchasable"),
                    "pricing": pricing.get(domain_a),
                    "semantic": sem_a,
                },
                domain_b: {
                    "available": b_avail.get("purchasable"),
                    "pricing": pricing.get(domain_b),
                    "semantic": sem_b,
                },
            },
            "verdict": (
                f"{domain_a} scores {sem_a['semantic_score']:.1%} semantic fit, "
                f"{domain_b} scores {sem_b['semantic_score']:.1%} semantic fit"
            ),
            "source": "name.com-live+heuristic",
        }, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"comparison failed: {e}"}]}
    finally:
        await client.close()


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
            "prepare_registration": _handle_prepare,
            "approve_domain": _handle_approve,
            "register_domain": _handle_register,
            "configure_dns": _handle_dns,
            "compare_domains": _handle_compare,
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
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                    "error": {"code": -32603, "message": str(e)}}
        print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
