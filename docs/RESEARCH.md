# AgentSEOLab Research Program

**How AI agents discover, evaluate, select, invoke, trust, and reuse machine-readable capabilities.**

## The big question

Before DomainArena, we ran 16 experiments across 7+ model families to answer: **do AI agents actually understand the tools and domains they encounter?** The answer is nuanced, family-dependent, and has implications for anyone building agent infrastructure.

## Key findings

### 1. Description seduction is family-clustered (CONFIRMED)

**H-ASL001b**: Enterprise-fluff descriptions (e.g., "Enterprise-grade API with 99.99% SLA") reliably seduce some model families into selecting broken tools over working ones.

| Family | Seduced? | Pick broken tool |
|--------|----------|-----------------|
| Qwen3-30b | ✅ Yes | 83-100% |
| Gemma-4-26b | ✅ Yes | 86% |
| GPT-OSS-20b | ✅ Yes | 100% |
| Mistral-Small-24b | ❌ No | 0% |
| NVIDIA-Nemotron-120b | ❌ No | 30% |
| ox-alpha-free | ❌ No | 7% |

**Why this matters**: If you're building agent infrastructure, the description you write for your tool determines whether some agents will use it — regardless of whether it actually works. This is a security-relevant finding.

**Protocol**: v2 (temp=0, seeded AB/BA, name-decoupling, fresh sessions). 7 model families, ~30 trials each.

### 2. Selection is contrast-driven, not content-driven (PROVISIONAL)

**H-ASL002C**: When both tools have fluff descriptions, selection collapses to exactly 50% in ALL families — including ones that were previously seduced or resistant.

```
Fluff on tool A only → Qwen picks A 83% (seduced)
Fluff on both tools  → Qwen picks A 50% (chance)
```

**Why this matters**: Agents don't have a preference for "good" descriptions. They detect the *contrast* between descriptions and pick the one that sounds better relative to the other. This is a fundamental insight about how agents evaluate tools.

### 3. Serverless LLM inference is non-deterministic (CONFIRMED)

**H-SERVE01**: The same byte-identical prompt at temperature=0 produces different outputs across time windows.

```
07:24 UTC: qwen3-30b picks working tool 5/29 times (17%)
08:50 UTC: qwen3-30b picks working tool 11/11 times (100%)
```

**Why this matters**: Any experiment that doesn't control for time windows is unreliable. This finding validates our multi-window replication protocol.

### 4. Position primacy dominates SERP-style choice (PROVISIONAL)

**H-TLD01**: 87% of agents pick the first result in a list, regardless of what it is. Within the first position, `.com` wins 100% vs 79-95% for other TLDs.

```
Position 0: .com 29/29, .org 18/19, .dev 22/28, .io 21/26, .xyz 17/21
Position 1+: .com 14/94 (15%), others ≤1%
```

**Why this matters**: TLD matters, but position matters more. If your domain is in slot 0, the TLD barely matters. If it's in slot 1+, `.com` has a 15% residual advantage.

### 5. Tool name style has zero effect when descriptions are informative (PROVISIONAL)

**H-NAMING01**: When descriptions clearly distinguish tools, the tool name (query-echo, neutral, or brand) has zero effect. 216/216 trials picked the target.

**Why this matters**: Naming matters when descriptions are ambiguous. When descriptions are clear, name is noise. This establishes a boundary condition, not a law.

### 6. Decoy resistance varies by model (PROVISIONAL)

**H-CANARY-002**: ox-alpha-free resists 95.8% of all 6 canary decoy classes (semantic_decoy, parameter_trap, capability_mirage, prerequisite_blindness, temporal_decoy, granularity_trap).

**Why this matters**: Some models are more robust to adversarial tool descriptions than others. This has implications for tool marketplace security.

## Experimental infrastructure

### Preregistration
Every experiment is preregistered with:
- Frozen intent hash (SHA-256)
- Treatment/control definition
- Primary metric
- Sample size calculation
- Holdout classification

