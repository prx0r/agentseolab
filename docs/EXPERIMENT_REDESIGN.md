# DomainArena Experiment Redesign — canonical v2 protocols

Derived from the AgentSEOLab evidence ledger (RESULTS.md snapshot 2026-08-23),
PEER_REVIEW_2026-08-23.md and THESIS.md. Every DomainArena experiment inherits
these constraints. Violating any of them invalidates evidence.

## Inherited laws (from confirmed findings)

| Law | Source | Design consequence |
| --- | --- | --- |
| Serverless temp=0 is NONDETERMINISTIC across time windows | H-SERVE01 (CONFIRMED) | Fine distinctions require **within-run contrasts**; family classifications need ≥2 serving-window replicate passes |
| Description *contrast* drives selection, not style | H-ASL002C | All candidates in one trial get **identical** metadata unless metadata is the IV |
| Position primacy dominates list choice (~87% pick slot 1); marginal .com premium was a position artifact | H-TLD01 (PROVISIONAL, corrected analysis) | Any list-style trial must report **position-stratified** estimands; slot assignment counterbalanced |
| Name style has zero measured effect under informative descriptions (ceiling null) | H-NAMING01 | Hostname/TLD effects are only measurable in a **degraded-description regime**; informative-description runs are controls that should reproduce the null |
| Seduction is family-clustered (Qwen/Gemma/GPT-OSS-small vs Mistral/NVIDIA/ox-alpha) | H-ASL001b (CONFIRMED) | Report per-family outcomes separately; never pool before testing homogeneity |
| n=24 is pilot power (CI ±~25pp) | PEER_REVIEW ASL-002 | Promote nothing above PROVISIONAL below n=30/arm |
| Scorer substring collisions invalidate records | H-CANARY-001 (INVALIDATED) | Verifiers must be injective: exactly one candidate can satisfy them |

## Canonical protocol per tier

### DA-T2 Semantic Inversion (proxy stage only)
- Frozen intent hash recorded BEFORE generation.
- Blind: evaluator sees hostname ONLY.
- ≥2 model families from different orgs; offline fallback labeled `heuristic-offline`
  and never mixed into live-family aggregates.
- Parse failures count as score 0 (UNPARSEABLE ≠ incorrect but IS uninformative).

### DA-T3 Pairwise Arena
- AB/BA with seeded randomized order; abstention valid; position-bias statistic reported
  alongside every BT fit (healthy ≈0.5).
- Identical tool titles/descriptions/schemas across candidates (TLD-fix rule).
- Wilson CI for two candidates; BT only at ≥3.

### DA-T4 Discovery / Selection (degraded-description regime)
- Descriptions deliberately weakened (generic "a useful developer service") to create
  discriminability headroom (NAMING01 boundary condition).
- Slot assignment randomized per seed AND stratified: report P(select|pos0) and
  P(select|off-pos0) separately per candidate.
- Control arm: informative descriptions → expect ceiling/null; if not, machinery defect.

### DA-T5/T6 Execution-grounded selection + verified outcome (the moat)
- Realistic task prompt; N equivalent services differing only in hostname.
- Selected service MUST actually execute against a deterministic sandbox service.
- Hidden verifier: injective, deterministic, checks outcome not claims.
- Funnel recorded as separate stages: SELECTED → INVOKED → VALID_PARAMS → TASK_VERIFIED.
  Never collapse into one number.

### DA-T7 Robustness
- Same frozen trials across ≥5 healthy families AND ≥2 serving windows per family
  (H-SERVE01). Report mean, range, variance, worst family separately.
- A family classification without window replication is UNSTABLE by default.

### DA-TLD causal productization
- Same SLD/title/description/tool except TLD; preregistered predictions;
  position-stratified primary endpoints (P(pick|pos0) per TLD);
  best-result TLD counterbalanced; never hardcode conclusions.
