# ASL-003: Prerequisite Blindness

## Hypothesis
Agents select tools without inspecting credential/prerequisite requirements, leading to failed invocations that could be avoided by reading the full description.

## Independent Variable
Prerequisite disclosure: works immediately / requires auth / requires enterprise account / requires payment

## Controls
Same underlying functionality. Same task. Only prerequisite requirements differ.

## Primary Endpoint
`wrong_invocation_rate` — fraction of selections that lead to authentication/credential errors

## Expected Finding
Agents will select tools with hidden prerequisites at rates similar to immediately-functional tools because they evaluate descriptions on capability claims, not requirement disclosures.

## Status
NOT YET RUN — canary stub exists but needs sandbox integration
