# Devpost Submission — DomainArena

## Project name
DomainArena — MCP-native infrastructure for measuring domain name comprehension in AI agents

## One-line pitch
Not another AI name generator: DomainArena is the measurement layer that tests whether a domain actually causes agents to select your product, with approval-gated registration on name.com.

## The problem
Every builder — human or agent — picks domains by vibes. Existing tools generate hundreds of names and score them with arbitrary 0–10 "brandability" heuristics. Nobody measures whether a domain *works*: does an autonomous agent given a task pick your service? The domain name market sits at the intersection of linguistics, psychology, and commerce, but until recently relied on human intuition ([DN.org, Jan 2026](https://dn.org/using-llms-to-score-brandability-at-scale/)).

## What we built

### The MCP interface (the centerpiece)

Every operation goes through MCP tools — no shortcuts:

| MCP Tool | What it does |
|---|---|
| `search_domain` | Live name.com inventory search |
| `recommend_domain` | Full pipeline: intent → search → feasibility → evidence → recommendation |
| `compare_domains` | Pairwise availability + pricing + semantic fit |
| `prepare_registration` | Fresh availability + pricing check (fail-closed) |
| `approve_domain` | Human-in-the-loop approval (one-time token) |
| `register_domain` | Idempotent registration (requires approval token) |
| `configure_dns` | DNS TXT evidence receipt (write + read-back verification) |

Plus MCP resources: `domainarena://decisions` (decision history) and `domainarena://config` (service configuration).

### The evidence model

Three evidence statuses — never collapsing them:

| Status | Weight | Example |
|---|---|---|
| `MEASURED` | 1.0 | DA-T3 pairwise selection result |
| `PROXY` | 0.5 | Structural fluency heuristic |
| `NOT_MEASURED` | — | DA-T6 execution trial (not yet run) |

A recommendation can be `VALIDATED` only when measured coverage ≥ 70%. Proxies improve provisional rankings but cannot promote to scientifically validated status.

### The safety model

- **Fail-closed**: Missing/malformed availability → abort
- **Approval required**: Registration needs explicit human approval (one-time token, hash stored on disk)
- **Price drift guard**: Price changes beyond threshold invalidate approval
- **Hard budgets**: `max_purchase_price` and `max_renewal_price` enforced at registration
- **Idempotent**: Duplicate registration attempts can't double-charge
- **purchaseType=registration**: Enforced on every availability check

## name.com API integration depth (6 endpoints)

| Endpoint | MCP Tool | Purpose |
|---|---|---|
| `POST /core/v1/domains:search` | `search_domain` | Inventory IS the optimization space |
| `POST /core/v1/domains:checkAvailability` | `check_availability` | Fresh check before purchase |
| `GET /core/v1/domains/{domain}:getPricing` | `get_pricing` | Price verification |
| `POST /core/v1/domains` | `register_domain` | Approval-gated, idempotent registration |
| `POST /core/v1/domains/{domain}/records` | `configure_dns` | DNS evidence receipt |
| `GET /core/v1/domains/{domain}/records` | `configure_dns` | Verify configuration |

## What's built and verified

| Component | Status | Evidence dimension |
|---|---|---|
| Live name.com search | ✅ Built | — |
| MCP server (9 tools + 2 resources) | ✅ Built | — |
| Approval-gated registration | ✅ Built | — |
| Price drift guard + hard budgets | ✅ Built | — |
| Structural fluency heuristic | ✅ Built | `PROXY` |
| Semantic inversion (blind, cross-family) | ✅ Built | `PROXY` |
| Pairwise AB/BA experiment (Wilson CI) | ✅ Built | `MEASURED` (when run) |
| Cross-family replication (3 families) | ✅ Built | `MEASURED` (when run) |
| 148 tests passing | ✅ Verified | — |

## Research grounding

- **Semantic inversion** (DN.org, Jan 2026): LLMs can decompose brandability into latent attributes. DomainArena implements blind name-only inference with hidden scorer separation.
- **Pairwise selection** (this work): AB/BA position-randomized comparison with Wilson score intervals, following the finding that "LLMs mirror human relative judgment behavior."
- **Cross-family replication**: Per canonical experiment principles, findings must replicate across ≥2 model families (Llama 3.3 + Mistral Small + Qwen3).
- **Agent-native service discovery** (AgentDNS, arxiv May 2025): Complements DomainArena's measurement of whether agents understand the domains they discover.

## Real-world viability

`recommend_domain(intent, audience, constraints)` is the missing recommendation layer for every AI app-builder (Lovable/Railway/Replit-class) that embeds domain purchase. Every successful recommendation converts directly into a name.com registration. The MCP interface means any MCP-compatible agent can use this.

## How to run

### Quickstart (fixture mode, no API keys needed)
```bash
pip install -e ".[dev]"
python -m domainarena.web.demo  # hackathon demo on http://127.0.0.1:8777
pytest tests/ -v                # 148 tests
```

### Live mode (requires name.com + Cloudflare credentials)
```bash
cp .env.example .env
# Fill in NAMECOM_USERNAME, NAMECOM_TOKEN, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN
export DOMAINARENA_MODE=live
python -m domainarena.web.demo
```

### MCP server (for AI agents)
```bash
python -m domainarena.api.mcp   # stdio JSON-RPC
```

### Pairwise experiment
```bash
python -m experiments.pairwise_selection \
  --intent "A JSON repair tool" \
  --domain-a "jsonrepair.dev" \
  --domain-b "fixjson.com" \
  --trials 20
```

## Tech stack
- Python 3.11+, FastAPI, httpx, Pydantic v2
- name.com API (6 endpoints: search, check, pricing, register, DNS write, DNS verify)
- Cloudflare Workers AI (semantic inversion across Llama 3.3, Mistral Small, Qwen3)
- MCP protocol (9 tools + 2 resources for AI agent integration)
- GitHub Actions CI (Python 3.11 + 3.12)

## What we'd do next
- Deploy as a hosted service (Docker ready)
- Add real execution-grounded agent trials (DA-T6) — agents choose AND invoke, hidden verifier confirms outcome
- Bradley-Terry pairwise arena with position-bias correction (requires ≥3 candidates)
- Integration with Lovable/Railway for embedded domain purchase
- Real-world outcome tracking (registration → deployment → traffic)

## Repos & lineage
Public repo: https://github.com/prx0r/agentseolab (history preserved from AgentSEOLab lab; baseline tag `pre-domainarena-hackathon-2026-08-24`; source ledger for all third-party references).
