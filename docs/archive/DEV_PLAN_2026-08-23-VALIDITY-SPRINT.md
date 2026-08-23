# AgentSEOLab — Validity Sprint Dev Plan
**2026-08-23 · FREEZE new experiments until this sprint completes**

## Verdict
Architecture 8/10 · Anti-theatre instincts 9/10 · Machinery 7/10 · Code consistency 5/10 · **Evidence quality 2/10** (correctly self-invalidated; zero trusted findings > fake confidence)

## Identity reframe
AgentSEOLab experimentally discovers causal rules governing how autonomous agents **discover, evaluate, select, invoke, trust and reuse** machine-readable capabilities. Not "AI SEO."

## Core research object
INTENT → SEARCH ACTIVATION → QUERY → RETRIEVAL → EXPOSURE → OPEN → TOOL SELECTION → PARAMETER CONSTRUCTION → EXECUTION → TASK SUCCESS → CITATION/REUSE

## P0 Bugs (fix before any compute on findings)
1. Evidence library reads `trial.model_id` but runner nests under `trial.provenance.model_id`
2. Hypothesis identity hashes description text (60 chars) — should hash causal question + intent family + intervention dimension + control + metric + protocol version
3. Replication records store cumulative snapshots → double-counting on multi-update
4. Same-direction replication not enforced (Model A 90% + Model B 10% both pass CI≠0.5)
5. Seed unused for ordering (deterministic AB/BA pattern, no randomization)
6. Sentinel freezes INVALIDATED H-CANARY-001 as drift baseline; imports old canary API (REAL/CANARIES/PROMPT gone)
7. Backend selection allows unknown names → silent fallback identity contamination
8. Field task_success conflates "cited a URL" with "task succeeded"
9. Search-result exposure collapsed into citation events

## Phase A — integrity sprint (12 items, ~1 day)
Fix all 12 above. Add `agentseolab audit` command verifying:
- all evidence references existing runs
- all runs reference frozen specs
- manifest hashes recompute
- trial provenance validates
- no invalidated finding sentinel-active
- no double-counted observations
- no CONFIRMED lacking n/CI
- no REPLICATED lacking independent model/run

## Event ontology (never collapse)
SEARCH_RESULT_EXPOSED / OPENED / SOURCE_READ / USED / CITED /
CAPABILITY_SELECTED / INVOKED / EXECUTION_SUCCEEDED / TASK_VERIFIED

## Field schema change
final_answer_present, citation_present, candidate_selected, tool_invoked,
execution_completed, output_valid, **task_success_verified=UNKNOWN** unless deterministic verifier exists

## Phase B — canonical ontology
Every study manipulates ONE dimension. Experiment = {hypothesis, intervention_dimension, treatment, control, intent_set, candidate_pool, model_family, preregistered_metric, analysis_plan, holdout_policy}

## Phase C — first real experiments
ASL-001 Selection ≠ execution (compelling-but-broken vs plain-but-working)
ASL-002 Overclaim penalty
ASL-003 Prerequisite blindness
ASL-004 Freshness sensitivity (causal interaction design)
ASL-005 Parameter-schema fitness
ASL-006 Distractor density
ASL-007 Name × description factorial
ASL-008 Structural discovery (full funnel)

## Evolution objective (NOT maximize selection)
Tool Description Fitness = correct_selection × execution_success × prerequisite_awareness × parameter_success × calibration − wasted_calls − misleading_selection
MAP-Elites niches per metric dimension.