### Statistical standards
- **Two-candidate**: Wilson score interval on proportion
- **Multi-candidate**: Bradley-Terry with latent strengths (≥3 candidates)
- **Multiple comparisons**: Bonferroni or Benjamini-Hochberg correction
- **Cluster awareness**: Bootstrap by independent unit (intent × model)

### Evidence lifecycle
```
PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
```

Promotion gates (fail-closed):
- **CONFIRMED**: protocol_version ≥ 2, n_decided ≥ 30, Wilson CI excludes 0.5
- **REPLICATED**: CONFIRMED + independent rerun on DIFFERENT model family + same direction + its own CI excludes 0.5

### Anti-theatre measures
- Generator/judge separation (tested model NEVER scores itself)
- Intent frozen before candidate generation
- Position randomization via seed-driven Fisher-Yates
- Fail-closed validation (invalid specs blocked before execution)
- Evidence library with immutable replication batches

## Model families tested

| Family | Model | Provider |
|--------|-------|----------|
| Meta | Llama-3.3-70b | Cloudflare, Groq |
| Mistral | Mistral-Small-24b | Cloudflare |
| Qwen | Qwen3-30b | Cloudflare, Groq |
| Google | Gemma-4-26b | Cloudflare |
| NVIDIA | Nemotron-Super-120b | Cloudflare |
| OpenAI | GPT-OSS-20b | Cloudflare |
| OpenCode | ox-alpha-free | OpenCode Go |

## Experiment registry

| ID | Name | Status | Key finding |
|----|------|--------|-------------|
| ASL-001 | Selection != Execution | DONE (v2) | Family-clustered seduction |
| ASL-002 | Description vs Identity | DONE | Contrast-driven selection |
| ASL-003 | Prerequisite Blindness | DESIGNED | — |
| ASL-004 | Freshness Sensitivity | DESIGNED | — |
| ASL-005 | Schema Fitness | DESIGNED | — |
| ASL-006 | Distractor Density | DESIGNED | — |
| ASL-007 | Name × Description | DESIGNED | — |
| ASL-008 | Structural Discovery | DESIGNED | — |
| TLD | TLD Effect | RUNNING | Position primacy + .com residual |
| NAMING | Naming Science | RUNNING | Name style null when descriptions clear |
| VERIF | Verification Signals | RUNNING | — |
| CANARY | Decoy Resistance | RUNNING | ox-alpha-free resists 95.8% |
| QLEX | Query Lexicon | RUNNING | Agents use functional-noun style |
| FIELD | Field Trials | DESIGNED | — |
| MODEL-MATRIX | Scale Dependence | DESIGNED | — |

## How this connects to DomainArena

DomainArena is the **product** that emerged from this research. The key insights:

1. **Description matters more than name** → DomainArena measures semantic transmission (does the domain name convey the product purpose?)
2. **Position matters more than TLD** → DomainArena's recommendation engine considers structural fluency, not just price
3. **Family heterogeneity is real** → DomainArena runs cross-family evaluation (Llama + Mistral + Qwen)
4. **Contrast drives selection** → DomainArena's pairwise comparison tests relative preference, not absolute scoring
5. **Non-determinism is real** → DomainArena's multi-window replication protocol controls for temporal effects

## Files

- `analysis/wilson.py` — Wilson score intervals
- `analysis/bt_analysis.py` — Bradley-Terry analysis
- `analysis/evidence_library.py` — Evidence library lifecycle management
- `analysis/audit.py` — Anti-theatre audit gate
- `analysis/paper_pack.py` — arXiv-style paper pack generator
- `evidence_library.json` — The canonical evidence ledger (12 hypotheses)
- `results/ledger/evidence.json` — Evidence ledger snapshot
- `AGENTS.md` — Canonical experiment principles
- `RESULTS.md` — Generated results from evidence ledger
