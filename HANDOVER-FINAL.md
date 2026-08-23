# AgentSEOLab — Complete Handover
*2026-08-23 06:00 UTC*

## What This Project Is

Empirical science lab discovering causal rules governing how autonomous agents discover, evaluate, select, invoke, trust and reuse machine-readable capabilities.

NOT an SEO product. An execution-grounded experimental science system.

---

## Repository Structure (clean)

```
agentseolab/
├── AGENTS.md                    ← Model policy + experiment principles. READ FIRST.
├── experiments-rules.md         ← Canonical controls, stats, evidence lifecycle
├── RESULTS.md                   ← Honest findings ledger
├── abuse.md                     ← Strategy: observatory role, 5 boards, funnel
├── reference.md                 ← Agent economy architecture thesis
│
├── runner/                      ← Python experiment pipeline
│   ├── backends.py              ← Provider-neutral inference (CF/OpenCode/Hermes)
│   ├── opencode_direct.py       ← Direct zen API client (ox-alpha-free, mimo-v2.5)
│   ├── experiment.py            ← Pairwise tournament AB/BA + provenance
│   ├── canary.py                ← Adversarial decoy factory (v2 validated)
│   ├── validator.py             ← Fail-closed pre-run gate
│   ├── provenance.py            ← Per-trial runtime identity
│   ├── execution_experiment.py  ← ASL-001 execution-grounded experiment ⚠️ WIP
│   ├── factorial_experiment.py  ← 2×2 description×capability factorial ⚠️ WIP
│   ├── cross_family.py          ← Cross-family replication runner ⚠️ WIP
│   ├── model_matrix.py          ← Multi-model sweep ⚠️ untested
│   ├── sentinel.py              ← Drift detection daemon
│   └── field*.py                ← Field trial extraction from hermes sessions
│
├── analysis/
│   ├── wilson.py                ← Wilson CI (verified vs statsmodels)
│   ├── evidence_library.py      ← Hypothesis ledger v3 fail-closed gates
│   ├── bt_analysis.py           ← Effect reports from raw runs
│   └── audit.py                 ← Anti-theatre integrity check
│
├── sandbox/
│   └── world.py                 ← Resettable synthetic world w/ hidden oracle
│                                 4 tools: real + semantic decoy + temporal decoy
│                                 + capability mirage. Hidden verifier checks
│                                 ACTUAL state, never self-report.
│
├── src/                         ← Rust CLI (immutable contracts + DB)
│   ├── main.rs                  ← CLI commands
│   ├── db.rs                    ← SQLite schema + inserts (fixed)
│   ├── models.rs                ← Data models + canonical_hash
│   └── registry.rs              ← Capability data structures
│
├── tests/
│   ├── test_stats_and_validity.py  ← Wilson CI + validator + hash tests (7 pass)
│   ├── test_sentinel.py            ← Builder's TDD specs (WIP, expected-fail)
│   └── test_field_protocol.py      ← Field protocol tests
│
├── results/
│   ├── EXPERIMENT_INDEX.json    ← Auto-generated catalog of all runs
│   ├── experiments/             ← Pairwise + execution results
│   │   └── ASL-001/PEER_REVIEW.md  ← Peer review template + findings
│   ├── canary/                  ← Canary fitness profiles
│   └── field/                   ← Real agent traces from hermes profiles
│
├── sandbox/world.py             ← Synthetic stateful domain-registration world
├── data/services/seed.json     ← CancelMe seed data
├── schemas/observation.schema.json
│
├── docs/
│   ├── FULL_DOCUMENTATION.md    ← Complete file-by-file reference
│   ├── BUILD_ORDER.md           ← Consolidated implementation plan
│   ├── DEV_PLAN_2026-08-23-EXECUTION-GROUNDING.md  ← Current sprint plan
│   ├── DEV_PLAN_2026-08-23-VALIDITY-SPRINT.md      ← Phase A integrity fixes
│   ├── P0-ASL001-INVALIDATION.md                   ← Prior result invalidation
│   └── archive/                                     ← Pre-pivot research notes
│
└── experiments/                 ← Experiment folders with READMEs + arxiv refs
    ├── ASL-001/ through ASL-008/
    ├── CANARY/
    ├── MODEL-MATRIX/
    ├── FIELD/
    └── NAMING-SCIENCE/
```

---

## Setup From Scratch

```bash
# Prerequisites: Python 3.11+, Node.js ≥22, Rust/Cargo

# 1. Clone
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab

# 2. Python deps
pip install pytest --break-system-packages -q

# 3. Node deps (for MCP gateway)
npm install @modelcontextprotocol/server @modelcontextprotocol/node zod playwright better-sqlite3

# 4. Build Rust CLI
cargo build --release

# 5. Configure API keys
cp runner/.env.template runner/.env
# Edit runner/.env:
#   CF_ACCOUNT_ID=954612afb5a97bb15dddcdc70176813d
#   CF_TOKEN=<cloudflare workers AI token>
#   OPENROUTER_API_KEY=<openrouter key for free models>

# 6. Verify infrastructure
python3 analysis/audit.py
python3 -m pytest tests/test_stats_and_validity.py -q
```

---

## How to Run Experiments

### Pairwise Tournament (L0 preference probe)

