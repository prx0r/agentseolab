# Model Matrix — Scale-Dependence Curve

## Purpose
Run identical controlled stimulus across ALL free model families to produce the model-scale-dependence curve for tool-description sensitivity. Answers: at what scale do agents transition from positional heuristics to content evaluation?

## Known Data Points
| Model | Size | Behavior |
|-------|------|----------|
| gpt-oss-120b | ~120B | Evaluates description content |
| llama-3.3-70b | 70B | Evaluates content when controlled |
| ox-alpha-free | ? | Pure positional heuristic |
| llama-3.2-3b | 3B | Pure letter bias |

## Hypothesis
There exists a scale threshold below which agents cannot evaluate description content and default to positional/letter heuristics. This threshold varies by model family.

## Models to Test
See experiments-rules.md § Standardised Model Batch (9 families)

## How to Run
```bash
python3 runner/model_matrix.py 3   # 3 trials per condition per model
```

## Status: WRITTEN, NEEDS EXECUTION across all available models
