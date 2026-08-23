# AgentSEOLab — Complete Documentation
*Last updated: 2026-08-23 05:30 UTC*

## What This Is

An empirical science lab that discovers causal rules governing how autonomous agents discover, evaluate, select, invoke, trust, and reuse machine-readable capabilities.

We run controlled experiments where AI models interact with simulated tools in a sandboxed environment. Every tool call is recorded, executed, and verified by a deterministic checker that never consults the model's self-report. Findings are gated through a fail-closed evidence lifecycle before they enter the knowledge base.

**Current status: zero REPLICATED findings. The system has correctly invalidated its own first headline result and refused to promote unreplicated effects. This is the system working as designed.**

---

## Quick Start

```bash
# Prerequisites: Python 3.11+, Node.js ≥22, Rust/Cargo

# Install
pip install pytest --break-system-packages -q
npm install playwright better-sqlite3 --save
cargo build --release

# Configure keys (edit with your values)
cp runner/.env.template runner/.env

# Verify infrastructure
python3 analysis/audit.py
python3 -m pytest tests/test_stats_and_validity.py -q

# Run first experiment
python3 runner/execution_experiment.py cloudflare 5
```

---

## Repository Structure Explained

### `/root/agentseolab/` — Root

| File | Purpose | Status |
|------|---------|--------|
| `AGENTS.md` | **Model policy + experiment design rules. READ FIRST.** Defines which free models to use, forbidden models, rotation requirements, controls checklist, statistical standards, evidence lifecycle, measurement ontology, compute funnel discipline. | ✅ Active |
| `experiments-rules.md` | Canonical experiment rules — standardised model batch (9 families from 7 orgs), controlled variables checklist, bias controls table, statistical test selection guide, sample size guidance. Also at `/root/experiments-rules.md`. | ✅ Active |
| `RESULTS.md` | Honest findings ledger. Documents what we found, what we didn't, what was invalidated. Currently: zero REPLICATED findings (correct behavior). | ✅ Active |
| `abuse.md` | Full strategy document: observatory role, 5 permanent boards, L0–L4 compute funnel, frontier research citations (AgentSearchBench, SAGEO Arena, canary tools, AgenticGEO), 10-item sprint plan. | ✅ Reference |
| `reference.md` | Agent economy architecture thesis: discovery → decision → authorize → execute → receipt → learn stack. Maps all projects into one coherent architecture. | ✅ Reference |
| `northstarclone.md` | Vendor clone strategy: JustDeleteMe + OpenTermsArchive + Stagehand + changedetection.io assembly plan. | ✅ Reference |
| `.gitignore` | Excludes node_modules, *.db, *.db-shm/wal, .env, logs/, artifacts/, __pycache__/ | ✅ Active |

### `runner/` — Python Experiment Pipeline

All inference backends load API keys from `runner/.env` (gitignored). Template at `runner/.env.template`.

| File | Lines | What It Does | Key Functions |
|------|-------|--------------|---------------|
| `backends.py` | 95 | Provider-neutral inference. Three adapters: CloudflareBackend (CF Workers AI), HermesBackend (hermes CLI), OpenCodeDirect (zen API direct). Health-probe fallback chain. Free CF models listed in FREE_CF_MODELS. | `get_backend(preferred)` → returns backend with auto-fallback |
| `opencode_direct.py` | 33 | Direct HTTP client for opencode.ai zen/go API. Custom User-Agent required (urllib default gets 403). | `run(prompt)` → {ok, raw, session_id, latency_ms} |
| `experiment.py` | ~200 | Pairwise tournament runner. ExperimentSpec with manifest hash. AB/BA order reversal, seed-driven shuffle. Fresh session per trial. Abstention allowed (UNPARSEABLE ≠ wrong). Position-bias check built in. Provenance wired via `_provenance()` helper. | `ExperimentSpec(...)`, `run_pairwise(spec)`, `parse_choice(raw)` |
| `canary.py` | 101 | Adversarial decoy factory. Six trap classes: semantic_decoy, parameter_trap, capability_mirage, prerequisite_blindness, temporal_decoy, granularity_trap. Scoring by exact tool_id match (not substring). UNPARSEABLE distinct from incorrect. | `build_domain_canary_spec(seed, n_per)`, `run_canary(spec=..., backend_obj=..., backend_name=...)` |
| `validator.py` | 49 | Fail-closed experiment gate. Rejects: duplicate names, substring collisions between candidates, missing tool_ids, missing seed/job, insufficient trials. | `validate_canary(spec)` → raises ValidationError or returns True |
| `provenance.py` | 21 | Per-trial runtime identity: provider, model_id, temperature, max_tokens, prompt_hash, response_hash, ordering, runner_version. | `trial_provenance(backend, prompt, response, ordering, extra)` → dict |
| `model_matrix.py` | 123 | Same stimulus across ALL free model families. Produces scale-dependence curve. Tests ~7 models × N trials each. Outputs summary table + JSON. | `run_matrix(n_per)` → list of per-model results |
| `sentinel.py` | 612 | Drift detection daemon. Replays fixed trial suite against current models. Opens drift task when effect sizes change materially. Only CONFIRMED/REPLICATED hypotheses eligible as baselines. | `create_sentinel_suite()`, `check_drift(baseline_p, current_p, threshold)` |
| `field.py` | 505 | Field trial extraction from hermes session files. Parses real agent traces for search queries, results, opens, citations, tool calls. Event ontology enforcement. | Used by builder agent during field experiments |
| `field_batch.py` | 132 | Batch field trials across scout/curator/patala profiles. | Called by hermes kanban tasks |
| `field_summary.py` | 139 | Summary generation from field trace data. | Produces aggregate statistics |
| `execution_experiment.py` | ~140 | ASL-001 execution-grounded experiment. Two tools compete: compelling-but-broken vs plain-but-working. Model selects AND constructs params. Sandbox executes. Verifier checks outcome. Measures full funnel not just selection. | `run_trial(backend, variant_order, trial_no)`, CLI: `python3 runner/execution_experiment.py <backend> <n>` |

