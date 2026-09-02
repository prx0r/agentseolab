# AgentSEOLab — role, gaps, and the Hermes operating plan
(2026-08-23 · saved verbatim from strategy review)

> **Cogym continuously evolves cognition. AgentSEOLab continuously discovers the changing rules by which agents discover, choose, cite, and invoke things.**

Black-box, stochastic, constantly drifting environment → ideal for near-unlimited Hermes compute. August results may stop holding when the model/search stack changes.

## What it is today
Intended scientific object:
SiteIntent → agent/search environment → trace → query → retrieval → open → citation → selection → invocation → task success.
README already distinguishes field vs lab trials and requires frozen intents, generator/judge separation, randomized order, reversed pairs, fresh sessions, immutable observations. SCIENTIFIC_METHOD correctly rejects one universal score — per-experiment estimands, Bradley–Terry/Plackett–Luce, holdouts, bootstrap uncertainty, hypothesis evidence library. July 2026 GEO survey supports: generic rules transfer poorly; no stable longitudinal cross-platform effects yet.

## Implementation gaps (attack first)
| Gap | Why it matters |
|---|---|
| No test directory | don't unleash autonomous mutation |
| No experiment runner | records results, doesn't produce them |
| No Bradley–Terry/bootstrap | science claims unimplemented |
| No field-search harness | best evidence tier is manual |
| No holdout manager | unlimited compute would overfit |
| No candidate evolution loop | evolution only documented |
| No controlled sandbox | can't isolate variables |
| No sentinel/drift runner | can't detect behavior change |

Correctness bugs: RecordExplanation never INSERTs; insert_field_trial doesn't populate search_queries; README commands mismatch CLI; **canonical_hash() not canonical** (HashMap ordering) → use RFC 8785/JCS or recursive key sort before trusting intent_hash. FreeAI adapter (hardcoded CF models, tokens_used:0) should be replaced by provider-neutral runner; Hermes/OpenCode-Go becomes a backend. Hydra premature in hot path (string-interpolated Cypher) — SQLite/Parquet = experimental truth; Hydra only relationships later.

## Frontier directions
1. **End-to-end GEO** (SAGEO Arena): interventions need full vector — search activation, retrieval@k, open, citation, accurate-use, tool-selection, invocation, task success. Not "AI liked B".
2. **Execution-grounded discovery** (AgentSearchBench, ~10k real agents): measure description→selection→execution→success. Misleading description raising selection but lowering success = negative optimization.
3. **Canary tools** (6 failure classes: semantic decoy, parameter trap, capability mirage, prerequisite blindness, temporal decoy, granularity trap): ask which descriptions attract agents *for the right reasons* under plausible-wrong competitors. Output: Tool Description Fitness (correct_selection, decoy_resistance, task_success, parameter_success).
4. **Evolutionary GEO** (AgenticGEO): MAP-Elites strategy archive + co-evolving critic, content-conditioned selection. Study architecture, don't import.

## Hermes' role: workforce, NOT judge
Hermes generates hypotheses/variants/red-team; authority stays measured behavior. Pipeline: HERMES(hypotheses+variants+redteam) → EXPERIMENT SPECS → RUNNER(fresh isolated sessions) → RAW TRACES → deterministic ingest → ANALYSIS(effect+uncertainty) → EVIDENCE LIBRARY(replicated/failed).

## Five permanent boards
| Board | Continuous job |
|---|---|
| agentseo-field | observe real search/citation traces (frozen intents, fresh sessions, trace-only recording) |
| agentseo-lab | controlled one-variable experiments (hostname/title/description/path/JSON-LD/operationId/MCP name+desc/params/freshness/price/provenance/llms.txt/sitemap) |
| agentseo-redteam | generate decoys/canaries/hard negatives per capability |
| agentseo-evolution | V0→32 variants→12 lab→5 canary→2 intent-holdout→winner/no-promo; MAP-Elites elites kept per metric |
| agentseo-replication | sentinel replays of accepted findings; effect drift → STALE/FAILED status |

## Compute funnel
L0 synthetic pairwise (100k+) → L1 simulated SERP/MCP env (10k+) → L2 controlled browser/search field (1000s) → L3 real deployed variants (dozens) → L4 real outcomes (scarce, strongest). Big compute at L0/L1; verification at L2-L4.

## Never: Mimo both scientist and ground truth
Mimo for hypothesis discovery, variant generation, failure clustering, red-team, synthesis, challengers. Outcomes from recorded selections, deterministic success, real opens/citations, cross-session comparison, external model families for transfer tests.

## Analysis: Python sidecar
Rust keeps contracts/ingest/immutability/runner control. Python does Bradley-Terry, cluster bootstrap, multiple-comparison correction, effect sizes, interactions. Raw observations canonical; stats regenerable.

## Output format (eventually)
Recommendation: Change + Evidence ID (H-0041) + Effect (+11.8pp, CI) + Replicated-on models + Intents + Failed/unknown domains + Last verified date. Closed loop: AgentSEOLab discovers causal evidence → agentseo applies → finalbuilds deploys → AgentSEOLab measures downstream.

## 10-item immediate sprint
1. Scientific integrity hardening (tests, JCS hashing, schema migrations, complete inserts, fix normalization, CLI/docs match, persistence tests)
2. Experiment contract (ExperimentSpec: treatment/control, seed, preregistered metric, allowed evidence, dev/holdout, manifest hash)
3. Runner abstraction (provider-neutral clean-session; OpenCode-Go adapter; persist model/provider/version/runtime)
4. Pairwise tournament runner (randomized, AB/BA reversal, fresh sessions, abstention allowed, outcome capture)
5. Analysis sidecar (BT + cluster bootstrap + treatment-effect reports from raw trials)
6. MCP sandbox (simulated tools, hard negatives, six canary classes, deterministic task-success verifier)
7. Field runner (search-capable agents on frozen SiteIntents; ingest real traces)
8. Evolution campaign (successive-halving screens; proposer workers cannot access holdouts)
9. Evidence library (auto hypothesis records from confirmatory experiments; keep failures + replication history)
10. Sentinel daemon (replay fixed suite on model changes; open drift task on material effect change)

Then boards produce observations. NO Hydra/UI/ontology/recommender until then.

## Repos beside it (specimens only)
git clone AIcling/agentic_geo (strategy archive idea) · Bingo-W/AgentSearchBench (execution-grounded tasks) · study MCPAgentBench distractor methodology · SAGEO Arena methodology reference.

## Fit in 24/7 system
FINALBUILDS2 ("what to build") ← HERMES (parallel execution) → COGYM (cognition) + AGENTSEOLAB (discovery/selection rules) → findings feed back. Unit of output: **a replicated effect**, not pages or SEO rules.
