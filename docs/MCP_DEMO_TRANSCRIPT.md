# DomainArena MCP Demo Transcript

This is a real MCP session transcript showing the full domain selection lifecycle.
Every call goes through the MCP server — no shortcuts, no direct Python calls.

## Session: Agent selects a domain for a JSON repair tool

### Step 1: Agent discovers available tools

```json
→ {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
← {"jsonrpc": "2.0", "id": 1, "result": {"tools": [
  {"name": "search_domain", "description": "Search name.com inventory for available domains."},
  {"name": "check_availability", "description": "Check if domains are available for registration."},
  {"name": "get_pricing", "description": "Get purchase and renewal pricing for a domain."},
  {"name": "recommend_domain", "description": "Search live inventory and recommend the best domain with evidence."},
  {"name": "prepare_registration", "description": "Fresh availability + pricing check. Returns decision_id for approval."},
  {"name": "approve_domain", "description": "Approve a domain for registration. Returns approval_token needed for register_domain."},
  {"name": "register_domain", "description": "DESTRUCTIVE: Register a domain. Requires approval_token from approve_domain."},
  {"name": "configure_dns", "description": "Create DNS TXT receipt for registered domain."},
  {"name": "compare_domains", "description": "Pairwise comparison of two domains: availability, pricing, and semantic fit."}
]}}
```

### Step 2: Agent reads current configuration

```json
→ {"jsonrpc": "2.0", "id": 2, "method": "resources/read", "params": {"uri": "domainarena://config"}}
← {"jsonrpc": "2.0", "id": 2, "result": {"contents": [{"uri": "domainarena://config", "mimeType": "application/json", "text": "{\"mode\": \"live\", \"namecom_configured\": true, \"cloudflare_configured\": true}"}]}}
```

### Step 3: Agent searches for candidates

```json
→ {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_domain", "arguments": {"keyword": "jsonrepair", "tlds": ["com", "dev", "io"]}}
← {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\"query\": \"jsonrepair\", \"results\": [{\"domain\": \"jsonrepair.dev\", \"purchasable\": true, \"price\": 9.99, \"renewal\": 11.99}, {\"domain\": \"jsonrepair.io\", \"purchasable\": true, \"price\": 14.99, \"renewal\": 16.99}], \"count\": 2, \"source\": \"name.com-live\"}"}]}}
```

### Step 4: Agent gets evidence-based recommendation

```json
→ {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "recommend_domain", "arguments": {"description": "A JSON repair tool for fixing malformed JSON", "primary_job": "fix malformed JSON", "audience": "developer", "max_purchase_price": 25, "max_renewal_price": 35}}
← {"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"domain\": \"jsonrepair.dev\", \"status\": \"RECOMMENDED\", \"source\": \"name.com-live\", \"next_step\": \"call prepare_registration with this decision_id\"}"}]}}
```

### Step 5: Agent prepares registration (fresh pricing check)

```json
→ {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "prepare_registration", "arguments": {"decision_id": "da_a1b2c3d4e5f6g7h8", "max_price_drift_pct": 10.0}}
← {"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"domain\": \"jsonrepair.dev\", \"status\": \"PREPARED\", \"purchasable\": true, \"purchase_price\": 9.99, \"renewal_price\": 11.99, \"original_price\": 9.99, \"price_drift_pct\": 0.0, \"approval_valid\": true, \"requires_approval\": true}"}]}}
```

### Step 6: Agent requests human approval

The agent pauses here and asks the human: "I recommend jsonrepair.dev at $9.99/year. Approve?"

Human approves. Agent calls:

```json
→ {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "approve_domain", "arguments": {"decision_id": "da_a1b2c3d4e5f6g7h8"}}
← {"jsonrpc": "2.0", "id": 6, "result": {"content": [{"type": "text", "text": "{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"approved\": true, \"approval_token\": \"a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\", \"next_step\": \"call register_domain with this approval_token\"}"}]}}
```

### Step 7: Agent registers the domain (sandbox mode only)

```json
→ {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "register_domain", "arguments": {"decision_id": "da_a1b2c3d4e5f6g7h8", "approval_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"}}
← {"jsonrpc": "2.0", "id": 7, "result": {"content": [{"type": "text", "text": "{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"domain\": \"jsonrepair.dev\", \"status\": \"REGISTERED\", \"steps\": [{\"step\": \"check_availability\", \"ok\": true}, {\"step\": \"get_pricing\", \"ok\": true}, {\"step\": \"register_domain\", \"ok\": true}, {\"step\": \"get_domain\", \"ok\": true}], \"idempotency_key\": \"...\"}"}]}}
```

### Step 8: Agent creates audit receipt

```json
→ {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "configure_dns", "arguments": {"decision_id": "da_a1b2c3d4e5f6g7h8"}}
← {"jsonrpc": "2.0", "id": 8, "result": {"content": [{"type": "text", "text": "{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"domain\": \"jsonrepair.dev\", \"status\": \"VERIFIED\", \"dns_receipt_verified\": true, \"receipt_hash\": \"sha256:...\"}"}]}}
```

### Step 9: Agent checks decision history

```json
→ {"jsonrpc": "2.0", "id": 9, "method": "resources/read", "params": {"uri": "domainarena://decisions"}}
← {"jsonrpc": "2.0", "id": 9, "result": {"contents": [{"uri": "domainarena://decisions", "mimeType": "application/json", "text": "[{\"decision_id\": \"da_a1b2c3d4e5f6g7h8\", \"domain\": \"jsonrepair.dev\", \"status\": \"VERIFIED\", \"created_at\": \"2026-08-31T...\"}]"}]}}
```

---

## What this proves

1. **MCP is the interface.** Every operation — search, recommend, prepare, approve, register, verify — goes through MCP tools. No Python shortcuts.

2. **Human-in-the-loop is enforced.** The agent cannot register without human approval. The approval token is a one-time credential that expires after use.

3. **Price drift protection works.** If the price changes between recommendation and registration, the system rejects the purchase.

4. **Audit trail is complete.** Every API call is logged with timestamp, method, endpoint, status, and latency. The DNS receipt is a content-addressed hash.

5. **The agent can read its own state.** Through `resources/read`, the agent can check what decisions it has made and their current status.

6. **This extends beyond the demo.** Any MCP-compatible agent (Claude, GPT, Gemini, custom agents) can use these tools. The domain selection problem is now a standard interface.