### `analysis/` — Statistics + Evidence Management

| File | Lines | What It Does | Key Functions |
|------|-------|--------------|---------------|
| `wilson.py` | 11 | Wilson score CI for binomial proportion. Canonical closed form. Verified against statsmodels `proportion_confint(method='wilson')`. Bounds always within [0,1]. | `wilson(k, n, z=1.96)` → {p, ci95, n, excludes_0.5} |
| `evidence_library.py` | 242 | Hypothesis ledger v3. Fail-closed promotion gates. Reads nested provenance.model_id from trials. Groups by causal-question hash (NOT description text). Each replication = one experiment's immutable result (no cumulative snapshots). Same-direction enforcement across model families. Status ladder: PROVISIONAL→CONFIRMED→REPLICATED. INVALIDATED retained forever. STALE marking for drift. | `update_library()`, `invalidate(hid, reason)`, `print_library()`, `load()`, `save(lib)` |
| `bt_analysis.py` | 42 | Effect reporting from raw run files. Uses Wilson CI (correctly). Skips non-pairwise files (canary etc.). | `collect_runs(dir)`, `report()` |
| `audit.py` | 74 | Anti-theatre integrity check. Verifies: runs parseable, every run has spec, manifest hashes recompute, no INVALIDATED sentinel-active, library exists. Exit code 0 = clean. | `run_audit(runs_dir, lib_path)` → bool; CLI: `python3 analysis/audit.py` |

### `sandbox/` — Execution Environment

| File | Lines | What It Does |
|------|-------|--------------|
| `world.py` | 252 | Resettable execution world with 4 tools that actually execute: domain_check (real DNS lookup), domain_scout (semantic decoy — web mention search), domain_cached (temporal decoy — stale cache), domain_enterprise (capability mirage — requires auth). Hidden deterministic verifier (`verify_task`) checks ACTUAL state after episode. Never consults agent self-report. Records every action and state transition. |
| `server.py` | ~50 | Lightweight MCP-compatible HTTP server exposing sandbox tools. Not yet integrated with main pipeline. |

### `src/` — Rust CLI (Immutable Contracts)

| File | Lines | What It Does |
|------|-------|--------------|
| `main.rs` | ~180 | CLI commands: init-db, capture-intent, record-field-trial, record-comparison, record-explanation, add-hypothesis, report |
| `db.rs` | 344 | SQLite schema (14 tables) + insert functions. WAL mode. All observations append-only. Fixed: insert_explanation now persists, search_queries populated per-query. |
| `models.rs` | ~250 | Data models: SiteIntent, FieldTrial, SearchQuery, PairwiseComparison, Explanation, Hypothesis. canonical_hash uses recursive key-sort (JCS-style). VALID_REASON_CODES constant. |
| `registry.rs` | 18 | Capability data structures only (HydraDB integration deferred). |

### `tests/`

| File | Tests | Status |
|------|-------|--------|
| `test_stats_and_validity.py` | 7 | ✅ All passing. Wilson CI vs statsmodels ground truth. Validator rejection cases. Canonical hash order independence. Choice parser abstain/wrong/unparseable distinction. |
| `test_sentinel.py` | 20 | ⏳ Builder's TDD specs — expected-fail until sentinel fully implemented |
| `test_field_protocol.py` | ? | Builder's field protocol tests |

---

## Data Files

