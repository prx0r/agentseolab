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

## Workflow Reference
1. Read `AGENTS.md` for model policy and general principles
2. Read `docs/experiments-rules.md` for canonical controls, stats, evidence lifecycle
3. Run experiment using the command above
4. Save results to `results/experiments/`
5. Write `PEER_REVIEW.md` in this folder with findings + next experiment recommendation
6. Run `python3 analysis/audit.py` to verify integrity before committing
7. Commit with descriptive message referencing this experiment ID
