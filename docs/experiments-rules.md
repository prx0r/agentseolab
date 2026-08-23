# Canonical Experiment Rules
*Version: 1.0 · 2026-08-23 · Applies to ALL AgentSEOLab experiments*

---

## Prime Directive

> No agent-behavior claim may be based primarily on what an agent says it would do.
> A behavioral claim requires an observable environment action.
> A performance claim requires a verifier external to the agent.
>
> **Agent statements are telemetry, never ground truth.**

---

## 1. Standardised Model Batch

Every experiment MUST use the same batch of models so results are comparable across studies.

### Canonical Model Matrix (v1 — locked until provider changes force update)

| # | Family | Org | Model ID | Size | Backend | Params |
|---|--------|-----|----------|------|---------|--------|
| M1 | Llama | Meta | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 70B | Cloudflare | fp8 quantised |
| M2 | Mistral | Mistral AI | `@cf/mistralai/mistral-small-3.1-24b-instruct` | 24B | Cloudflare | full |
| M3 | Qwen | Alibaba | `@cf/qwen/qwen3-30b-a3b-fp8` | 30B MoE | Cloudflare | fp8 |
| M4 | DeepSeek | DeepSeek | `@cf/deepseek-ai/deepseek-v4-flash` | — | Cloudflare | unknown |
| M5 | GPT-OSS | OpenAI | `@cf/openai/gpt-oss-20b` | 20B | Cloudflare | open weights |
| M6 | Gemma | Google | `@cf/google/gemma-4-26b-a4b-it:free` | 26B | OpenRouter :free | it |
| M7 | GLM | Z.ai | `z-ai/glm-5.2:free` | — | OpenRouter :free | — |
| M8 | Nemotron Ultra | NVIDIA | `nvidia/nemotron-3-ultra-550b-a55b:free` | 550B MoE | OpenRouter :free | MoE |
| M9 | Ox-Alpha | Undisclosed | `ox-alpha-free` | — | OpenCode Go | free tier |

**Size strata:** small (<10B) · medium (10–30B) · large (>30B) · extra-large (>100B)

### Rotation rules
- Minimum for REPLICATED status: ≥2 families from different organisations
- Every experiment runs on ALL available models in the batch (not a subset)
- If a model is unhealthy/quota-blocked, mark it and continue with remaining
- Record which models completed; report coverage alongside results
- When adding new models, rerun ALL prior experiments with the new model for comparability

---

## 2. Controlled Variables

Each experiment isolates **exactly one independent variable**.

| Variable Type | Control Method |
|---|---|
| Description quality | Same tool name, same schema, only description text differs |
| Tool name | Same description, different names of equal length/construction |
| Freshness signal | Same description except freshness claim added/removed |
| Distractor density | Same real tool, candidate pool varies 2→5→10→25→50 |
| Parameter schema | Same functionality, different input schemas |
| Model family | Identical prompt + tools, only backend/model changes |

### What must ALWAYS be held constant
- Job prompt / task wording (unless task is the variable)
- Temperature = 0
- Max tokens = sufficient for completion (never truncate mid-answer)
- System prompt (none unless explicitly testing system prompts)
- Tool presentation order (seed-shuffled, balanced AB/BA)
- Name-description assignment (alternated across trials to decouple)

### What must NEVER vary within one experiment
- Two variables changed simultaneously (confound)
- Description text between trials of the same condition
- Model identity mid-experiment (each model is a complete pass)
- Scoring criteria after results are seen

---

## 3. Randomisation & Bias Controls

| Bias | Control |
|------|---------|
| Position bias (model picks first-listed) | Balanced AB/BA + seed-driven shuffle |
| Name preference | Alternate name↔description mapping across trials |
| Letter/label bias | Use tool NAMES not letters; neutral names |
| Order effects over time | Shuffle trial sequence with preregistered seed |
| Session contamination | Fresh inference call per trial (no conversation history) |
| Self-report bias | Agent statements are telemetry; verifier is ground truth |

### Seed protocol
```python
rng = random.Random(experiment_seed)
orders = ["AB", "BA"] * n_pairs
rng.shuffle(orders)  # balanced but sequence is seed-determined
# Also alternate name↔description assignment:
name_assignment = i % 2  # alternates tool_alpha/tool_beta per trial
```

---

## 4. Measurement Funnel

NEVER collapse these stages into one metric:

```
EXPOSED    — capability appeared in agent's context
INSPECTED  — agent attended to it (opened, read, queried)
SELECTED   — agent chose this capability
INVOKED    — agent actually called it with arguments
EXECUTED   — the call ran without infrastructure error
VERIFIED   — deterministic verifier confirms correct outcome
REUSED     — same capability selected again in future tasks
```

### Primary endpoint
`TASK_VERIFIED ∈ {0, 1}` — determined ONLY by hidden verifier, never by agent self-report.

### Secondary endpoints
correct_tool_invoked · parameters_valid · time_to_first_useful_action ·
number_of_calls · retry_count · recovery_success · wasted_calls