| Path | Contents | Gitignored? |
|------|----------|-------------|
| `lab.db` | Ingested comparisons (SQLite, 36 rows) | Yes |
| `evidence_library.json` | Hypothesis ledger (3 entries: 1 INVALIDATED, 1 CONFIRMED_SINGLE_MODEL, 1 PROVISIONAL) | No — tracked |
| `results/experiments/*.json` | Raw experiment results + specs | No — tracked |
| `results/canary/*.json` | Canary fitness profiles | No — tracked |
| `results/field/*/trace_raw.json` | Real agent traces | No — tracked |
| `results/sandbox/ASL001_*.json` | Execution-grounded results | No — tracked |
| `data/services/seed.json` | CancelMe service seed data (10 services) | No — tracked |
| `runner/.env` | API keys | Yes — gitignored |

---

## How Everything Connects

```
RUNNER PIPELINE                    ANALYSIS                     EVIDENCE
─────────────────                 ──────────                   ────────
backends.py                       wilson.py
  (inference)                       (statistics)
      │                                ▲
      ▼                                │
experiment.py ──── runs/*.json ──► bt_analysis.py
  (pairwise AB/BA)                  (effect reports)
      │
      ├── provenance.py             evidence_library.py
      │   (per-trial identity) ◄── (hypothesis ledger)
      │                                 ▲
canary.py                               │
  (decoy resistance) ──── results/ ────┤
                                      │
validator.py                          │
  (pre-run gate)                      │
                                      │
execution_experiment.py               │
  (ASL-001 execution) ────────────────┘
      │
sandbox/world.py
  (resettable tools +
   hidden verifier)

SENTINEL
  reads CONFIRMED/REPLICATED hypotheses
  replays fixed suite on model change
  opens drift task if effect size shifts

AUDIT
  verifies entire pipeline integrity
  must pass before any finding published
```

---

## Running Experiments

### 1. Pairwise Tournament (L0 preference probe)

```bash
# Quick
python3 runner/experiment.py "my-test-name"

# With specific parameters
N_PAIRS=8 python3 runner/experiment.py

# What it does:
# - Presents two tool descriptions to the model
# - AB/BA order reversal (seed-shuffled)
# - Fresh session per trial
# - Records selection + position bias check
```

⚠️ **This measures stated preference, NOT behavior.** Results go to a separate ledger from execution-grounded findings.

### 2. Canary Factory (decoy resistance)

```bash
python3 runner/canary.py --backend cloudflare --n 3
python3 runner/canary.py --backend opencode --n 2 --out custom_path.json
```

Tests whether the model picks the REAL tool when competing against six types of adversarial decoys. Output includes fitness profile per trap class.

### 3. Execution-Grounded ASL-001

```bash
# On llama-3.3-70b via Cloudflare
python3 runner/execution_experiment.py cloudflare 10

# On ox-alpha-free via OpenCode Zen
ASL_BACKEND=opencode python3 runner/execution_experiment.py opencode 10
```

The model must SELECT a tool AND construct valid arguments. The sandbox EXECUTES the call. A deterministic verifier checks the output. TASK_VERIFIED requires the correct tool to have been invoked with valid parameters producing a verifiable result.

### 4. Model Matrix (scale-dependence curve)

```bash
python3 runner/model_matrix.py 3
```

Same stimulus across all available model families. Produces comparison table showing which models evaluate description content vs use positional heuristics.

### 5. Cross-Family Replication

```bash
python3 runner/cross_family.py
```

Runs the same experiment on two genuinely different model families simultaneously. REPLICATION confirmed if both show same direction with own CI excluding 0.5.

---

## Evidence Library Operations

```bash
# Update hypothesis ledger from latest runs
python3 analysis/evidence_library.py

# Mark hypothesis as stale (drift detected)
python3 -c "
import sys; sys.path.insert(0, 'analysis')
from evidence_library import mark_stale
mark_stale('H-CANARY-002', 'effect size drifted below threshold')
"

# View current state
python3 analysis/evidence_library.py
```

---

## Model Policy Summary

| Backend | Models | Cost | Notes |
|---------|--------|------|-------|
| Cloudflare Workers AI | llama-3.3-70b-fast · mistral-small-24b · qwen3-30b · deepseek-v4-flash · gpt-oss-20b · llama-3.1-8b · gemma-4-26b · glm-5.2 | Free (daily neurons) | Primary workhorse. Rotate families for diversity. |
| OpenCode Go | ox-alpha-free ONLY | Free (weekly quota) | Intermittent availability. Wait for reset when exhausted. |
| OpenRouter :free | gemma-4-26b:free, glm-5.2:free, nemotron-ultra-550b:free | Free tier | Rate limited but usable for small batches |

**Forbidden:** gpt-oss-120b (expensive neurons), any paid API, balance-drawdown prompts.

**Rotation requirement:** Minimum 2 different organisations for REPLICATED status. Rotate for diversity because different architectures produce different behavioral biases.
