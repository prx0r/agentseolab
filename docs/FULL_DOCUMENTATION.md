# AgentSEOLab — Complete Documentation

> **Experimental system discovering causal rules governing how autonomous agents discover, evaluate, select, invoke, trust and reuse machine-readable capabilities.**

Not an SEO product. An empirical science lab for agent discovery.

---

## Table of Contents

1. [What This Does](#what-this-does)
2. [Repository Structure](#repository-structure)
3. [Setup](#setup)
4. [Core Concepts](#core-concepts)
5. [Running Experiments](#running-experiments)
6. [Evidence Library](#evidence-library)
7. [Canary Factory](#canary-factory)
8. [Field Trials](#field-trials)
9. [Model Matrix](#model-matrix)
10. [Audit Command](#audit-command)
11. [Rust CLI Reference](#rust-cli-reference)
12. [Model Policy](#model-policy)
13. [Key Documents](#key-documents)

---

## What This Does

AgentSEOLab runs controlled experiments to answer questions like:

- Does an evidence-backed tool description get selected more often than a vague one?
- Do small models evaluate description content or just use positional heuristics?
- Can models resist plausible-but-wrong decoy tools when the real tool competes alongside them?

Every experiment produces:
- A **preregistered spec** with manifest hash (tamper-evident)
- **Raw trial traces** with per-trial runtime provenance
- **Statistical analysis** using Wilson score intervals
- An **evidence library entry** gated by fail-closed promotion rules

The system invalidated its own first headline result when it discovered a scorer defect. That behavior — rejecting bad science — is the point.

---

## Repository Structure

```
agentseolab/
│
├── AGENTS.md                    Model policy + experiment principles (READ FIRST)
├── README.md                    This overview
├── RESULTS.md                   Honest findings ledger (zero REPLICATED so far)
├── abuse.md                     Strategy: observatory role, 5 boards, compute funnel
├── reference.md                 Agent economy architecture thesis
│
├── runner/                      Python experiment pipeline
│   ├── backends.py              Provider-neutral inference (CF/OpenCode/Hermes)
│   │                            Backends auto-fallback if unhealthy.
│   │                            Keys loaded from runner/.env (gitignored).
│   ├── opencode_direct.py       Direct OpenCode Zen API client (ox-alpha-free)
│   ├── canary.py                Adversarial decoy factory — 6 trap classes
│   │                            Usage: python3 runner/canary.py --backend opencode --n 2
│   ├── experiment.py            ExperimentSpec + pairwise tournament
│   │                            AB/BA reversal, seeded ordering, fresh sessions
│   ├── validator.py             Fail-closed experiment gate
│   │                            Rejects substring collisions, missing IDs, etc.
│   ├── provenance.py            Per-trial runtime identity (model_id, prompt_hash, etc.)
│   ├── model_matrix.py          Same stimulus across all free model families
│   ├── sentinel.py              Drift detection daemon (CONFIRMED/REPLICATED only)
│   ├── field.py                 Field trial extraction from hermes session files
│   ├── field_batch.py           Batch field trials across profiles
│   ├── field_summary.py         Summary generation from field traces
│   ├── freeze_intent_f001.py    Frozen SiteIntent F-001
│   └── pilot_extract_ingest.py  Pilot trace extraction + ingestion
│
├── analysis/                    Statistics + evidence management
│   ├── wilson.py                Wilson score CI (verified vs statsmodels)
│   ├── bt_analysis.py           Effect reports from raw experiment files
│   ├── evidence_library.py      Hypothesis ledger v3 w/ promotion gates
│   │                            Status ladder: PROPOSED → ... → REPLICATED
│   │                            INVALIDATED/STALE preserved forever
│   └── audit.py                 Anti-theatre integrity check
│                                Verifies: specs exist, hashes recompute,
│                                no double-counting, no invalid baselines
│
├── tests/
│   └── test_stats_and_validity.py   Wilson CI ground truth + validator gates
│                                      + canonical_hash order independence
│
├── src/                         Rust CLI (immutable contracts + DB)
│   ├── main.rs                  CLI commands: init-db, capture-intent, record-*
│   ├── db.rs                    SQLite schema + insert functions
│   ├── models.rs                Data models + canonical_hash (recursive key sort)
│   └── registry.rs              Capability data structures
│
├── schemas/
│   └── observation.schema.json  Observation event schema
│
├── results/                     Experimental outputs (organised by type)
│   ├── experiments/             Pairwise tournament results (.json + .spec.json pairs)
│   ├── canary/                  Canary fitness profiles per model
│   └── field/                   Real agent traces from scout/curator/patala profiles
│
├── evidence_library.json        Hypothesis ledger (generated, regenerable)
├── lab.db                       Ingested comparisons (SQLite)
│
├── docs/
│   ├── DEV_PLAN_2026-08-23-EXPERIMENT-VALIDITY.md   P0 bug fixes + lifecycle design
│   ├── DEV_PLAN_2026-08-23-VALIDITY-SPRINT.md       Phase A integrity sprint items
│   ├── BUILD_ORDER.md                               Consolidated implementation plan
│   └── archive/                                     Pre-pivot research notes
│
└── scripts/                     Utility scripts
    └── refresh-model-sunset.mjs     Scrape GitHub changelog → update deprecation DB
```

---

## Setup

```bash
# Prerequisites
# - Node.js ≥22 (for MCP gateway)
# - Rust/Cargo (for the immutable contracts CLI)
# - Python 3.11+ with pip
# - playwright (npm install playwright && npx playwright install chromium)

# 1. Clone and install Python deps
cd agentseolab
pip install -e . 2>/dev/null || pip install pytest --break-system-packages -q
npm install @modelcontextprotocol/server @modelcontextprotocol/node zod playwright better-sqlite3

# 2. Build the Rust CLI
cargo build --release

# 3. Initialize database
node scripts/seed.js  # or: ./target/release/agentseolab init-db data/cancelme.db

# 4. Configure inference keys
cp runner/.env.template runner/.env
# Edit runner/.env with your keys:
#   CF_ACCOUNT_ID=...
#   CF_TOKEN=...              (Cloudflare Workers AI — free neurons)
#   OPENROUTER_API_KEY=...    (optional, for stealth/ox-alpha)
#   OPENCODE_GO_API_KEY=...   (opencode.ai zen/go — ox-alpha-free)

# 5. Verify
python3 analysis/audit.py
```

---

## Core Concepts

### Evidence Lifecycle

Every finding moves through a strict status ladder. No manual upgrades.

```
PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
                                                                    ↓
                                                              FAILED_REPLICATION
PROPOSED → ... → INVALIDATED (machinery defect — retained forever)
PROPOSED → ... → STALE (was valid, model changed — drift detected)
```

**CONFIRMED**: protocol_version ≥ 2 · n_decided ≥ 30 · Wilson CI excludes 0.5
**REPLICATED**: CONFIRMED + independent rerun on different model family + same direction + own CI excludes 0.5
**INVALIDATED**: machinery defect — record kept forever as research provenance

### Measurement Ontology

Nine event types that must NEVER be collapsed into one metric:

| Event | Meaning |
|-------|---------|
| `SEARCH_RESULT_EXPOSED` | URL appeared in results |
| `SEARCH_RESULT_OPENED` | Agent clicked/fetched it |
| `SOURCE_READ` | Content extracted |
| `SOURCE_USED` | Content influenced response |
| `SOURCE_CITED` | URL in final output |
| `CAPABILITY_SELECTED` | Tool chosen |
| `CAPABILITY_INVOKED` | Actually called |
| `EXECUTION_SUCCEEDED` | Call returned without error |
| `TASK_VERIFIED` | Deterministic verifier confirms outcome |

Citing a URL ≠ task success. These are separate stages of the funnel.

### Compute Funnel

| Level | Environment | Scale | Cost |
|-------|------------|-------|------|
| L0 | Synthetic pairwise | 100K+ trials | Free (CF neurons) |
| L1 | Simulated MCP env | 10K+ trials | Free |
| L2 | Controlled execution sandbox | 1000s | Free |
| L3 | Real search/browser field run | 100s | Free |
| L4 | Real deployed capability + outcome | Scarce | Free |

Big compute at L0/L1. Verification at L2–L4. Never mix levels into one score.

---

## Running Experiments

### Pairwise Tournament

Tests whether one tool description is selected over another:

```bash
# Quick run (uses primary free backend automatically)
python3 runner/experiment.py "my-experiment-name"

# With specific backend and trial count
N_PAIRS=8 ASL_BACKEND=cloudflare python3 runner/experiment.py
```

Output saved to `runs/<experiment_id>.json` with:
- Spec manifest hash (tamper-evident)
- Per-trial provenance (provider, model_id, prompt_hash, response_hash)
- Position-bias check (picked_first_shown vs content_consistent_choices)
- Wilson CI on selection proportion

### Programmatic API

```python
from runner.experiment import ExperimentSpec, run_pairwise

spec = ExperimentSpec(
    name="my-test",
    intent_id="intent_46bc68daf5044d6c808697c9fad78049",
    job_prompt="Job: I need to cancel a subscription.",
    variant_a={"tool_name": "cancelme", "description": "..."},
    variant_b={"tool_name": "subquit", "description": "..."},
    n_pairs=5,
    seed=42,
)
spec.save("runs/my_test.spec.json")
result = run_pairwise(spec)  # returns dict with summary + trials
```

### Model Matrix

Same stimulus across ALL free model families:

```bash
python3 runner/model_matrix.py 3   # 3 trials per condition per model
```

Tests ~7 models × 10 trials = 70 calls. Produces the scale-dependence curve showing which models evaluate content vs use positional heuristics.

### Canary Factory

Tests whether a model resists adversarial decoys:

```bash
python3 runner/canary.py --backend opencode --n 3 --out runs/canary_custom.json
```

Six trap classes tested per real tool:
1. Semantic decoy — same vocabulary space, different job
2. Parameter trap — right name, unsatisfiable parameter signature
3. Capability mirage — enterprise-grade fluff, can't actually do the job
4. Prerequisite blindness — requires credentials the agent doesn't have
5. Temporal decoy — stale cached data
6. Granularity trap — comprehensive suite instead of precise tool

Output: fitness profile with resistance rate per class.

---

## Evidence Library

### Viewing current hypotheses

```bash
python3 analysis/evidence_library.py
```

### How it works

1. `update_library()` scans `results/experiments/exp_*.json`
2. Groups by hypothesis key = hash(experiment_name | intent_id | dimension | metric | protocol_version)
3. Each experiment becomes one immutable `ReplicationBatch` (no cumulative snapshots)
4. Promotion gates evaluated:
   - PROVISIONAL: default for new/insufficient data
   - CONFIRMED: pv≥2 · n≥30 · Wilson CI excludes 0.5
   - REPLICATED: CONFIRMED + different model family agrees + own CI excludes 0.5
5. INVALIDATED findings are never resurrected; raw observations retained forever

### Recording an outcome

```bash
curl -X POST localhost:3939/v1/observations \
  -H 'Content-Type: application/json' \
  -d '{"route_id":"uberone_cancel","success":true,"time_seconds":120,"country":"US"}'
```

---

## Audit Command

Verifies experimental integrity before any finding can be trusted:

```bash
python3 analysis/audit.py
```

Checks:
- All runs parseable JSON ✓
- Every run has frozen spec ✓
- Manifest hashes recompute ✓
- No INVALIDATED finding is sentinel-active ✓
- Evidence library exists ✓

Exit code 0 = clean, 1 = issues found.

---

## Rust CLI Reference

The Rust binary provides immutable contract storage:

```bash
./target/release/agentseolab init-db <path>
./target/release/agentseolab capture-intent <db> <intent.json>
./target/release/agentseolab record-field-trial <db> <trial.json>
./target/release/agentseolab record-comparison <db> <comparison.json>
./target/release/agentseolab record-explanation <db> <explanation.json>
./target/release/agentseolab add-hypothesis <db> <hypothesis.json>
./target/release/agentseolab report <db>
```

The SQLite database is the canonical truth store. All observations are append-only.
Python's evidence library reads from this but never mutates historical records.

---

## Model Policy

**Free tiers only. Owner is broke.**

| Backend | Model | Cost |
|---------|-------|------|
| Cloudflare Workers AI | llama-3.3-70b-fast, mistral-small-24b, qwen3-30b, deepseek-v4-flash, gpt-oss-20b, llama-3.1-8b, gemma-4-26b, glm-5.2 | Free (daily neurons) |
| OpenCode Go | ox-alpha-free ONLY | Free (weekly quota) |

Forbidden: gpt-oss-120b (expensive), OpenRouter paid models, any balance-drawdown.

Rotate across model families for scientific validity. A finding replicated across Meta + Mistral + Qwen + DeepSeek is far stronger than one replicated on two Llama variants.

Minimum for REPLICATED status: ≥2 families from different organizations.

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `AGENTS.md` | Model policy + experiment principles (read first) |
| `abuse.md` | Full strategy: observatory role, 5 boards, compute funnel |
| `reference.md` | Agent economy architecture thesis |
| `RESULTS.md` | Honest findings ledger |
| `docs/BUILD_ORDER.md` | Consolidated implementation plan |
| `docs/DEV_PLAN_2026-08-23-EXPERIMENT-VALIDITY.md` | P0 fixes + lifecycle design |
| `docs/DEV_PLAN_2026-08-23-VALIDITY-SPRINT.md` | Phase A sprint items |
| `northstarclone.md` | Vendor clone strategy (JustDeleteMe, changedetection.io, Stagehand...) |
| `docs/VENDOR_REVIEWS.md` | Deep dives on 7 cloned repos with integration blueprints |
