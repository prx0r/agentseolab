# AgentSEOLab

**Experimental system discovering causal rules governing how autonomous agents discover, evaluate, select, invoke, trust and reuse machine-readable capabilities.**

Not an SEO product. An empirical science lab.

## Current Status

**Evidence: zero REPLICATED findings.** The system correctly invalidated its first headline result and refused to promote unreplicated effects. See `RESULTS.md`.

## Architecture

```
runner/          Python experiment pipeline
  experiment.py    ExperimentSpec + pairwise tournament (seeded, AB/BA)
  backends.py      Provider-neutral inference (Cloudflare/OpenCode/Hermes)
  canary.py        Adversarial decoy factory (6 trap classes)
  validator.py     Fail-closed experiment gate
  provenance.py    Per-trial runtime identity
  sentinel.py      Drift detection (CONFIRMED/REPLICATED only)
analysis/        Statistics + evidence management
  wilson.py        Wilson score CI (verified vs statsmodels)
  bt_analysis.py   Effect reporting from raw runs
  evidence_library.py  Hypothesis ledger w/ promotion gates
  audit.py         Anti-theatre integrity check
src/             Rust CLI (contracts, DB, immutable records)
tests/           pytest suite
results/         Immutable experimental outputs
docs/            Dev plans + archived research notes
```

## Quick Start

```bash
pip install -e .
cargo build --release
./target/release/agentseolab init-db lab.db

# Run an experiment (uses free models only — see AGENTS.md)
python3 runner/experiment.py

# Check evidence integrity
python3 analysis/audit.py

# View hypothesis ledger
python3 analysis/evidence_library.py

# Tests
python3 -m pytest tests/test_stats_and_validity.py -q
```

## Key Principle

> No effect enters the evidence library unless the experiment itself has passed validation.

See `AGENTS.md` for model policy (free tiers only). See `abuse.md` for full strategy.
