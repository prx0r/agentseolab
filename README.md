# AgentSEOLab → **DomainArena**

> **DomainArena is not a naming generator. It is an empirical decision engine over name.com's live domain inventory.**
>
> It measures whether a candidate domain causes the intended human or AI agent to correctly understand, select and successfully use the product — then recommends the best purchasable option under hard budget constraints.

*Product layer of the AgentSEOLab empirical lab (lineage preserved — see `docs/HACKATHON_LINEAGE.md`).*

## DomainArena quick start

```bash
source /home/box/Documents/patala/.venv/bin/activate
export $(grep -v '^#' runner/.env | xargs)

# Live recommendation over real name.com inventory (read-only)
python3 -m domainarena.pipeline

# Demo UI: intent → evidence table → explained recommendation
python3 -m domainarena.web/app.py   # http://127.0.0.1:8777

# MCP server for agents
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 -m domainarena.api.mcp

# Tests
python3 -m pytest tests/domainarena -q
```

## How it works

```
frozen intent (sha256-locked)
  → heterogeneous generators ∩ name.com live Search
  → HARD feasibility filters ($20 means >$20 impossible — removal, not penalty)
  → Semantic Inversion proxy (blind hostname inference across model families)
  → AB/BA pairwise arena + Bradley–Terry
  → execution-grounded selection + hidden deterministic verifier
  → cross-family / cross-serving-window robustness (worst family reported)
  → Pareto frontier → audience-conditioned recommendation
  → approval gate → recheck → register → DNS evidence receipt
```

| Doc | Purpose |
|-----|---------|
| [northstar.md](northstar.md) | Product thesis |
| [HACKATHON_NORTHSTAR.md](HACKATHON_NORTHSTAR.md) | Competition criteria mapping |
| [docs/HANDOVER_2026-08-24.md](docs/HANDOVER_2026-08-24.md) | Full agent handover |
| [docs/EXPERIMENT_REDESIGN.md](docs/EXPERIMENT_REDESIGN.md) | Canonical v2 protocols |
| [docs/namecom-api/](docs/namecom-api/) | Complete name.com Core API docs |

---

# AgentSEOLab (lab core)

> **Experimental system discovering causal rules governing how autonomous agents discover, evaluate, select, invoke, trust and reuse machine-readable capabilities.**

Not an SEO product. An empirical science lab.

## Documentation

**Full documentation: [docs/FULL_DOCUMENTATION.md](docs/FULL_DOCUMENTATION.md)**

| Doc | Purpose |
|-----|---------|
| [AGENTS.md](AGENTS.md) | Model policy + experiment principles (READ FIRST) |
| [RESULTS.md](RESULTS.md) | Honest findings ledger — zero REPLICATED findings yet |
| [abuse.md](abuse.md) | Strategy: observatory role, 5 boards, compute funnel |
| [reference.md](reference.md) | Agent economy architecture thesis |
| [BUILD_ORDER.md](docs/BUILD_ORDER.md) | Consolidated implementation plan |

## Quick Start

```bash
pip install pytest --break-system-packages -q
cargo build --release

# Run an experiment
python3 runner/experiment.py

# Verify integrity
python3 analysis/audit.py

# View hypothesis ledger
python3 analysis/evidence_library.py
```

## Key Principle

> No effect enters the evidence library unless the experiment itself has passed validation.

The system invalidated its own first headline result when it discovered a scorer defect. That behavior is the point.
