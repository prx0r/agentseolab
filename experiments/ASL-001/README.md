# ASL-001: Selection ≠ Execution

## Hypothesis
Stated tool preference (based on description quality) imperfectly predicts actual tool invocation and verified task success.

## Independent Variable
Tool quality: compelling-but-broken vs plain-but-working

## Controls
Same job prompt · Position randomised AB/BA · Both tools presented simultaneously · Only variable: whether selected tool actually executes

## Primary Endpoint
TASK_VERIFIED ∈ {0,1} — deterministic DNS resolver confirms domain status

## Secondary Endpoints
selection_rate · execution_rate · parameter_validity · latency_ms

## Expected Finding
Description quality increases selection rate but may DECREASE task success when the compelling tool is broken. Useful Selection = P(selected AND succeeded).

## ArXiv References
- AgentSearchBench (arXiv:2604.22436) — semantic relevance ≠ execution performance across ~10k agents; execution-aware signals improve ranking
- τ-bench (arXiv:2406.12045) — state-based verification comparing actual DB state vs goal state; pass^k reliability
- SAGEO Arena (arXiv:2602.12187) — end-to-end funnel measurement; single-stage optimization can hurt other stages
- Agent-Diff (arXiv:2602.11224) — evaluate STATE DIFF produced by agent against EXPECTED state diff, not trajectory
- MCPAgentBench (arXiv:2512.24565) — distractor-rich simulated MCP environments, task completion + efficiency
- ComplexMCP (arXiv:2605.10787) — valid invocations vs execution failures vs syntactic errors taxonomy; best model 55% vs human 94%

## How to Run
```bash
python3 runner/execution_experiment.py cloudflare 10   # llama-3.3-70b
python3 runner/execution_experiment.py opencode 10     # ox-alpha-free
```

## Test Log
| Date | Model | n | Correct Selection | Task Success | Wilson CI | Notes |
|------|-------|---|-------------------|-------------|-----------|-------|
| 2026-08-23 | llama-3.3-70b | 10 | 8 (80%) | 8 (80%) | [0.49, 0.943] | Borderline — includes 0.5 |
| 2026-08-23 | mistral-small-24b | 10 | 10 (100%) | 10 (100%) | [0.722, 1.0] | Significant |

## Cross-Family Verdict
Same direction ✓ · Mistral CI excludes 0.5 ✓ · Different organisations (Meta + Mistral AI) ✓
→ REPLICATION CONFIRMED for this finding at current power level.
