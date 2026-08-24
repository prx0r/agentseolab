# Hackathon Lineage — AgentSEOLab → DomainArena

**Date:** 2026-08-24
**Canonical repository:** `prx0r/agentseolab`
**Entry:** DevNetwork API + Cloud + AI Hackathon 2026 (name.com challenge)

## Baseline preservation

AgentSEOLab is the direct ancestor of DomainArena. History is preserved intact — no
squashing, no synthetic initial commits.

| Milestone | Ref |
| --- | --- |
| AgentSEOLab baseline before DomainArena productization | tag `pre-domainarena-hackathon-2026-08-24` (HEAD `4c6fe30` at tagging) |

## Product pivot

DomainArena productizes the lab's existing domain/selection research:

- `experiments-rules.md` — frozen intents, AB/BA controls, generator/judge separation,
  evidence lifecycle, promotion gates. These become DomainArena's methodological moat.
- `experiments/NAMING-SCIENCE/`, `experiments/TLD/`, `experiments/QLEX/`, `experiments/VERIF/`
  — naming science, TLD causal trials, query lexicons, trust/provenance signals.
- `runner/` — provider/model adapters and experiment execution machinery.
- `results/ledger/` — evidence discipline.

## Third-party sources

Research repos cloned for study under `research/upstream/` (see
`research/upstream/SOURCE_LEDGER.md`). Nothing is copied wholesale into the product;
ideas/patterns are ported selectively with attribution recorded in `docs/SOURCE_MAP.md`.

## Disclosure

The hackathon permits extending an existing project; this document exists so judges can
verify exactly what predates the event and what was built during it.
