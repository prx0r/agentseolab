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
