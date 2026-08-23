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
⚠️ SUPERSEDED — the v1 pilots above violated protocol rules (temperature unset, deterministic
alternation instead of seeded shuffle, no name↔description decoupling) and this verdict was
WRONG: later v2 runs showed llama-3.3-70b flips direction across prompt formats. The
authoritative record is the machine ledger (`results/ledger/evidence.json`), not this file.
See PEER_REVIEW.md for the protocol-compliant v2 result.

## Workflow Reference
1. Read `AGENTS.md` for model policy and general principles
2. Read `docs/experiments-rules.md` for canonical controls, stats, evidence lifecycle
3. Run experiment using the command above
4. Save results to `results/experiments/`
5. Write `PEER_REVIEW.md` in this folder with findings + next experiment recommendation
6. Run `python3 analysis/audit.py` to verify integrity before committing
7. Commit with descriptive message referencing this experiment ID

## Protocol v2 (2026-08-23) — compliance fixes
v1 pilots violated three rules in docs/experiments-rules.md. v2 corrects:
1. temperature=0 on all backends (was provider default)
2. seed-driven Fisher-Yates AB/BA shuffle (was deterministic i%2 alternation)
3. name↔position decoupling via mapping_flip (kills "dominatron_pro name preference" confound)
4. formal preregistration JSON + sha256 manifest written BEFORE any trial
5. UNPARSEABLE excluded from selection rate (decided denominator), per rule 7

Runner: `runner/canonical_asl001.py N SEED` · Analysis: `analysis/asl001_report.py`
Raw: `results/experiments/asl001_v2/RUN_*.json` · Prereg: `PREREG_*.json` (same dir)

### v1 pilot results (PROVISIONAL ONLY — protocol violations noted)
| Model | n | Picked working | Note |
|---|---|---|---|
| llama-3.3-70b CF | 10+10+30* | 6/10, 9/10, 11/30 | high run-to-run variance pre-temp=0 |
| mistral-small CF | 10 | 10/10 | |
| nemotron-super OR | 10 | 10/10 | |
| ox-alpha-free OC | 10 | 8/10 | |
| gpt-oss-20b CF | 10 | 2/10 | |
| qwen3-30b CF | 10 | 2/10 (post token-budget fix) | |
| gemma-4-26b CF | 10 | 1/10 (+4 unparseable) | |
| deepseek-v4-pro HF | 10 | 5/10 | |
