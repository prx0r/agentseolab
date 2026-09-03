# DomainArena

**A/B testing for domain names in the agentic web.**

[![Hackathon](https://img.shields.io/badge/DevNetwork_API%2BCloud%2BAI_Hackathon-2026-blue)](https://api-cloud-ai-hackathon-2026.devpost.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-148_passing-brightgreen)](#tests)

> Human domain tools ask: "Does this name sound good?"
> DomainArena asks: "Does an AI agent infer the right product from this name with no context?"

**[Demo Video](DomainArena-Demo.mp4)** | **[Live Demo](http://127.0.0.1:8777)** | **[MCP Server](#mcp-server)**

---

## The Problem

Before an agent can use a service, it has to decide which service a domain represents. Nobody has measured whether agents actually understand domain names — until now.

The domain name market sits at the intersection of linguistics, psychology, and commerce, but until recently relied on human intuition and small-sample heuristics ([DN.org, Jan 2026](https://dn.org/using-llms-to-score-brandability-at-scale/)). LLMs can now operationalize brand intuition, turning what was once artisanal judgment into a measurable, repeatable signal.

## What DomainArena Measures

> Given a task description, which domain names do AI agents infer are relevant, which do they select, and does the hostname itself affect their choice?

This is the first benchmark that asks: **"given only a domain name, can an AI model infer what service runs behind it?"** The answer has implications for domain investors, registries, and anyone building agent-native products.

---

## Research Foundation

Built on **16 experiments** across **7+ model families** studying how AI agents discover, evaluate, and select tools.

| Finding | Status | Implication |
|---------|--------|-------------|
| Description seduction is family-clustered | Confirmed | Some models pick broken tools if the description sounds enterprise-y |
| Selection is contrast-driven, not content-driven | Provisional | Agents detect relative quality, not absolute quality |
| Serverless LLM inference is non-deterministic | Confirmed | Same prompt flips behavior across time windows |
| Position primacy dominates SERP choice | Provisional | 87% pick slot 0; TLD matters only within-slot |
| Tool name style has zero effect | Provisional | When descriptions are clear, name is noise |
| Decoy resistance varies by model | Provisional | ox-alpha-free resists 95.8% of adversarial descriptions |

---

## How name.com Is Central

DomainArena uses **6 name.com API endpoints** in one workflow:

```
INTENT
  ↓
name.com SEARCH           — discover candidate domains
  ↓
AGENT COMPREHENSION TEST  — blind inference, no context
  ↓
EVIDENCE-BASED RANKING    — Wilson CI, cross-family
  ↓
name.com FRESH PRICE      — recheck availability + pricing
  ↓
HUMAN APPROVAL            — one-time token, approval-gated
  ↓
name.com REGISTER         — execute approved acquisition
  ↓
DNS CREATE + READ-BACK    — configure + verify
  ↓
VERIFIED RECEIPT           — sha256, append-only
```

| name.com Capability | DomainArena Use |
|---|---|
| Search | Discover candidate domains |
| Availability | Fail closed before purchase |
| Pricing | Enforce purchase + renewal budgets |
| Registration | Execute approved acquisition |
| DNS create | Configure acquired domain |
| DNS read | Verify configuration actually landed |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP CLIENT                            │
│           (Claude, GPT, Gemini, custom)                 │
└────────────────────────┬────────────────────────────────┘
                         │ JSON-RPC 2.0
┌────────────────────────▼────────────────────────────────┐
│              DOMAIN ARENA MCP SERVER                     │
│                                                         │
│  Tools:              Resources:                         │
│  search_domain       domainarena://decisions            │
│  recommend_domain    domainarena://config               │
│  compare_domains                                        │
│  prepare_registration                                   │
│  approve_domain                                         │
│  register_domain                                        │
│  configure_dns                                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  DOMAIN SERVICE                          │
│             (single source of truth)                    │
│                                                         │
│  State machine: 11 states, strict transitions           │
│  Approval-gated registration                            │
│  Price drift guard + hard budgets                       │
│  Immutable decision basis (hash-locked)                 │
└──┬──────────────┬──────────────┬────────────────────────┘
   │              │              │
name.com      Cloudflare      Pipeline
Provider      Workers AI    (semantic inversion)
```

---

## Evidence Model

DomainArena distinguishes three evidence statuses — never collapsing them:

| Status | Meaning | Weight |
|---|---|---|
| `MEASURED` | Real measurement from experiment | 1.0 |
| `PROXY` | Heuristic approximation | 0.5 |
| `NOT_MEASURED` | No data collected | — |

A recommendation can be `VALIDATED` only when **measured coverage ≥ 70%**. Proxies improve provisional rankings but cannot promote to scientifically validated status.

---

## Quick Start

```bash
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

```bash
# Fixture mode (no credentials needed)
python3 -m domainarena.web.demo    # http://127.0.0.1:8777

# Live mode (requires name.com credentials)
cp .env.example .env
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

---

## Safety & Purchase Approval

| Guard | Description |
|---|---|
| Fail-closed | Missing/malformed availability → abort |
| Write guard | Registration/DNS writes require `DOMAINARENA_ALLOW_WRITES=1` |
| Approval required | Registration needs explicit human approval (one-time token) |
| Price drift guard | Price changes beyond threshold invalidate approval |
| Hard budgets | `max_purchase_price` and `max_renewal_price` enforced at registration |
| Idempotent | Duplicate registration attempts can't double-charge |
| Token hashing | Approval token hash stored on disk, raw token returned once |

---

## Tests

```bash
pytest tests/ -v    # 148 tests passing
```

### Full Lifecycle Verified

```
[PASS] search              — find candidate domains
[PASS] fresh availability  — fail-closed before purchase
[PASS] pricing             — enforce budget constraints
[PASS] approval gate       — human approval required
[PASS] registration        — execute acquisition
[PASS] DNS create          — configure domain
[PASS] DNS readback        — verify configuration landed
[PASS] receipt hash        — content-addressed evidence
```

### Before/After

```
HUMAN HEURISTIC
  "jsonultra.xyz sounds cool"
  → Agent thinks: "fantasy role-playing game"
  → WRONG

AGENT-TESTED
  "fixjson.com"
  → Agent thinks: "utility for repairing malformed JSON"
  → CORRECT → acquired via name.com
```

---

## What's Built

| Component | Status | Evidence Dimension |
|---|---|---|
| Live name.com search | Built | — |
| MCP server (9 tools + 2 resources) | Built | — |
| Approval-gated registration | Built | — |
| Price drift guard | Built | — |
| Structural fluency heuristic | Built | `PROXY` |
| Semantic inversion (blind) | Built | `PROXY` |
| Pairwise AB/BA experiment | Built | `MEASURED` |
| Cross-family replication | Built | `MEASURED` |
| Execution-grounded selection | Prototype | `NOT_MEASURED` |

---

## Tech Stack

- **Language:** Python 3
- **APIs:** name.com (6 endpoints), Cloudflare Workers AI
- **Protocol:** MCP (Model Context Protocol)
- **Statistics:** Wilson score intervals, pairwise AB/BA comparison
- **Testing:** pytest (148 tests)
- **Deployment:** Cloudflare Workers (optional)

---

## License

MIT

---

**DevNetwork API + Cloud + AI Hackathon 2026**
