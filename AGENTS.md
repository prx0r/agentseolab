# AgentSEOLab — Canonical Experiment Principles

## Model Policy

### The Rule
**Cheapest model that can do the job. Always. Rotate across families for scientific validity.**

Owner is broke. Never spend money on inference. Every experiment MUST use free-tier models.

### Approved Free Models (Cloudflare Workers AI — daily neuron allocation)

| Tier | Model | Size | Use For |
|------|-------|------|---------|
| Strong | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 70B | Primary experiment subject |
| Strong | `@cf/mistralai/mistral-small-3.1-24b-instruct` | 24B | Cross-family replication |
| Strong | `@cf/qwen/qwen3-30b-a3b-fp8` | 30B MoE | Cross-family replication |
| Strong | `@cf/deepseek-ai/deepseek-v4-flash` | — | Reasoning-sensitive experiments |
| Medium | `@cf/openai/gpt-oss-20b` | 20B | Mid-scale comparison point |
| Fast | `@cf/meta/llama-3.1-8b-instruct-fp8` | 8B | Scale-stratification data point |
| Visual | `@cf/google/gemma-4-26b-a4b-it` | 26B | Cross-family diversity |
| Code | `@cf/qwen/qwen2.5-coder-32b-instruct` | 32B | Coding-agent-specific experiments |

### OpenCode Go
- `ox-alpha-free` ONLY (weekly quota; stop and wait for reset)
- Never any other zen model under the Go key

### Forbidden
- `@cf/openai/gpt-oss-120b` (expensive neuron cost)
- OpenRouter paid models
- Any balance-drawdown API or "enable usage from balance" prompt

### Why rotation matters scientifically
Different model families have different architectures, training data, and behavioral biases. A finding replicated across llama + mistral + qwen + deepseek + ox-alpha is far stronger than one replicated on two llama variants. If a causal effect only holds on one family, that's a boundary condition, not a law.

**Minimum for REPLICATED status:** ≥2 model families from different organizations (e.g. Meta + Mistral, not Llama-3.2 + Llama-3.3).

---

## Experiment Design Principles

### 1. ONE variable at a time
Each experiment isolates exactly one independent variable (description wording, tool name, parameter schema, freshness signal). Everything else held constant. If you change two things and see an effect, you don't know which caused it.

### 2. Proper controls
- **Neutral names**: `tool_alpha`, `tool_beta` — never semantically loaded names that could confound
- **Position randomization**: seed-driven shuffle of presentation order; balanced AB/BA but sequence randomized
- **Name-description decoupling**: alternate which neutral name maps to which description across trials so name preference can't masquerade as description preference

### 3. Fresh session per trial
Every trial gets a new inference session with no conversational history. Memory off, skills off, session search off — unless those ARE the independent variable.

### 4. Frozen intents
SiteIntents are captured and hash-locked BEFORE any candidate generation. The intent is immutable experimental context.

### 5. Preregistration
ExperimentSpec declares treatment/control, metric, seed, holdout classification BEFORE running. Manifest hash makes it tamper-evident.

### 6. Generator/judge separation
Hermes generates hypotheses and variants. It NEVER judges its own candidates. Outcomes come from recorded selections, deterministic success, real traces.

### 7. Abstention allowed
Models may say "neither works." That's data, not failure. UNPARSEABLE ≠ incorrect selection.

### 8. Failure ≠ change
Timeouts, bot-blocks, empty responses are ERRORS — never counted as selections or changes.

---

## Statistical Standards

### Two-candidate experiments
Wilson score interval on the proportion. No bootstrap, no Bradley-Terry.
```
from analysis.wilson import wilson
result = wilson(wins_a, n_decided)
# result["ci95"] excludes 0.5 → significant
```

### Multi-candidate tournaments
Real Bradley-Terry with latent strengths. Only after ≥3 candidates.

### Multiple comparisons
Any exploratory sweep testing >5 variants must apply Bonferroni or Benjamini-Hochberg correction before claiming significance.

### Cluster awareness
Trials sharing intent/model/session are correlated. Bootstrap by independent unit (intent × model), not individual observation.

---

## Evidence Lifecycle

```
PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
                                                                    ↓
                                                              FAILED_REPLICATION
PROPOSED → ... → INVALIDATED (machinery defect)
PROPOSED → ... → STALE (was valid, model changed)
```

### Promotion gates (fail-closed, no manual upgrades)
- **CONFIRMED**: protocol_version ≥ 2 · n_decided ≥ 30 · Wilson CI excludes 0.5
- **REPLICATED**: CONFIRMED + independent rerun on DIFFERENT model family + same direction + its own CI excludes 0.5
- **INVALIDATED**: machinery defect — record retained forever, never deleted
- **FAILED_REPLICATION**: valid protocol, effect didn't replicate — different from INVALIDATED

### What disqualifies evidence
- Protocol version < current
- Model identity inferred from session prefix instead of recorded provenance
- Scorer conditions impossible to satisfy (e.g. substring collision between candidates)
- Missing spec manifest hash
- Observations double-counted across cumulative snapshots

---

## Measurement Ontology (never collapse these)

```
SEARCH_RESULT_EXPOSED   — URL appeared in results
SEARCH_RESULT_OPENED    — agent clicked/fetched it  
SOURCE_READ             — content extracted
SOURCE_USED             — content influenced response
SOURCE_CITED            — URL in final output
CAPABILITY_SELECTED     — tool chosen
CAPABILITY_INVOKED      — actually called
EXECUTION_SUCCEEDED     — call returned without error
TASK_VERIFIED           — deterministic verifier confirms outcome
```

Citing a URL ≠ task success. Opening a result ≠ reading it. These are separate stages.

---

## Compute Funnel

| Level | Environment | Scale | Cost |
|-------|------------|-------|------|
| L0 | Synthetic pairwise | 100K+ trials | Free (CF neurons) |
| L1 | Simulated MCP/A2A env | 10K+ trials | Free |
| L2 | Controlled execution sandbox | 1000s | Free |
| L3 | Real search/browser field run | 100s | Free |
| L4 | Real deployed capability + outcome | Scarce | Free |

Big compute at L0/L1. Verification at L2–L4. Never mix levels into one score.
EOF