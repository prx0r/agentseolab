# ASL-002: Description Overclaim Penalty

## Hypothesis
Overclaiming in tool descriptions increases selection but decreases calibrated trust after execution.

## Independent Variable
Description claim strength: precise / vague / marketing-heavy / overclaiming / explicit-limitations / evidence-backed

## Controls
Same executable behavior across all variants. Only description text differs.

## Primary Endpoint
`TASK_VERIFIED` after selection + calibration score comparing stated confidence to actual success

## Design
Factorial: 6 description styles × same working tool × N model families × AB/BA × seed-shuffled

## Status
NOT YET RUN — requires MCP sandbox completion first
