# ASL-004: Freshness Sensitivity (Causal Interaction Design)

## Hypothesis
Explicit freshness information affects selection ONLY when the task requires current data. This is a causal INTERACTION experiment, not a main effect test.

## Design: 2×2 Factorial
| | Task needs current data | Task doesn't need current data |
|---|---|---|
| Description says "live/today" | Predicted: ↑ selection | Predicted: no effect |
| Description says "cached" | Predicted: ↓ selection | Predicted: no effect |

## Controls
Same tool functionality across all cells. Same base description structure. Only freshness claim and task urgency vary independently.

## Primary Endpoint
Interaction term: freshness_signal × task_relevance on TASK_VERIFIED

## ArXiv References
- GEO Princeton (arXiv:2311.09735) — statistics-with-sources up to +40% improvement
- SAGEO Arena (arXiv:2602.12187) — stage-specific evaluation essential

## Status
NOT YET RUN

## Workflow Reference
1. Read `AGENTS.md` for model policy and general principles
2. Read `docs/experiments-rules.md` for canonical controls, stats, evidence lifecycle
3. Run experiment using the command above
4. Save results to `results/experiments/`
5. Write `PEER_REVIEW.md` in this folder with findings + next experiment recommendation
6. Run `python3 analysis/audit.py` to verify integrity before committing
7. Commit with descriptive message referencing this experiment ID
