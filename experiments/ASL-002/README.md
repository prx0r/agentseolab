# ASL-002: Description Overclaim Penalty

## Hypothesis
Overclaiming in tool descriptions increases selection but decreases calibrated trust after execution.

## Independent Variable
Description claim strength: precise / vague / marketing-heavy / overclaiming / explicit-limitations / evidence-backed

## Controls
Same executable behavior across ALL variants. Only description text differs. Same task. Same candidate pool size.

## Primary Endpoint
TASK_VERIFIED after selection + calibration score (stated confidence vs actual success gap)

## Design
6 description styles × same working tool × N model families × AB/BA × seed-shuffled × fresh sessions

## ArXiv References
- Style over Substance (arXiv:2307.03025) — evaluation biases from style differences
- AgentSearchBench (arXiv:2604.22436) — semantic relevance diverges from execution performance
- Verbosity bias literature — longer/more detailed responses rated higher regardless of correctness

## Status
NOT YET RUN — requires MCP sandbox completion first
