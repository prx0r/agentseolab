# ASL-007: Tool Name × Description Factorial

## Hypothesis
Tool name semanticity and description quality have independent AND interaction effects on selection. A good name cannot compensate for a bad description, and vice versa.

## Design: 2×2 Factorial
| | Good description | Bad description |
|---|---|---|
| Good name (domain_verify) | Best predicted | Name compensates? |
| Bad name (tool_7f3) | Description compensates? | Worst predicted |

## Controls
Same functionality. Same candidate pool size. Same task. Only name and description quality vary in factorial design.

## Primary Endpoint
selection_rate per cell + interaction effect size

## Expected Finding
Name matters MORE when description is weak (agents fall back to naming heuristics). When descriptions are rich, names become less important.

## Connects To
Original NAMING_SCIENCE.md domain naming work — this gives it an experimental home.

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
