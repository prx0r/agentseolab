"""DomainArena MCP server (stdio JSON-RPC).

Tools:
- recommend_domain(intent, audience, constraints) — read-only
- compare_domains(a, b) — pairwise evidence summary
Registration is intentionally NOT exposed as an agent tool without an
approval gate; use the HTTP API approve → recheck-and-register flow.
"""
from __future__ import annotations
import json
import sys

from ..api.http import RecommendRequest, _demo_candidates
from ..optimizer import recommend

TOOLS = [
    {
        "name": "recommend_domain",
        "description": ("Given a product intent, target audience and hard budget "
                        "constraints, return the best purchasable domain with evidence."),
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
]


def _handle(method: str, params: dict) -> dict:
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "recommend_domain":
            req = RecommendRequest(
                description=args["description"],
                primary_job=args["primary_job"],
                audience=args.get("audience", "ai_agent"),
                constraints={
                    "max_purchase_price": args.get("max_purchase_price"),
                    "max_renewal_price": args.get("max_renewal_price"),
                },
            )
            cands = _demo_candidates(req)
            if not cands:
                return {"content": [{"type": "text",
                                     "text": "No feasible candidates under constraints."}]}
            rec = recommend(cands, req.audience)
            return {"content": [{"type": "text", "text": json.dumps({
                "domain": rec.domain_name,
                "score": round(rec.score, 4),
                "on_pareto_front": rec.on_pareto,
                "explanation": rec.explanation,
                "note": "registration requires explicit approval via HTTP API",
            }, indent=2)}]}
        if name == "compare_domains":
            cands = _demo_candidates(RecommendRequest(
                description="x", primary_job="x"))
            scores = {c.domain_name: round(rec.score, 4)
                      for (c, _), rec in
                      ((pair, recommend([pair], args.get("audience", "ai_agent")))
                       for pair in cands
                       if c.domain_name in [d.lower() for d in args.get("domains", [])])}
            return {"content": [{"type": "text", "text": json.dumps(scores, indent=2)}]}
        raise ValueError(f"unknown tool {name}")
    raise ValueError(f"unsupported method {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            result = _handle(msg.get("method", ""), msg.get("params") or {})
            resp = {"jsonrpc": "2.0", "id": msg.get("id"), "result": result}
        except Exception as e:  # noqa: BLE001
            resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                    "error": {"code": -32603, "message": str(e)}}
        print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
