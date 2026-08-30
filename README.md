# DomainArena

**A/B testing for domain names in the agentic web.**

DomainArena measures which domain names AI agents actually understand and select, then safely registers the winner through name.com.

```
                  ┌─────────────────────┐
                  │   PRODUCT INTENT    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ name.com SEARCH API │
                  │  live inventory     │
                  └──────────┬──────────┘
                             │
                    hard constraints
                             │
                             ▼
              ┌─────────────────────────────┐
              │        DOMAIN ARENA         │
              │  semantic comprehension     │
              │  randomized pairwise choice │
              │  task success               │
              │  cross-model robustness     │
              └─────────────┬───────────────┘
                            │
                            ▼
                    RECOMMENDATION
                            │
                            ▼
                   CheckAvailability
                            │
                       GetPricing
                            │
                            ▼
                     HUMAN APPROVAL
                            │
                            ▼
                      CreateDomain
                            │
                            ▼
                  Create DNS record
                            │
                     List/read-back
                            │
                            ▼
                  VERIFIED RECEIPT
```

## The problem

Before an agent can use a service, it has to decide which service a domain represents. Nobody has measured whether agents actually understand domain names — until now.

## What DomainArena measures

> Given a task description, which domain names do AI agents infer are relevant, which do they select, and does the hostname itself affect their choice?

Four independent papers (ToolTweak, Tool Preferences Unreliable, ToolDNS, PA-Tool) identified that naming drives agent behavior. None built the measurement tool. We did.

## Quick start

```bash
pip install -e .
cp .env.example .env       # add name.com + Cloudflare credentials
python -m domainarena.web.demo   # hackathon demo on http://127.0.0.1:8777
```

## How name.com is central

DomainArena uses **6 name.com API endpoints** in one workflow:

| Endpoint | Purpose |
|---|---|
| `POST /domains:search` | Find available candidates |
| `POST /domains:checkAvailability` | Fresh check before purchase |
| `GET /domains/{domain}:getPricing` | Price verification |
| `POST /domains` | Register (idempotent) |
| `POST /domains/{domain}/records` | DNS evidence receipt |
| `GET /domains/{domain}/records` | Verify configuration |

## Hackathon demo

The demo shows the full flow:

1. **YOUR INTENT** — describe what you're building
2. **LIVE DISCOVERY** — name.com search returns real inventory
3. **AGENT COMPREHENSION** — AI models infer what each domain does (blind)
4. **DOMAIN ARENA** — evidence-based recommendation
5. **LIVE CHECKOUT** — fresh availability + pricing (fail-closed)
6. **REGISTRATION** — idempotent CreateDomain
7. **DNS** — evidence receipt via TXT record
8. **VERIFIED** — content-addressed receipt hash

## Safety

- **Fail-closed**: missing/malformed availability → abort
- **Approval required**: registration needs explicit human approval
- **Price drift guard**: price changes beyond threshold invalidate approval
- **Idempotent**: duplicate registration attempts can't double-charge
- **purchaseType=registration**: enforced on every availability check

## Architecture

```
domainarena/
├── api/
│   ├── http.py          # FastAPI: recommend/approve/register
│   └── mcp.py           # MCP server: 8 agent-callable tools
├── arena/
│   ├── semantic_inversion.py  # blind inference scoring
│   ├── discovery.py           # selection trials
│   ├── execution.py           # task verification
│   └── pairwise.py            # AB/BA randomization
├── models.py            # EvidenceVector, Candidate, etc.
├── optimizer.py         # Pareto selection + weighted scoring
├── providers/
│   └── namecom.py       # name.com client (fail-closed)
├── web/
│   └── demo.py          # hackathon demo UI
└── world.py             # cogym worldpack
```

## MCP tools

```text
search_domain         — search name.com inventory
check_availability    — check purchasable status
get_pricing           — get purchase/renewal prices
recommend_domain      — full pipeline recommendation
compare_domains       — pairwise evidence comparison
prepare_registration  — fresh check before purchase
register_domain       — register (sandbox only)
get_dns               — list DNS records
```

## Evidence

Every experiment produces:
- Content-addressed receipt (sha256 of config + results)
- Timestamped trial data
- Model family attribution
- AB/BA position balance verification

## License

MIT
