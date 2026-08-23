# Model Matrix — Scale-Dependence Curve

## Purpose
Run the same controlled stimulus across ALL free model families simultaneously to produce the model-scale-dependence curve for tool-description sensitivity.

## Key Question
At what model scale do agents transition from positional heuristics to content evaluation?

## Known So Far
- gpt-oss-120b: evaluates description content
- llama-3.3-70b: evaluates content when descriptions are properly controlled
- ox-alpha-free: pure positional heuristic
- llama-3.2-3b: pure letter bias

## How to Run
```bash
python3 runner/model_matrix.py 3   # 3 trials per condition per model
```

## Output
results/model_matrix.json — table showing evidence/process preference per model + Wilson CI

## Status: WRITTEN, NEEDS EXECUTION across all 7 CF models + OpenRouter free models
