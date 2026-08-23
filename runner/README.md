# Runner — experiment machinery

## Active entry points
| File | Purpose |
|---|---|
| `execution_experiment.py` | ASL-001 v2 single-model run (preregisters, temp=0, seeded AB/BA, name-decoupling) |
| `canonical_asl001.py` | ASL-001 v2 full canonical matrix (7 families) |
| `asl002_swap.py` + `asl002_matrix.sh` | ASL-002 fluff-swap causality |
| `qlex.py` | Agent Query Lexicon harvester (elicited + Moltbook sample) |
| `sentinel_rerun.py` | daily drift probe (cron 04:17) |
| `backends.py` | provider adapters (CF chat+instruct formats, temp=0) |
| `canary.py` | decoy factory v2 |
| `experiment.py`, `validator.py`, `provenance.py`, `opencode_direct.py` | shared infra |

## Archive
- `field/` — L3/L4 field harnesses, episode runners, superseded v1 batch scripts (kept for provenance)
- `../analysis/_legacy/` — old sentinel

## Conventions
Every new experiment: prereg JSON before trials · temp=0 · UA header on non-CF providers ·
usage logging via providers/track_usage.py · results to results/experiments/<exp>/
