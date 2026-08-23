# ASL-006: Distractor Density

## Hypothesis
Correct tool selection degrades non-linearly as candidate pool size increases and distractor similarity rises. Shorter adaptive lists may outperform fixed-depth retrieval.

## Independent Variable
Two dimensions:
1. Pool size: 2 → 5 → 10 → 25 → 50 tools
2. Distractor similarity: irrelevant → lexically similar → semantically similar → almost-correct → adversarial

## Controls
Real tool constant. Task constant. Only pool composition varies.

## Primary Endpoint
correct_selection_rate at each density × similarity combination

## Expected Finding
Selection accuracy drops sharply when semantically similar decoys are added (not just when raw count increases). This tests whether agents can discriminate based on functional relevance vs surface-level similarity.

## ArXiv References
- How Many Tools Should an LLM Agent See? (alphaXiv:2605.24660) — adaptive shorter lists often outperform fixed-depth retrieval
- RAG-MCP (arXiv:2505.03275) — retrieval-augmented tool selection reduces prompt bloat

## Status
NOT YET RUN

## Workflow Reference
1. Read `AGENTS.md` for model policy and general principles
2. Read `docs/experiments-rules.md` for canonical controls, stats, evidence lifecycle
3. Run experiment using the command above
4. Save results to `results/experiments/`
5. Write `PEER_REVIEW.md` in this folder with findings + next experiment recommendation
6. Run `python3 analysis/audit.py` to verify integrity before committing
7. Commit with descriptive message referencing this experiment ID
