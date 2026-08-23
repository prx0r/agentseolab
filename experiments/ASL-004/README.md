# ASL-004: Freshness Sensitivity (Causal Interaction)

## Hypothesis
Explicit freshness information in tool descriptions affects selection ONLY when task freshness is relevant. This is a causal INTERACTION design, not a main effect test.

## Independent Variable
2×2 factorial:
- Description freshness signal: live/today vs cached/no declaration
- Task freshness relevance: current-data-required vs historical-data-sufficient

## Controls
Same tool functionality. Same base description structure. Only freshness claim and task urgency vary independently.

## Primary Endpoint
`TASK_VERIFIED` with interaction term: freshness_signal × task_relevance

## Expected Finding
Freshness language matters only when the task requires current data. When it doesn't matter, both descriptions perform equally.

## ArXiv References
- GEO Princeton (arXiv:2311.09735) — statistics-with-sources up to +40%
- SAGEO Arena (arXiv:2602.12187) — stage-specific evaluation essential

## Status
NOT YET RUN
