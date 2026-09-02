# DomainArena

**A/B testing for domain names in the agentic web.**

Measure which domains AI agents actually understand, then safely acquire and configure the winner with name.com.

> Human domain tools ask: "Does this name sound good?"
> DomainArena asks: "Does an AI agent infer the right product from this name with no context?"

Built on 16 experiments across 7+ model families studying how AI agents discover, evaluate, and select tools.

## Research foundation

Before building DomainArena, we ran a comprehensive research program answering: **do AI agents actually understand the tools and domains they encounter?**

Key findings:

| Finding | Status | Implication |
|---------|--------|-------------|
| Description seduction is family-clustered | ✅ CONFIRMED | Some models pick broken tools if the description sounds enterprise-y |
| Selection is contrast-driven, not content-driven | 📋 PROVISIONAL | Agents detect relative quality, not absolute quality |
| Serverless LLM inference is non-deterministic | ✅ CONFIRMED | Same prompt flips behavior across time windows |
| Position primacy dominates SERP choice | 📋 PROVISIONAL | 87% pick slot 0; TLD matters only within-slot |
| Tool name style has zero effect | 📋 PROVISIONAL | When descriptions are clear, name is noise |
| Decoy resistance varies by model | 📋 PROVISIONAL | ox-alpha-free resists 95.8% of adversarial descriptions |

**→ See [RESEARCH.md](RESEARCH.md) for the full research program.**

## The problem

