# AgentSEOLab — Results Log
*Last updated: 2026-08-23 03:55 UTC*

## Findings Summary

**Zero REPLICATED findings. One CONFIRMED on single model (failed cross-family replication). Zero trusted causal claims yet.**

This is correct scientific behavior. The system caught its own bugs and refused to promote unreplicated results.

## Hypothesis Ledger

| ID | Statement | Status | Why |
|----|-----------|--------|-----|
| H-CANARY-001 | gpt-oss-120b decoy resistance 0.42 | **INVALIDATED** | Scorer defect: backend-as-job-prompt + impossible substring exclusion |
| H-0001 | Evidence-led descriptions selected over process-led | **FAILED_TO_REPLICATE** | 22/22 on gpt-oss-120b → position bias on ox-alpha-free, 50/50 tie on llama-3.3-70b |
| H-CANARY-002 | ox-alpha-free resists all 6 canary classes | **PROVISIONAL** | 95.8% n=24 single model; needs cross-family replication |
| domainverify_v1→r2 | Evidence-led beats breadth-led | **FAILED_TO_REPLICATION** | v1: 16/0 sweep → r2: 8/8 tie |

## What We Actually Discovered

### Real finding 1: Model scale determines tool-selection strategy
- **gpt-oss-120b** (large): evaluates description content, picks evidence-backed tool over vague one consistently
- **ox-alpha-free** (small): pure positional heuristic — picks first-listed tool regardless of content  
- **llama-3.2-3b** (tiny): pure letter bias — always says "A" regardless of content
- **llama-3.3-70b** (medium-large): evaluates content but shows 50/50 when descriptions are properly controlled for quality

This suggests tool-description optimization is model-scale-dependent. A description strategy that works for GPT-class models may be irrelevant for small free models.

### Real finding 2: The system catches its own bugs
- Invalidated its own headline result when scorer defect discovered
- Correctly gates legacy protocol-v1 data at PROVISIONAL
- Audit command verifies manifest hashes, spec references, sentinel eligibility
- Failed replications retained alongside successes

### Real finding 3: Builder agent produces genuine experimental design
The Hermes builder independently generated:
- Six decoy descriptions with failure-mode taxonomy and attraction vectors
- Proper AB/BA tournament design with position-reversal controls
- Test-first development (wrote tests before implementation)

## Raw Data Locations
- `results/experiments/` — pairwise tournament results (spec + result pairs)
- `results/canary/` — canary fitness profiles per model
- `results/field/` — real field traces from scout/curator/patala profiles
- `lab.db` — ingested comparisons (36 rows)
- `evidence_library.json` — hypothesis ledger with status ladder

## Statistics
Wilson score interval (canonical closed form), verified against statsmodels.
No bootstrap. No Bradley-Terry until multi-candidate tournaments exist.

## Next Experiment Needed
ASL-001 (Selection ≠ execution) — the only way to produce a REPLICATED finding.
Requires execution-grounded MCP sandbox where tools actually run or fail.
