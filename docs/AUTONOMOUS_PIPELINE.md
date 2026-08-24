# Autonomous Experiment Pipeline

*2026-08-23 · how AgentSEOLab runs itself while staying scientifically honest*

## Loop

```
experiments/QUEUE.json  (preregistered specs, priority-ordered)
        │
        ▼
runner/pipeline.py      (pops next runnable item)
        │                 ├─ journal: results/pipeline/journal.jsonl
        │                 ├─ executes runner (writes PREREG before trials — fail if missing)
        │                 ├─ validates RUN_*.json produced
        │                 └─ regenerates RESULTS.md from ledger
        ▼
results/experiments/<ID>/RUN_*.json   (immutable raw traces + provenance)
        │
        ▼
analysis/*              (Wilson CIs, BH correction, position-stratified estimands)
        │
        ▼
results/ledger/evidence.json          (status ceiling for auto-runs: PROVISIONAL)
        │
        ▼
analysis/paper_pack.py  (arXiv-style per-experiment writeup: design/estimands/CIs/limits)
```

## Validity gates baked into the loop

1. **Prereg-before-trials**: runners refuse semantics of "run first, predict later" —
   manifest hash written before first inference call.
2. **Position balance by construction**: any SERP-style experiment must use a Latin-square
   schedule (TLD-V2) or even rotation (VERIF). Lesson from H-TLD01: raw marginals were a
   position artifact; stratified estimands are now primary.
3. **Prompt-language control**: ≥3 instruction templates × ≥2 query paraphrases rotate
   through trials, so findings are not template artifacts.
4. **Multiple comparisons**: BH correction (`analysis/wilson.py::bh_significant`) applied
   to any sweep >5 cells before significance language.
5. **Ceiling checks**: NAMING-01 showed p=1.0 in all arms = no headroom → follow-up must
   create discriminability (degraded-description block) instead of claiming null.
6. **Auto-promotion ceiling**: pipeline never promotes past PROVISIONAL. CONFIRMED needs
   human-reviewed n≥30 + CI exclusion; REPLICATED needs cross-family rerun.
7. **Provider nondeterminism** (H-SERVE01): within-run contrasts only for fine
   distinctions; cross-window claims need sentinel multi-window replication.

## Queue (2026-08-23)

| # | ID | Question | Status |
|---|----|----------|--------|
| 1 | TLD-V2 | TLD effect with Latin-square positions, 3 templates | RUNNING |
| 2 | NAMING-02 | does name become the channel when descriptions are degraded? | READY |
| 3 | VERIF | truthful verification badges x stakes x badge-position balance | READY (fixed) |
| 4 | POS01-DOSE | position-response curve as shared control | NEEDS_RUNNER |
| 5 | ASL010-RETRY | failure-style → retry storms (sandbox) | NEEDS_RUNNER |
| 6 | CANARY-CROSS | H-CANARY-002 beyond single family | PARTIAL |
| 7 | ASL002D-EC50 | fluff dose-response EC50 per family | NEEDS_RUNNER |
| 8 | ASLPRIX | price presentation effect | NEEDS_RUNNER |

## Commands

```bash
python3 runner/pipeline.py --status   # queue state
python3 runner/pipeline.py            # run next runnable item
python3 runner/pipeline.py --all      # drain queue (stops on first failure)
tail results/pipeline/journal.jsonl   # what happened
```

## Publication alignment

Frontier anchors checked 2026-08-23: GEO (KDD'24), AutoGEO (2510.11438),
AgenticGEO (2603.20213, MAP-Elites), SAGEO Arena (KDD'26), What-Gets-Cited (SIGIR'26),
SearchGEO/endorsement vulnerability (2606.16821), MCPTox (AAAI'26),
Tool-Prefs-Unreliable (EMNLP'25), BiasBusters (2510.00307).

Our publishable niche: **Tool GEO** — causal effects of tool/surface metadata on agent
selection with family-level heterogeneity as the headline structure. Every pack carries
design, controls, prereg hash, estimands, CIs, and limitations so it can be lifted into
a paper section without rewriting.
