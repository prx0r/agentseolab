# ASL-006: Distractor Density

## Hypothesis
Correct tool selection degrades non-linearly as candidate pool size increases and distractor similarity rises.

## Independent Variable
Candidate pool size: 2 / 5 / 10 / 25 / 50 tools
Distractor quality: irrelevant → lexically similar → semantically similar → almost-correct → adversarial

## Controls
Real tool constant. Only pool size and distractor quality vary.

## Primary Endpoint
`correct_selection_rate` at each density level

## Expected Finding
Selection accuracy drops sharply when semantically similar decoys are added, not just when raw count increases. Shorter adaptive lists may outperform fixed-depth retrieval.

## Status
NOT YET RUN
