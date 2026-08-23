# AgentSEOLab — Consolidated Implementation Plan
*2026-08-23 · supersedes all prior dev plans · single source of truth for build order*

## Codebase Inventory

| Module | Lines | Status | Role |
|--------|-------|--------|------|
| `runner/backends.py` | 95 | ✅ working | Provider-neutral inference: OpenCode/Cloudflare/Hermes |
| `runner/opencode_direct.py` | 33 | ✅ working | Direct zen API client (ox-alpha-free) |
| `runner/canary.py` | 101 | ✅ validated | Adversarial decoy factory (6 trap classes) |
| `runner/experiment.py` | 194 | ✅ works | Pairwise tournament AB/BA seeded reversal |
| `runner/validator.py` | 49 | ✅ working | Fail-closed experiment gate |
| `runner/provenance.py` | 21 | ✅ working | Per-trial runtime identity |
| `runner/model_matrix.py` | 123 | ⚠️ untested | Multi-model sweep across all free families |
| `analysis/wilson.py` | 11 | ✅ verified | Wilson CI (matches statsmodels) |
| `analysis/bt_analysis.py` | 42 | ✅ working | Effect reports from raw runs |
| `analysis/evidence_library.py` | 242 | ✅ v3 gates | Hypothesis ledger fail-closed promotion |
| `analysis/audit.py` | 74 | ✅ passing | Anti-theatre integrity check |
| `runner/sentinel.py` | 612 | 🔧 builder WIP | Drift detection daemon |
| `runner/field.py` | 505 | 🔧 builder WIP | Field trial extraction from hermes sessions |
| `runner/field_batch.py` | 132 | 🔧 builder WIP | Batch scaling across profiles |
| `src/main.rs` | 277 | ✅ working | Rust CLI (init-db, capture-intent, record-*, report) |
| `src/db.rs` | 344 | ✅ fixed | SQLite: explanations + search_queries populated |

## Known Gaps

| Gap | Impact | Phase |
|-----|--------|-------|
| experiment.py trials lack nested provenance | pv1 runs stay PROVISIONAL forever | **B1** |
| model_matrix untested | Can't produce scale-dependence curve | **B2** |
| No MCP sandbox | Can't measure selection→execution→success | **C1** |
| Sentinel stub doesn't match builder's tests | 20 failing tests | **D1** |
| free_ai.rs + hydradb.rs dead code | Bundle bloat | **D2** |
| No unified CLI entry point | Every operation is a separate script invocation | **D3** |

---

## BUILD ORDER

### Phase B — Pipeline Completion (current)

**B1. Wire provenance into experiment.py**
- Each TrialRecord gets a nested `provenance` dict from `provenance.py`
- Trials become protocol_version=2 → eligible for CONFIRMED promotion
- File: `runner/experiment.py`
- Test: existing tests still pass + provenance fields present in output JSON

**B2. Validate + run model_matrix.py across all free CF models**
- Smoke test each backend individually first
- Then run the full matrix (7 models × 10 trials = 70 calls, ~15 min)
- Produces the model-scale-dependence curve: which models evaluate description content vs use positional heuristics
- File: `runner/model_matrix.py`, output: `results/model_matrix.json`

**B3. Integrate builder's field system**
- Review `runner/field.py` (505 lines) — it extracts real traces from hermes session files
- Review `runner/field_batch.py` — scales across scout/curator/patala profiles  
- Wire into evidence library so field observations feed hypothesis updates
- Test against the 8 existing field traces in `results/field/`

### Phase C — Execution-Grounded Science

**C1. MCP Sandbox**
This is the biggest missing piece. Without it we can only measure SELECTION, not whether selections actually work.

Build a local MCP server exposing simulated tools:
```
sandbox/
├── tools/
│   ├── domain_verify.py      # real: checks DNS via DoH, returns structured result
│   ├── domain_scout.py       # semantic decoy: searches web mentions
│   ├── dominatron_pro.py     # mirage: returns error "requires enterprise"
│   └── ...
├── verifier.py               # deterministic task-success checker
└── server.py                 # lightweight MCP-compatible HTTP endpoint
```

Each tool either:
- Returns correct structured result → EXECUTION_SUCCEEDED
- Returns an error / wrong data type → EXECUTION_FAILED
- Requires unavailable credentials → PREREQUISITE_BLOCKED

Then the experiment becomes:
```
model sees tool descriptions
→ selects one
→ constructs parameters
→ sandbox executes
→ deterministic verifier checks output
→ TASK_VERIFIED or EXECUTION_FAILED
```

Useful Selection = P(selected AND executed AND verified). This is the metric that matters per AgentSearchBench.

**C2. Run ASL-001 (Selection ≠ execution)**
Two tools:
- A: compelling description, subtly cannot complete the job
- B: plain description, genuinely succeeds

Measure across ≥2 model families × n≥10:
- selection_rate(A) vs execution_success(A)
- Useful Selection = P(selected AND succeeded)

If A wins selection but fails execution → proof that description quality ≠ capability quality.

**C3. ASL-002–008 series**
After ASL-001 proves the methodology, run remaining experiments:
- Overclaim penalty · Prerequisite blindness · Freshness sensitivity
- Parameter-schema fitness · Distractor density · Name×description factorial

### Phase D — Infrastructure Hardening

**D1. Complete sentinel implementation**
Builder's test_sentinel.py has 20 TDD specs. Implement to pass them.

**D2. Remove dead Rust code**
Delete free_ai.rs (Python handles inference), hydradb.rs (premature).

**D3. Unified CLI entry point**
```bash
agentseolab run --experiment ASL-001 --models llama-3.3,mistral-small --n 10
agentseolab audit
agentseolab report --hypothesis H-CANARY-002
agentseolab sentinel --check-drift
```

**D4. Continuous pipeline**
- Cron: source-monitor every 6h
- Cron: model-sunset refresh daily  
- Cron: sentinel drift-check on model version change
- Webhook: changedetection.io → verification queue

### Phase E — Scale & Science

Only after C1 produces a REPLICATED finding:
- Evolution campaign (32 variants, successive halving, MAP-Elites)
- Naming science program (7 experiments)
- Cogym∘AgentSEO synthetic economy bridge
- MCP Registry submission for distribution

---

## Dependency Graph

```
B1 (provenance) ──────────────────────────────────┐
B2 (model matrix) → model-scale curve published    │
                                                    ▼
C1 (MCP sandbox) → C2 (ASL-001) → C3 (ASL series)
                                                    │
D1-D4 (infrastructure) ────────────────────────────┤
                                                    ▼
                              E (evolution + naming science + economy)
                              ONLY after first REPLICATED finding exists
```

## Current Blockers

| Blocker | Unblocks |
|---------|----------|
| OpenCode Go quota resets in ~20h | ox-alpha-free experiments |
| Docker daemon broken on this box | Browsertrix WACZ archival, changedetection.io sidecar |
| Builder agent running its own tasks | Don't interfere with agentseo-* boards |
