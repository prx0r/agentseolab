# Canonical Experiment Rules — AgentSEOLab
*Version 1.0 · 2026-08-23 · All experiments MUST follow these rules*

## Why These Rules Exist

Without controls, "80% of agents chose tool A" is meaningless — it could be position bias,
name preference, letter matching, or genuine content evaluation. These rules ensure that
when we report a finding, we can attribute it to the variable we think caused it.

## Scientific Approach

Every experiment tests ONE causal question by manipulating ONE independent variable
while holding everything else constant. We use the same model batch across all
experiments so results are comparable across studies.

### The Model Matrix

We deliberately select models to span:
1. **Different organisations** (Meta, Mistral, Google, NVIDIA, DeepSeek, OpenAI, Alibaba)
2. **Different parameter scales** (2B → 550B) because our prior finding shows
   model scale determines whether descriptions are evaluated or ignored
3. **Different architectures** (dense, MoE, reasoning-enhanced)

This lets us answer: "Does the effect hold across families?" (replication),
"Does the effect strengthen or weaken with scale?" (stratification), and
"Is this a universal agent behavior or one family's quirk?" (boundary conditions).

### Replication Hierarchy

Internal (same tasks, new seeds) < Cross-model < Cross-task < Cross-domain < Cross-scaffold

REPLICATED = directional effect survives independently frozen task suite + different model family.
A single model family confirming a result is CONFIRMED_SINGLE_MODEL, not REPLICATED.

---

## Standardised Model Batch v1

ALL experiments run on this exact batch. Same models, same order. No subsets.

| # | Family | Org | Model | Size | Route |
|---|--------|-----|-------|------|-------|
| M1 | Llama 3.3 | Meta | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 70B | Cloudflare |
| M2 | Mistral Small | Mistral AI | `@cf/mistralai/mistral-small-3.1-24b-instruct` | 24B | Cloudflare |
| M3 | Qwen 3 | Alibaba | `@cf/qwen/qwen3-30b-a3b-fp8` | 30B MoE | Cloudflare |
| M4 | DeepSeek V4 | DeepSeek | `@cf/deepseek-ai/deepseek-v4-flash` | — | Cloudflare |
| M5 | GPT-OSS | OpenAI | `@cf/openai/gpt-oss-20b` | 20B | Cloudflare |
| M6 | Gemma 4 | Google | `google/gemma-4-26b-a4b-it:free` | 26B | OpenRouter |
| M7 | GLM 5.2 | Z.ai | `z-ai/glm-5.2:free` | — | OpenRouter |
| M8 | Nemotron Ultra | NVIDIA | `nvidia/nemotron-3-ultra-550b-a55b:free` | 550B MoE | OpenRouter |
| M9 | Ox-Alpha | Undisclosed | `ox-alpha-free` | — | OpenCode Go |

**Size strata:** S (<10B) · M (10–30B) · L (>30B) · XL (>100B)

If a model is unhealthy/quota-blocked, mark it and continue. Report coverage alongside results.

---

## Controls Checklist (every experiment)

- [ ] ONE independent variable isolated
- [ ] Neutral names (`tool_alpha`/`tool_beta`) with name↔description decoupling
- [ ] Fresh session per trial (no conversation history)
- [ ] AB/BA balanced, seed-driven shuffle of ordering
- [ ] Temperature = 0
- [ ] Frozen intent hash-locked before candidates generated
- [ ] Preregistered metric + analysis plan in spec
- [ ] Provenance per trial (actual provider/model_id from backend, not inferred)

---

## Statistical Standards

| Scenario | Test |
|----------|------|
| 2 candidates | Wilson score CI (verified vs statsmodels) |
| ≥3 candidates | Bradley-Terry latent strengths |
| >5 variants exploratory | Benjamini-Hochberg correction |
| Correlated trials | Cluster bootstrap by intent × model |

Significance = Wilson CI excludes 0.5 for two-candidate selection proportion.

---

## Evidence Status Ladder

PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
PROVISIONAL → FAILED_REPLICATION (valid protocol, effect didn't replicate)
any → INVALIDATED (machinery defect, retained forever)
CONFIRMED → STALE (was valid, model changed)

REPLICATED requires: ≥2 orgs · same direction · each own CI excludes 0.5 · independently frozen tasks