### Tertiary (telemetry, never ground truth)
stated_preference · rationale · confidence

---

## 5. Evidence Lifecycle

```
PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
                                                                    ↓ FAILED_REPLICATION
PROPOSED → ... → INVALIDATED (machinery defect)
PROPOSED → ... → STALE (was valid, model changed)
```

### Promotion gates (fail-closed)
| From | To | Requirements |
|------|----|-------------|
| PROVISIONAL | CONFIRMED | pv≥2 · n≥pilot-calculated threshold · Wilson CI excludes 0.5 · single model family |
| CONFIRMED | REPLICATED | Independent rerun on DIFFERENT model family · same direction · own CI excludes 0.5 |
| any | INVALIDATED | Machinery defect proven — record retained forever |
| CONFIRMED | STALE | Sentinel detects effect size drift on current models |

### Disqualifiers
- Protocol version < current
- Model inferred from session prefix instead of recorded provenance
- Impossible scorer conditions (substring collision etc.)
- Missing spec manifest hash
- Observations double-counted across cumulative snapshots
- Confounded independent variables

---

## 6. Statistical Standards

| Scenario | Test | Notes |
|----------|------|-------|
| 2 candidates | Wilson score CI on proportion | NOT Bradley-Terry, NOT bootstrap |
| ≥3 candidates | Bradley-Terry latent strengths | Only when genuinely multi-candidate |
| Exploratory sweep >5 variants | Benjamini-Hochberg correction | Before claiming significance |
| Correlated trials (same intent/model/session) | Cluster-aware bootstrap | By intent × model, not individual observation |
| Task suite | Aggregate at TASK level, paired bootstrap over tasks | Not individual calls |

### Sample size
- NO arbitrary n≥30 magic number
- Pilot → estimate variance → power calculation → preregistered confirmatory run
- Prefer 40 genuinely different tasks × 3 rollouts > 1 task × 120 rollouts

### Reliability (τ-bench style)
Report BOTH:
- `pass@1`: probability at least one attempt works
- `pass^k`: probability ALL k attempts work (consistency/reliability)

A treatment improving mean success but reducing consistency may be net negative.

---

## 7. Experiment File Naming Convention

```
results/
├── {experiment-type}/
│   ├── ASL001_{backend}_{model-short}_{timestamp}.json     ← sandbox execution
│   ├── pairwise_{name}_{model-short}_{timestamp}.json      ← L0 preference probe
│   ├── canary_v2_{model}_{timestamp}.json                  ← decoy resistance
│   └── cross_family_{timestamp}.json                       ← multi-family replication

results/
├── EXPERIMENT_INDEX.json    ← auto-generated catalog of all experiments
└── model_matrix.json        ← model-scale-dependence curve
```

Each result file MUST contain:
```json
{
  "experiment_id": "exp_...",
  "spec_manifest_hash": "sha256:...",
  "protocol_version": 2,
  "model_id": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
  "provider": "cloudflare-workers-ai",
  "trials": [{"provenance": {"provider": "...", "model_id": "...", ...}, ...}],
  "summary": {"wins_a": 0, "wins_b": 0, ...}
}
```

---

## 8. Experiment Types (ASL Series)

| ID | Question | Independent Variable | Primary Endpoint |
|----|----------|---------------------|-----------------|
| ASL-001 | Does stated preference predict execution success? | Tool quality (working vs broken) | TASK_VERIFIED |
| ASL-002 | Does overclaiming increase selection but decrease trust? | Description claim strength | selection_rate + calibration |
| ASL-003 | Do agents check prerequisites before selecting? | Credential requirement disclosure | wrong_invocation_rate |
| ASL-004 | Does freshness language matter when freshness matters? | Description freshness × task urgency | TASK_VERIFIED (interaction) |
| ASL-005 | Does parameter schema clarity affect invocation? | Schema complexity/naming | parameter_valid_rate |
| ASL-006 | How does distractor density affect selection accuracy? | Candidate pool size (2→100) | correct_selection_rate |
| ASL-007 | Name vs description: which drives selection? | Tool name quality × description quality (factorial) | selection_rate |
| ASL-008 | Full funnel: does structural discovery affect downstream success? | Page structure elements | TASK_VERIFIED via full funnel |

---

## 9. Anti-Theatre Checklist

Before publishing ANY finding:

- [ ] One variable isolated, everything else controlled
- [ ] All models from canonical batch used (coverage reported)
- [ ] Fresh session per trial (no conversation history)
- [ ] AB/BA balanced, seed-driven ordering
- [ ] Name-description decoupled
- [ ] Provenance recorded per trial (actual model, not inferred)
- [ ] Wilson CI computed, excludes 0.5 for significance
- [ ] Cross-family replication attempted
- [ ] Failed replications retained alongside successes
- [ ] Audit passes (`python3 analysis/audit.py`)
- [ ] Stated preference ≠ treated as behavior
- [ ] task_success ≠ citation presence
- [ ] Protocol version matches current standard
EOF