Before an agent can use a service, it has to decide which service a domain represents. Nobody has measured whether agents actually understand domain names — until now. The domain name market sits at the intersection of linguistics, psychology, and commerce, but until recently relied on human intuition and small-sample heuristics ([DN.org, Jan 2026](https://dn.org/using-llms-to-score-brandability-at-scale/)). LLMs can now operationalize brand intuition, turning what was once artisanal judgment into a measurable, repeatable signal.

## What DomainArena measures

> Given a task description, which domain names do AI agents infer are relevant, which do they select, and does the hostname itself affect their choice?

This is the first benchmark that asks: "given only a domain name, can an AI model infer what service runs behind it?" The answer has implications for domain investors, registries, and anyone building agent-native products.

## How name.com is central

DomainArena uses **6 name.com API endpoints** in one workflow:

```text
INTENT
  ↓
name.com SEARCH          — discover candidate domains
  ↓
AGENT COMPREHENSION TEST — blind inference, no context
  ↓
EVIDENCE-BASED RANKING   — Wilson CI, cross-family
  ↓
name.com FRESH PRICE     — recheck availability + pricing
  ↓
HUMAN APPROVAL           — one-time token, approval-gated
  ↓
name.com REGISTER        — execute approved acquisition
  ↓
DNS CREATE + READ-BACK   — configure + verify
  ↓
VERIFIED RECEIPT          — sha256, append-only
```

| name.com capability | DomainArena use |
|---|---|
| Search | discover candidate domains |
| Availability | fail closed before purchase |
| Pricing | enforce purchase + renewal budgets |
| Registration | execute approved acquisition |
| DNS create | configure acquired domain |
| DNS read | verify configuration actually landed |

## Architecture — MCP is the interface

Every operation goes through MCP tools. The demo UI and HTTP API are frontends for the same `DomainService` — MCP is the agent-native interface.

```
    ┌─────────────────────────────────────────────────┐
    │                  MCP CLIENT                      │
    │         (Claude, GPT, Gemini, custom)            │
    └────────────────────┬────────────────────────────┘
                         │ JSON-RPC 2.0
    ┌────────────────────▼────────────────────────────┐
    │              DOMAIN ARENA MCP SERVER             │
    │                                                  │
    │  Tools:          Resources:                      │
    │  search_domain   domainarena://decisions         │
    │  recommend_domain domainarena://config           │
    │  compare_domains                                   │
    │  prepare_registration                             │
    │  approve_domain                                   │
    │  register_domain                                  │
    │  configure_dns                                    │
    └────────────────────┬────────────────────────────┘
                         │
    ┌────────────────────▼────────────────────────────┐
    │              DOMAIN SERVICE                      │
    │         (single source of truth)                 │
    │                                                  │
    │  State machine: 11 states, strict transitions    │
    │  Approval-gated registration                     │
    │  Price drift guard + hard budgets                │
    │  Immutable decision basis (hash-locked)          │
    └──┬─────────────┬─────────────┬──────────────────┘
       │             │             │
    name.com      Cloudflare    Pipeline
    Provider      Workers AI    (semantic inversion)
```

## The evidence model

DomainArena distinguishes three evidence statuses — never collapsing them:

| Status | Meaning | Example |
|---|---|---|
| `MEASURED` | Real measurement from experiment | DA-T3 pairwise selection result |
| `PROXY` | Heuristic approximation | Structural fluency (vowel ratio) |
| `NOT_MEASURED` | No data collected | DA-T6 execution trial (not yet run) |

Proxy evidence contributes at half weight (β=0.5). A recommendation can be `VALIDATED` only when measured coverage ≥ 70%. Proxies improve provisional rankings but cannot promote to scientifically validated status.

## Research grounding

### Semantic inversion (DN.org, Jan 2026)

The core insight: LLMs can decompose brandability into latent attributes — phonetics, memorability, cultural resonance — and produce structured judgments across dimensions that matter to buyers. DomainArena implements this as blind name-only inference: the model sees only the domain, infers the product, and a hidden scorer compares against the frozen intent.

### Pairwise selection (this work)

Following the finding that "humans are better at relative judgment than absolute rating, and LLMs appear to mirror this behavior," DomainArena's DA-T3 experiment uses AB/BA position-randomized pairwise comparison with Wilson score intervals. This is statistically more powerful than single-name scoring.

### Cross-family replication

Per the canonical experiment principles, findings must replicate across ≥2 model families. DomainArena runs semantic inversion across Llama 3.3, Mistral Small, and Qwen3 — if a causal effect only holds on one family, that's a boundary condition, not a law.

### Agent-native service discovery (AgentDNS, May 2025)

[AgentDNS](https://arxiv.org/abs/2505.22368) proposes a root domain naming system for LLM agent service discovery. DomainArena complements this by measuring whether agents can actually understand the domain names they discover.

## Safety and purchase approval

- **Fail-closed**: Missing/malformed availability → abort
- **Write guard**: Registration/DNS writes require `DOMAINARENA_ALLOW_WRITES=1`
- **Approval required**: Registration needs explicit human approval (one-time token)
- **Price drift guard**: Price changes beyond threshold invalidate approval
- **Hard budgets**: `max_purchase_price` and `max_renewal_price` enforced at registration
- **Idempotent**: Duplicate registration attempts can't double-charge
- **purchaseType=registration**: Enforced on every availability check
- **Token hashing**: Approval token hash stored on disk, raw token returned once

## Environment variables

```bash
NAMECOM_USERNAME=          # name.com API username
NAMECOM_TOKEN=             # name.com API token
NAMECOM_MODE=sandbox       # sandbox or production-approved
CLOUDFLARE_ACCOUNT_ID=     # for semantic inference
CLOUDFLARE_API_TOKEN=      # for semantic inference
DOMAINARENA_ALLOW_WRITES=0 # 0=rehearsal, 1=live registration
```

## MCP demo transcript

See [docs/MCP_DEMO_TRANSCRIPT.md](docs/MCP_DEMO_TRANSCRIPT.md) for a complete session showing an agent using MCP tools to select, approve, and register a domain.

## Quickstart

```bash
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Fixture mode (no credentials needed)
python3 -m domainarena.web.demo   # http://127.0.0.1:8777

# Live mode (requires name.com credentials)
cp .env.example .env       # add name.com + Cloudflare credentials
DOMAINARENA_ALLOW_WRITES=1 python3 -m domainarena.web.demo

# MCP server (for AI agents)
python3 -m domainarena.api.mcp     # stdin/stdout JSON-RPC

# Pairwise experiment
python3 -m experiments.pairwise_selection \
  --intent "A JSON repair tool" \
  --domain-a "jsonrepair.dev" \
  --domain-b "fixjson.com" \
  --trials 20
```

## Tests

```bash
pytest tests/ -v    # 148 tests passing
```

### Full lifecycle verified

The complete name.com lifecycle is tested end-to-end:

```text
[PASS] search              — find candidate domains
[PASS] fresh availability  — fail-closed before purchase
[PASS] pricing             — enforce budget constraints
[PASS] approval gate       — human approval required
[PASS] registration        — execute acquisition
[PASS] DNS create          — configure domain
[PASS] DNS readback        — verify configuration landed
[PASS] receipt hash        — content-addressed evidence
```

```python
# From test_lifecycle_e2e.py — the full flow
recommend → prepare → approve → register → configure_dns → verified receipt
```

### Before/after: why this matters

```text
HUMAN HEURISTIC
  "jsonultra.xyz sounds cool"
  → Agent thinks: "fantasy role-playing game"
  → WRONG

AGENT-TESTED
  "fixjson.com"
  → Agent thinks: "utility for repairing malformed JSON"
  → CORRECT → acquired via name.com
```

### Test coverage

- `test_world.py` — DomainArenaWorld state transitions, terminal conditions, scoring
- `test_lifecycle_e2e.py` — Full recommend → approve → prepare → register → DNS flow + persistence roundtrip
- `test_namecom.py` — name.com client (mock + integration)
- `test_policy_api.py` — Optimizer policy, Pareto front, HTTP API
- `test_additional.py` — Demo smoke, MCP approval bypass, business audience, provenance
- `test_pairwise.py` — Pairwise experiment runner (choice extraction, Wilson CI, prompt generation)

## What's built vs what's next

| Component | Status | Evidence dimension |
|---|---|---|
| Live name.com search | ✅ Built | — |
| MCP server (9 tools + 2 resources) | ✅ Built | — |
| Approval-gated registration | ✅ Built | — |
| Price drift guard | ✅ Built | — |
| Structural fluency heuristic | ✅ Built | `PROXY` |
| Semantic inversion (blind) | ✅ Built | `PROXY` |
| Pairwise AB/BA experiment | ✅ Built | `MEASURED` (when run with credentials) |
| Cross-family replication | ✅ Built | `MEASURED` (when run with credentials) |
| Execution-grounded selection | 🔬 Prototype | `NOT_MEASURED` (DA-T6 pending) |
| Bradley-Terry aggregation | 📋 Planned | Requires ≥3 candidates |
| Real-world outcome tracking | 📋 Planned | Requires market data |

## Limitations

- Requires name.com API credentials for live inventory
- Requires Cloudflare Workers AI for semantic comprehension
- Registration only in sandbox mode (production requires explicit approval)
- Structural fluency is a PROXY, not a measurement — real brandability scoring requires DA-T3/DA-T6 experiments
- Demo in fixture mode uses seed candidates, not live search

## License

MIT
