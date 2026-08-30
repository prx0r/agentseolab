# DomainArena

**A/B testing for domain names in the agentic web.**

## The problem

Before an agent can use a service, it has to decide which service a domain represents. Nobody has measured whether agents actually understand domain names — until now.

## What DomainArena measures

> Given a task description, which domain names do AI agents infer are relevant, which do they select, and does the hostname itself affect their choice?

## 30-second demo

```
1. YOU: "I'm building a JSON repair tool"
2. SEARCH: name.com finds 3 available domains
3. COMPREHENSION: AI infers what each domain does (blind)
4. ARENA: Evidence-based recommendation
5. CHECKOUT: Fresh availability + pricing
6. APPROVAL: You approve the winner
7. REGISTER: name.com registers it
8. DNS: Evidence receipt recorded
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

## Architecture

```
         PRODUCT INTENT
               |
               v
      name.com SEARCH API
         live inventory
               |
          hard constraints
               |
               v
        DOMAIN ARENA
  semantic comprehension
  randomized pairwise choice
  cross-model robustness
               |
               v
         RECOMMENDATION
               |
          CheckAvailability
               |
             GetPricing
               |
               v
         HUMAN APPROVAL
               |
            CreateDomain
               |
        Create DNS record
          List/read-back
               |
               v
        VERIFIED RECEIPT
```

## Safety and purchase approval

- **Fail-closed**: Missing/malformed availability → abort
- **Approval required**: Registration needs explicit human approval
- **Price drift guard**: Price changes beyond threshold invalidate approval
- **Idempotent**: Duplicate registration attempts can't double-charge
- **purchaseType=registration**: Enforced on every availability check

## MCP tools

```text
search_domain         — search name.com inventory
check_availability    — check purchasable status
get_pricing           — get purchase/renewal prices
recommend_domain      — full pipeline recommendation
compare_domains       — pairwise availability + pricing + semantic fit
prepare_registration  — fresh check before purchase
approve_domain        — approve for registration (returns token)
register_domain       — register (requires approval token)
configure_dns         — create DNS evidence receipt
```

## API

```bash
# Recommend
curl -X POST http://localhost:8801/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"description": "A JSON repair tool", "primary_job": "fix malformed JSON"}'

# Get decision state
curl http://localhost:8801/v1/decisions/{id}

# Prepare registration (fresh availability + pricing check)
curl -X POST http://localhost:8801/v1/decisions/{id}/prepare-registration

# Approve (returns approval_token)
curl -X POST http://localhost:8801/v1/decisions/{id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approve": true}'

# Register (requires approval_token)
curl -X POST http://localhost:8801/v1/decisions/{id}/register \
  -H "Content-Type: application/json" \
  -d '{"approval_token": "..."}'

# Configure DNS evidence receipt
curl -X POST http://localhost:8801/v1/decisions/{id}/configure-dns
```

## Quickstart

```bash
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab
pip install -e .
cp .env.example .env       # add name.com + Cloudflare credentials
python3 -m domainarena.web.demo   # hackathon demo on http://127.0.0.1:8777
```

## Tests

```bash
pytest tests/domainarena/ -v    # 138 tests passing
```

### Test coverage

- `test_world.py` — DomainArenaWorld state transitions, terminal conditions, scoring
- `test_lifecycle_e2e.py` — Full recommend → approve → prepare → register → DNS flow + persistence roundtrip
- `test_namecom.py` — name.com client (mock + integration)
- `test_policy_api.py` — Optimizer policy, Pareto front, HTTP API
- `test_additional.py` — Demo smoke, MCP approval bypass, business audience, provenance

## Limitations

- Requires name.com API credentials for live inventory
- Requires Cloudflare Workers AI for semantic comprehension
- Registration only in sandbox mode (production requires explicit approval)
- Single-model semantic scoring (cross-model replication pending)

## License

MIT
