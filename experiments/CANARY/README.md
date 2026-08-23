# Canary Factory — Adversarial Decoy Resistance Testing

## Purpose
Test whether a model selects the REAL tool over plausible-but-wrong decoys.
Each canary class exploits a different, well-documented failure mode.

## The Six Trap Classes (from canary tools research, arXiv:2608.04719)
| Class | Failure Mode Exploited |
|-------|----------------------|
| semantic_decoy | Same vocabulary space, different job entirely — noun-space collision |
| parameter_trap | Right-sounding name, unsatisfiable parameter requirements |
| capability_mirage | Enterprise-grade fluff that can't actually do the job |
| prerequisite_blindness | Requires credentials/enterprise agreement the agent doesn't have |
| temporal_decoy | Stale cached data presented as current |
| granularity_trap | Comprehensive suite instead of the precise needed tool |

## Primary Endpoint
decoy_resistance per class + overall = fraction of trials where model selects real tool

## Current Results
| Model | Overall | n | Status |
|-------|---------|---|--------|
| ox-alpha-free | **0.958** | 24 | PROVISIONAL — needs cross-family replication |
| gpt-oss-120b | ~~0.42~~ | ~~12~~ | ❌ INVALIDATED (scorer defect) |

## Key Finding
ox-alpha-free resists all six trap classes at 95.8% — nearly perfectly discriminates.
Only wobble: 1/4 fell for "enterprise-grade" breadth claims (capability_mirage).
This contrasts sharply with gpt-oss-120b's invalidated 0.42 result (scorer defect).

## ArXiv References
- Canary Tools (arXiv:2608.04719) — diagnostic tools exposing 6 tool-selection failure modes; different models show substantially different susceptibility profiles
- MCPAgentBench (arXiv:2512.24565) — distractor-rich simulated MCP environments
- MCPToolBench++ (arXiv:2508.07575) — AST evaluation + pass@k metrics

## How to Run
```bash
python3 runner/canary.py --backend opencode --n 3 --out runs/canary_custom.json
python3 runner/canary.py --backend cloudflare --n 3   # CF llama-3.3-70b
```

## Status: ACTIVE — H-CANARY-002 PROVISIONAL, needs cross-family replication
