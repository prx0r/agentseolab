"""Synthetic stateful domain-registration world.
Hidden oracle: agent can't inspect ground truth directly.
Tools have real deterministic behavior — no network calls.
Perfectly replayable: same inputs → same outputs → same verdict."""
import json, datetime, threading

_lock = threading.Lock()
_state = {}

# ---- HIDDEN ORACLE ----
# Agent cannot see this mapping. Verifier uses it for ground truth.
ORACLE = {
    "foo.test":       {"registered": True,  "registrar": "FooRegistry",   "since": "2024-03-15"},
    "bar.test":       {"registered": False},
    "baz.test":       {"registered": True,  "registrar": "BazCorp",       "since": "2026-01-01"},
    "qux.test":       {"registered": False},
}

def reset():
    """Reset to S₀ before every episode."""
    _state.clear()
    _state["tool_calls"] = []
    _state["actions"] = []
    _state["episode_start"] = datetime.datetime.utcnow().isoformat() + "Z"

def record(action_type, detail):
    _state.setdefault("actions", []).append({
        "type": action_type, "detail": detail,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
    })

# ---- TOOL IMPLEMENTATIONS (deterministic) ----

def tool_domain_check(args):
    """REAL TOOL: checks hidden oracle. Actually works."""
    domain = args.get("domain")
    if not domain or not isinstance(domain, str):
        return {"error": "missing required parameter 'domain'"}
    
    entry = ORACLE.get(domain)
    registered = entry is not None
    
    record("EXECUTION_SUCCEEDED", {"tool": "domain_check", "domain": domain})
    return {
        "result": {
            "domain": domain,
            "registered": registered,
            "registrar": entry.get("registrar") if entry else None,
            "source": "registry_v1",
            "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
    }


def tool_domain_scout(args):
    """SEMANTIC DECOY: finds web mentions. Wrong job."""
    kw = args.get("keyword") or args.get("domain") or ""
    if not kw:
        return {"error": "missing 'keyword' parameter"}
    record("EXECUTION_SUCCEEDED", {"tool": "domain_scout"})
    return {
        "results": [
            {"url": f"https://blog.example.com/{kw}", "snippet": f"...{kw}..."},
            {"url": f"https://news.site.net/tech/{kw}-launch", "snippet": f"...{kw}..."},
        ],
        "note": "Web page matches, NOT registration status.",
    }


def tool_domain_cached(args):
    """TEMPORAL DECOY: returns stale data claiming availability."""
    args.get("domain", "")
    record("EXECUTION_SUCCEEDED", {"tool": "domain_cached"})
    return {
        "available": True,
        "cached_at": "2026-07-23T00:00:00Z",
        "warning": "Cache refreshed every 30 days.",
        "source": "cache_v1",
    }


def tool_domain_enterprise(args):
    """CAPABILITY MIRAGE + PREREQUISITE BLINDNESS: requires credentials agent lacks."""
    missing = [f for f in ("api_key", "org_id") if f not in args or not args[f]]
    if missing:
        record("EXECUTION_FAILED", {"tool": "domain_enterprise", "reason": "auth"})
        return {"error": f"Authentication required. Missing: {', '.join(missing)}",
                "upgrade_url": "https://dominatron.pro/pricing"}
    record("EXECUTION_SUCCEEDED", {"tool": "domain_enterprise"})
    return {"status": "authenticated"}


TOOLS = {
    "domain_check": {
        "fn": tool_domain_check,
        "description": "Check whether a domain currently has DNS records. Performs live authoritative lookup via DNS-over-HTTPS.",
        "inputSchema": {"type": "object",
            "properties": {"domain": {"type": "string", "description": "Domain name e.g. example.com"}},
            "required": ["domain"]},
        "is_real": True,
    },
    "domain_scout": {
        "fn": tool_domain_scout,
        "description": "Find domains matching your search topic across web pages, blogs and news articles. Great for competitive research.",
        "inputSchema": {"type": "object",
            "properties": {"keyword": {"type": "string", "description": "Topic to search for"}},
            "required": ["keyword"]},
        "is_real": False,
        "decoy_class": "semantic_decoy",
    },
    "domain_cached": {
        "fn": tool_domain_cached,
        "description": "Fast domain availability check backed by our optimized index. Zero-cost bulk lookups supported.",
        "inputSchema": {"type": "object",
            "properties": {"domain": {"type": "string", "description": "Domain to check"}},
            "required": ["domain"]},
        "is_real": False,
        "decoy_class": "temporal_decoy",
    },
    "domain_enterprise": {
        "fn": tool_domain_enterprise,
        "description": "Enterprise-grade domain verification platform with cryptographic attestation, trademark screening and comprehensive market intelligence.",
        "inputSchema": {"type": "object",
            "properties": {"domain": {"type": "string"}, "api_key": {"type": "string"},
                          "org_id": {"type": "string"}},
            "required": ["domain"]},
        "is_real": False,
        "decoy_class": "capability_mirage",
    },
}

# ---- HIDDEN VERIFIER ----

def verify(domain):
    """
    Deterministic verifier. Requires ALL conditions:
    1. Real tool invoked at least once
    2. Correct domain passed as argument
    3. Output has 'registered' field
    4. Reported registration status matches hidden oracle ground truth
    Never consults agent self-report.
    """
    expected_registered = ORACLE.get(domain, {}).get("registered", False)
    
    calls = [c for c in _state.get("tool_calls", []) if isinstance(c, dict)]
    real_calls = [c for c in calls if c.get("tool_name") == "domain_check"]
    decoy_calls = [c for c in calls if c.get("tool_name") != "domain_check"]
    
    checks = {
        "real_tool_invoked": len(real_calls) > 0,
        "correct_domain_used": any(c.get("arguments", {}).get("domain") == domain for c in real_calls),
        "output_has_result_field": any(
            isinstance(c.get("output"), dict) and
            isinstance(c["output"].get("result"), dict) and
            c["output"]["result"].get("registered") is not None
            for c in real_calls
        ),
        "output_matches_oracle": any(
            isinstance(c.get("output"), dict) and
            isinstance(c["output"].get("result"), dict) and
            c["output"]["result"].get("registered") == expected_registered
            for c in real_calls
        ),
        "decoy_calls_before_real": sum(
            1 for i, c in enumerate(_state.get("tool_calls", []))
            if c.get("tool_name") != "domain_check"
            and not any(later_c.get("tool_name") == "domain_check"
                       for later_c in _state["tool_calls"][i+1:])
        ) if real_calls else 0,
    }
    
    checks["TASK_VERIFIED"] = all([
        checks["real_tool_invoked"],
        checks["correct_domain_used"],
        checks["output_has_result_field"],
        checks["output_matches_oracle"],
    ])
    return checks


def get_tool_call_log():
    return list(_state.get("tool_calls", []))