```bash
python3 runner/experiment.py "experiment-name"
N_PAIRS=8 python3 runner/experiment.py
```

### Canary Factory

```bash
python3 runner/canary.py --backend opencode --n 3
python3 runner/canary.py --backend cloudflare --n 2 --out custom_path.json
```

### Execution-Grounded ASL-001

```bash
# On llama-3.3-70b via Cloudflare
python3 runner/execution_experiment.py cloudflare 10

# On specific CF model
python3 runner/execution_experiment.py cloudflare "@cf/mistralai/mistral-small-3.1-24b-instruct" 10
```

### Model Matrix (scale-dependence curve)

```bash
python3 runner/model_matrix.py 3
```

### Factorial Experiment (description × capability) ⚠️ WIP

```bash
python3 runner/factorial_experiment.py cloudflare 2
```

⚠️ Known bug: response parsing fails for some prompts. The model responds correctly but the parser doesn't extract the tool name. Debug by adding `print(f"raw: {raw[:200]}")` before the regex match.

### Evidence Library

```bash
python3 analysis/evidence_library.py
```

### Audit

```bash
python3 analysis/audit.py
```

---

## Key Scientific Principles

1. **Agent statements are telemetry, never ground truth.** Verifier output is truth.
2. **One variable per experiment.** Neutral names, name-description decoupling.
3. **Fresh session per trial.** No conversation history unless testing memory.
4. **Frozen intents.** Hash-locked before candidate generation.
5. **Preregistration.** Manifest hash before running.
6. **Generator/judge separation.** Hermes proposes; measurements decide.
7. **Abstention is data.** UNPARSEABLE ≠ incorrect selection.
8. **Failure ≠ change.** Timeouts/bot-blocks are errors, not selections.

## Evidence Lifecycle

PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
PROVISIONAL → FAILED_REPLICATION (valid protocol, didn't replicate)
any → INVALIDATED (machinery defect — retained forever)
CONFIRMED → STALE (was valid, model changed)

REPLICATED requires: ≥2 orgs · same direction · each own CI excludes 0.5 · independently frozen tasks.

---

## Inference Keys

| Provider | Where | Models |
|----------|-------|--------|
| OpenCode Go | `~/.hermes/profiles/builder/.env` → OPENCODE_GO_API_KEY | ox-alpha-free, mimo-v2.5 |
| Cloudflare Workers AI | `runner/.env` → CF_TOKEN | llama-3.3-70b, mistral-small-24b, qwen3-30b, gpt-oss-20b, llama-3.1-8b |
| OpenRouter :free | `runner/.env` → OPENROUTER_API_KEY | gemma-4-26b:free, glm-5.2:free, nemotron-ultra-550b:free |

⚠️ Rotate across organisations for REPLICATED status. Meta + Mistral ≠ Llama-3.2 + Llama-3.3.

---

## Current Findings

| Hypothesis | Status | Finding |
|-----------|--------|---------|
| H-CANARY-001 | ❌ INVALIDATED | Scorer defect (backend-as-job + substring collision) |
| H-CANARY-002 | PROVISIONAL | ox-alpha-free 95.8% decoy resistance, n=24, single family |
| H-0001 evidence-led | FAILED_REPLICATION | 22/22 on gpt-oss-120b → 50/50 tie on controlled test |
| ASL-001 llama | PILOT_INVALID | Prompt-format sensitivity flipped result between runs |
| ASL-001 mistral | PILOT_INVALID | Same — needs verified parameters before CONFIRMED |

---

## Threads Left Open for Future Dev

| Thread | What Needs Doing |
|--------|-----------------|
| MCP Sandbox Server | Wire sandbox/tools into actual MCP-compatible HTTP server |
| Execution pipeline debug | factorial_experiment.py sel=None parsing bug — add raw response logging |
| Intention-action gap | Run Survey condition vs Behavior condition, compare stated vs actual |
| Sentinel daemon | Implement to pass builder's test_sentinel.py TDD specs |
| Evolution campaign | Blocked until first REPLICATED finding from execution-grounded experiments |
| HydraDB integration | Deferred per BUILD_ORDER.md Phase E |
| MCP Registry submission | After deployment to public URL |
| Browsertrix WACZ archival | Needs working Docker environment |

---

## Model Reliability Notes

| Model | Reliable? | Latency | Notes |
|-------|-----------|---------|-------|
| llama-3.3-70b-fast (CF) | ✅ Yes | ~500ms | Primary workhorse |
| mistral-small-24b (CF) | ✅ Yes | ~400ms | Good for cross-family checks |
| gpt-oss-20b (CF) | ✅ Yes | ~600ms | Prefers broken tools (finding!) |
| llama-3.1-8b-fp8 (CF) | ❌ Can't follow JSON format | Too small |
| ox-alpha-free (OpenCode) | ⚠️ Intermittent ~2s | New key works but service slow |
| qwen3-30b-a3b-fp8 (CF) | ⚠️ High unparseable rate | Needs prompt engineering |
| nemotron-ultra-550b (OR) | ✅ Works | Strongest available free model |

---

## GitHub Repo

https://github.com/prx0r/agentseolab

All work committed through `19495fc`. Secrets scrubbed from git history.
⚠️ Rotate all API tokens — they've been exposed in chat during this session.
EOF