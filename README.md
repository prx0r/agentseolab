# DomainArena

**A/B testing for domain names in the agentic web.**

[![Hackathon](https://img.shields.io/badge/DevNetwork_API%2BCloud%2BAI_Hackathon-2026-blue)](https://api-cloud-ai-hackathon-2026.devpost.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-148_passing-brightgreen)](#tests)

> Human domain tools ask: "Does this name sound good?"
> DomainArena asks: "Does an AI agent infer the right product from this name with no context?"

**[Watch Demo](https://youtu.be/ucm5W9WwZaI)** | **[Try Live Demo](https://domainarena.prx0r.workers.dev)** | **[View Source](https://github.com/prx0r/domainarena)**

---

## Judge in 30 Seconds

**Sponsor API:** [name.com](https://name.com) — 6 API endpoints used in a single workflow: Search, Availability, Pricing, Registration, DNS Create, DNS Read.

**Core workflow:**
```
Task description (intent)
  → name.com SEARCH (discover candidates)
  → Agent comprehension test (blind inference, no context)
  → Evidence-based ranking (Wilson CI, cross-family)
  → name.com FRESH PRICE (recheck availability + pricing)
  → Human approval (one-time token, approval-gated)
  → name.com REGISTER (execute approved acquisition)
  → DNS CREATE + READ-BACK (configure + verify)
  → Verified receipt (sha256, append-only)
```

**The magic moment:** We measure which domain names AI agents actually understand — then safely acquire the winner. A domain that sounds good to humans might be meaningless to an agent. DomainArena finds the ones that work for both.

**Live demo:** `https://domainarena.prx0r.workers.dev` — interactive MCP-driven domain evaluation and acquisition pipeline.

**name.com integration depth:** 6 endpoints in one workflow. Not surface-level — Search discovers, Availability fails closed, Pricing enforces budgets, Registration executes, DNS configures, Read-back verifies.

---

## The Problem

Before an agent can use a service, it has to decide which service a domain represents. Nobody has measured whether agents actually understand domain names — until now. The domain name market sits at the intersection of linguistics, psychology, and commerce, but until recently relied on human intuition and small-sample heuristics ([DN.org, Jan 2026](https://dn.org/using-llms-to-score-brandability-at-scale/)). LLMs can now operationalize brand intuition, turning what was once artisanal judgment into a measurable, repeatable signal.

## What DomainArena Measures

> Given a task description, which domain names do AI agents infer are relevant, which do they select, and does the hostname itself affect their choice?

This is the first benchmark that asks: **"given only a domain name, can an AI model infer what service runs behind it?"**

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

---

## How name.com Is Central

DomainArena uses **6 name.com API endpoints** in one workflow:

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

| Status | Meaning | Weight |
|---|---|---|
| `MEASURED` | Real measurement from experiment | 1.0 |
| `PROXY` | Heuristic approximation | 0.5 |
| `NOT_MEASURED` | No data collected | — |

A recommendation can be `VALIDATED` only when **measured coverage ≥ 70%**.

---

## Quick Start

```bash
git clone https://github.com/prx0r/domainarena.git
cd domainarena
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
```

---

## Safety & Purchase Approval

| Guard | Description |
|---|---|
| Fail-closed | Missing/malformed availability → abort |
| Write guard | Registration/DNS writes require `DOMAINARENA_ALLOW_WRITES=1` |
| Approval required | Registration needs explicit human approval (one-time token) |
| Price drift guard | Price changes beyond threshold invalidate approval |
| Hard budgets | `max_purchase_price` and `max_renewal_price` enforced |
| Idempotent | Duplicate registration attempts can't double-charge |

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

---

## Tech Stack

- **Language:** Python 3
- **APIs:** name.com (6 endpoints), Cloudflare Workers AI
- **Protocol:** MCP (Model Context Protocol)
- **Statistics:** Wilson score intervals, pairwise AB/BA comparison
- **Testing:** pytest (148 tests)
- **Deployment:** Cloudflare Workers

---

## License

MIT

---

**DevNetwork API + Cloud + AI Hackathon 2026**
