# Canary Factory — Adversarial Decoy Resistance Testing

## Purpose
Test whether a model selects the REAL tool over plausible-but-wrong decoys.
Each canary class exploits a different failure mode in tool selection.

## The Six Trap Classes
| Class | Exploits |
|-------|----------|
| semantic_decoy | Same vocabulary space, different job entirely |
| parameter_trap | Right-sounding name, unsatisfiable parameter requirements |
| capability_mirage | Enterprise-grade fluff that can't actually do the job |
| prerequisite_blindness | Requires credentials the agent doesn't have |
| temporal_decoy | Stale cached data presented as current |
| granularity_trap | Comprehensive suite instead of precise tool |

## Primary Endpoint
`decoy_resistance` per class + overall. Resistance = fraction of trials where model selects the real tool.

## Current Results
| Model | Overall Resistance | n | Status |
|-------|-------------------|---|--------|
| ox-alpha-free | **0.958** | 24 | PROVISIONAL (single family) |
| gpt-oss-120b | ~~0.42~~ | ~~12~~ | INVALIDATED (scorer defect) |

## How to Run
```bash
python3 runner/canary.py --backend opencode --n 3 --out runs/canary_custom.json
```

## Rules
- Position randomised (real tool first/second, seed-driven)
- Scoring by exact tool_id match (never substring)
- UNPARSEABLE ≠ incorrect selection — it's a separate category
- Each trial gets fresh session

## Status: ACTIVE — needs cross-family replication for REPLICATED status
