# AgentSEOLab

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
