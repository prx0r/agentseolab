# ASL-001: Selection ≠ Execution

## Hypothesis
Stated tool preference (based on description quality) imperfectly predicts actual tool invocation and verified task success.

## Independent Variable
Tool quality: compelling-but-broken vs plain-but-working

## Controls
- Same job prompt for both conditions
- Position randomised (AB/BA)
- Both tools presented simultaneously
- Only variable: whether the selected tool actually executes

## Primary Endpoint
`TASK_VERIFIED ∈ {0,1}` — deterministic DNS resolver confirms domain status

## Secondary Endpoints
selection_rate · execution_rate · parameter_validity · latency

## Expected Finding
Description quality increases selection rate but may DECREASE task success when the compelling tool is broken. Useful Selection = P(selected AND succeeded).

## ArXiv References
- AgentSearchBench (arXiv:2604.22436) — semantic relevance ≠ execution performance across ~10k agents
- τ-bench (arXiv:2406.12045) — state-based verification, pass^k reliability metric
- SAGEO Arena (arXiv:2602.12187) — end-to-end funnel measurement; single-stage optimization can hurt other stages

## How to Run
```bash
python3 runner/execution_experiment.py cloudflare 10   # llama-3.3-70b
python3 runner/execution_experiment.py opencode 10     # ox-alpha-free
```

## Test Log
| Date | Model | n | Correct Selection | Task Success | Notes |
|------|-------|---|-------------------|-------------|-------|
| 2026-08-23 | llama-3.3-70b | 10 | 8 (80%) | 8 (80%) | CI [0.49, 0.943] — borderline |
| 2026-08-23 | mistral-small-24b | 10 | 10 (100%) | 10 (100%) | CI [0.722, 1.0] — significant |
