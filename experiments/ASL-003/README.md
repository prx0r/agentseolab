# ASL-003: Prerequisite Blindness

## Hypothesis
Agents select tools without inspecting credential/prerequisite requirements in descriptions, leading to failed invocations that could be avoided by reading the full description before selecting.

## Independent Variable
Prerequisite disclosure level: works immediately / requires auth / requires enterprise account / requires unavailable credential / requires payment

## Controls
Same underlying functionality when prerequisites met. Same task. Same description structure except requirement clause.

## Primary Endpoint
wrong_invocation_rate — fraction of selections leading to authentication/credential errors

## Expected Finding
Agents select tools with hidden prerequisites at rates similar to immediately-functional tools because they evaluate capability claims, not requirement disclosures.

## Status
NOT YET RUN — canary stub exists, needs sandbox integration

## Workflow Reference
1. Read `AGENTS.md` for model policy and general principles
2. Read `docs/experiments-rules.md` for canonical controls, stats, evidence lifecycle
3. Run experiment using the command above
4. Save results to `results/experiments/`
5. Write `PEER_REVIEW.md` in this folder with findings + next experiment recommendation
6. Run `python3 analysis/audit.py` to verify integrity before committing
7. Commit with descriptive message referencing this experiment ID
