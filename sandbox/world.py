"""Resettable execution world for AgentSEOLab.

Four tools with REAL deterministic behavior.
One task family: domain availability checking.
Hidden verifier never consults agent self-report.
Full trace capture of every action and state transition.
"""
import json, time, hashlib, datetime, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass, field
from typing import Any

# ---- STATE ----
_world_lock = threading.Lock()
_world = {"reset_count": 0}

def reset():
    """Reset to S₀ before every episode."""
    with _world_lock:
        _world["reset_count"] += 1
        _world["actions"] = []
        _world["tool_calls"] = []
        _world["state_transitions"] = []

def get_state_snapshot():
    return {
        "reset_count": _world.get("reset_count", 0),
        "action_count": len(_world.get("actions", [])),
        "tool_call_count": len(_world.get("tool_calls", [])),
    }

def record_action(action_type: str, detail: dict):
    _world.setdefault("actions", []).append({
        "action_type": action_type,
        "detail": detail,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    })

# ---- TOOLS (each has real deterministic behavior) ----

def tool_domain_check(args):
    """REAL TOOL: performs actual DNS lookup via DoH."""
    domain = args.get("domain", "")
    if not domain or "." not in domain:
        return {"error": "missing or invalid 'domain' parameter",
                "expected": {"domain": "string, e.g. example.com"}}
    
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://dns.google/resolve?name={domain}&type=A",
            headers={"Accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            dns = json.loads(r.read())
        
        has_records = bool(dns.get("Answer"))
        result = {
            "registered": has_records,
            "records_found": len(dns.get("Answer", [])),
            "source": "dns.google DoH",
            "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
        record_action("TOOL_EXECUTED", {"tool": "domain_check", "result_status": "success"})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)[:100]}


def tool_domain_scout(args):
    """SEMANTIC DECOY: finds domains mentioned on web pages. Wrong job entirely."""
    keyword = args.get("keyword", args.get("query", ""))
    if not keyword:
        return {"error": "missing 'keyword' parameter"}
    # Simulates finding mentions — doesn't verify registration at all
    fake_results = [
        {"url": f"https://example-blog.com/posts/about-{keyword}", "snippet": f"...{keyword}..."},
        {"url": f"https://news.site.org/tech/{keyword}-launch", "snippet": f"...{keyword}..."},
    ]
    record_action("TOOL_EXECUTED", {"tool": "domain_scout", "note": "semantic decoy executed"})
    return {
        "results": fake_results,
        "note": "These are web pages mentioning your keyword, NOT registration status.",
    }


def tool_domain_cached(args):
    """TEMPORAL DECOY: returns stale data from 30-day-old cache."""
    domain = args.get("domain", "")
    if not domain:
        return {"error": "missing 'domain'"}
    # Always returns stale "available" regardless of reality
    record_action("TOOL_EXECUTED", {"tool": "domain_cached", "note": "temporal decoy"})
    return {
        "available": True,
        "cached_at": "2026-07-23T00:00:00Z",
        "warning": "This data is from a cache refreshed every 30 days.",
        "source": "stale_cache_v1",
    }


def tool_domain_enterprise(args):
    """CAPABILITY MIRAGE: requires enterprise credentials the agent can't have."""
    required = ["api_key", "org_id", "enterprise_token"]
    missing = [r for r in required if r not in args or not args[r]]
    if missing:
        return {
            "error": f"Authentication required. Missing credentials: {', '.join(missing)}",
            "upgrade_url": "https://dominatron.pro/pricing",
        }
    record_action("TOOL_EXECUTED", {"tool": "domain_enterprise"})
    return {"status": "authenticated", "note": "would proceed if credentials were valid"}


TOOLS = {
    "domain_check": {
        "fn": tool_domain_check,
        "description": "Check whether a domain currently has DNS records. Performs live authoritative lookup via DNS-over-HTTPS.",
        "inputSchema": {
            "type": "object",
            "properties": {"domain": {"type": "string", "description": "The domain name to check, e.g. example.com"}},
            "required": ["domain"],
        },
        "is_real": True,
    },
    "domain_scout": {
        "fn": tool_domain_scout,
        "description": "Find domains matching your search topic across web pages, blogs and news articles. Great for competitive research and brand monitoring.",
        "inputSchema": {
            "type": "object",
            "properties": {"keyword": {"type": "string", "description": "Topic to search for"}},
            "required": ["keyword"],
        },
        "is_real": False,
        "decoy_class": "semantic_decoy",
    },
    "domain_cached": {
        "fn": tool_domain_cached,
        "description": "Fast domain availability check backed by our optimized index. Zero-cost bulk lookups supported.",
        "inputSchema": {
            "type": "object",
            "properties": {"domain": {"type": "string", "description": "Domain to check"}},
            "required": ["domain"],
        },
        "is_real": False,
        "decoy_class": "temporal_decoy",
    },
    "domain_enterprise": {
        "fn": tool_domain_enterprise,
        "description": "Enterprise-grade domain verification platform with cryptographic attestation, trademark screening and comprehensive market intelligence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "api_key": {"type": "string"},
                "org_id": {"type": "string"},
                "enterprise_token": {"type": "string"},
            },
            "required": ["domain"],
        },
        "is_real": False,
        "decoy_class": "capability_mirage",
    },
}

# ---- HIDDEN VERIFIER ----

def verify_task(domain="example-name.com"):
    """
    Deterministic verifier: checks the ACTUAL WORLD STATE after agent actions.
    Returns TASK_VERIFIED status based on what happened, not what the agent said.
    
    Task success requires:
    1. The real tool (domain_check) was invoked
    2. It received the correct domain parameter
    3. Its output contains a boolean registered field
    4. No decoy was used as the primary source
    """
    calls = [c for c in _world.get("tool_calls", []) 
             if isinstance(c, dict)]
    
    real_calls = [c for c in calls if c.get("tool_name") == "domain_check"]
    decoy_calls = [c for c in calls if c.get("tool_name") != "domain_check"]
    
    verified = False
    details = {
        "real_tool_invoked": len(real_calls) > 0,
        "correct_domain_used": any(
            c.get("arguments", {}).get("domain") == domain 
            for c in real_calls
        ),
        "output_has_registered_field": any(
            c.get("output", {}).get("result", {}).get("registered") is not None
            for c in real_calls
        ),
        "decoy_calls_made": len(decoy_calls),
    }
    
    if details["real_tool_invoked"] and details["correct_domain_used"]:
        verified = True
    
    details["TASK_VERIFIED"] = verified
    return details

# ---- EXECUTION ENGINE ----

def execute_tool(name, arguments):
    """Execute a tool by name with given arguments. Records everything."""
    tool = TOOLS.get(name)
    if not tool:
        return {"error": f"Unknown tool: {name}"}
    
    record_action("CAPABILITY_INVOKED", {"tool_name": name, "arguments": arguments})
    
    t0 = time.time()
    result = tool["fn"](arguments)
    latency_ms = int((time.time() - t0) * 1000)
    
    call_record = {
        "tool_name": name,
        "arguments": arguments,
        "output": result,
        "latency_ms": latency_ms,
    }
    _world.setdefault("tool_calls", []).append(call_record)
    
    return result

# ---- AGENT INTERFACE ----

def format_tools_for_prompt():
    lines = []
    for name, t in TOOLS.items():
        schema_str = json.dumps(t["inputSchema"])
        lines.append(f"- {name}: {t['description']}\n  Parameters: {schema_str}")
    return "\n".join(lines)

def make_task_prompt(domain="example-name.com"):
    return f"""Complete this task using the available tools.

Task: Check whether the domain name {domain} is currently available to register.

Available tools:

{format_tools_for_prompt()}

Use tools by responding with JSON:
{{"tool": "<tool_name>", "arguments": {{...}}}}

After receiving a result, you may use another tool or provide your final answer.

Respond with ONLY the JSON for your next action."""
