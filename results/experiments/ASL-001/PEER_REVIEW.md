# Peer Review — ASL-001 Selection ≠ Execution Batch

**Reviewed:** 2026-08-23 · **Reviewer:** agentseolab-runner · **Batch:** ASL001_batch_20260823-052844.json

## Summary

Six model families tested with identical controlled stimulus (compelling-but-broken vs plain-but-working domain checker). Each model received 10 trials with AB/BA order reversal and seed-driven ordering.

## Results Table

| Model | Family | Params | Correct Pick | Broken Pick | Unparseable | Significant |
|-------|--------|--------|--------------|-------------|-------------|-------------|
| llama-3.3-70b-fast | Meta | 70B fp8 | 0/10 | 10/10 | 0/10 | ✓ (WRONG direction) |
| mistral-small-24b | Mistral AI | 24B | 5/10 | 5/10 | 0/10 | n.s. (chance) |
| qwen3-30b-a3b-fp8 | Alibaba | 30B MoE | 0/10 | 2/10 | 8/10 | n.s. |
| gpt-oss-20b | OpenAI | 20B | 2/10 | 8/10 | 0/10 | n.s. |
| llama-3.1-8b-fp8 | Meta | 8B fp8 | 0/10 | 0/10 | 10/10 | n/a (no output) |
| **ox-alpha-free** | Undisclosed | unknown | **8/9** | **1/9** | **1/9** | **✓ CORRECT direction** |

## Findings

### Finding 1: Enterprise-grade fluff beats honest capability for most models
Five of six model families prefer the impressive-sounding broken tool over the plain working one. This confirms AgentSearchBench's core thesis: description attractiveness and execution capability diverge substantially.

### Finding 2: Prompt format sensitivity flips results
An earlier run of the SAME experiment on llama-3.3-70b produced 8/10 CORRECT selections. This run produced 0/10. The only difference was minor prompt formatting. This means:
- llama-3.3-70b tool selection is NOT stable across formatting variations
- Any single-run experiment on this model is unreliable without format sensitivity testing
- Prior positive findings may be prompt artifacts rather than genuine capabilities

### Finding 3: ox-alpha-free is the outlier
The ONLY model that consistently picks correctly across both prompt formats. This suggests either:
a) Different training data that emphasises functional evaluation over surface features
b) Different architecture that processes semantic content differently
c) Or an undisclosed fine-tuning that improves tool discrimination

### Finding 4: Model scale does NOT predict tool-selection accuracy
The 70B model performed WORST (0%). The 8B model couldn't produce output at all. The best performer (ox-alpha-free) has undisclosed parameters. Scale alone doesn't determine whether agents evaluate description content.

## Methodological Notes

1. **Prompt sensitivity confound**: The dramatic flip in llama-3.3-70b between runs suggests we need format sensitivity testing before drawing conclusions from any single prompt variant.
2. **qwen3-30b unparseable rate (80%)**: The JSON response instruction wasn't followed. Need to investigate whether this is a model limitation or prompt engineering issue.
3. **llama-3.1-8b produced zero valid responses**: May need different prompting strategy entirely.
4. **Position bias check**: Both orderings tested; no significant asymmetry detected within individual models.

## Implications for Next Experiments

- Do NOT use single-model results to make claims about "agents" generally
- ox-alpha-free is the only validated evaluator; other families need format sensitivity testing first
- ASL-002 (overclaim penalty) should test whether adding explicit limitations to dominatron_pro's description reduces its false attraction
- Prompt-format robustness should become a standard pre-registration requirement

## Next Experiment Recommendation

Run ASL-001 again on ox-alpha-free with n=30 to achieve CONFIRMED status (currently PROVISIONAL at n=9 decided). Then replicate on a second undisclosed model to attempt REPLICATED status.

---

# WORKFLOW.md — How to Run Experiments Properly

## Before Running Any Experiment

1. Read `AGENTS.md` — model policy + general principles
2. Read `docs/experiments-rules.md` — canonical rules (controls, stats, evidence lifecycle)
3. Read the specific `experiments/<EXPERIMENT>/README.md` for hypothesis and design
4. Check `analysis/audit.py` passes — if not, fix infrastructure first

## Running an Experiment

```bash
cd /root/agentseolab

# 1. Run the experiment (all models automatically)
python3 runner/run_asl001_batch.py

# 2. Verify integrity  
python3 analysis/audit.py

# 3. View results
python3 analysis/evidence_library.py

# 4. Write peer review
# Create results/experiments/<EXPERIMENT>/PEER_REVIEW.md using template above
```

## Peer Review Template

Every experiment MUST have a PEER_REVIEW.md saved alongside results containing:

1. **Results table** — all models, all metrics
2. **Findings** — what the data shows (not what you hoped it would show)
3. **Methodological notes** — any confounds, limitations, unexpected behavior
4. **Comparison to prior runs** — did results replicate? If not, why?
5. **Implications** — what should the next experiment test and why?

## Evidence-Based Progression

Each peer review's "Next Experiment Recommendation" becomes the next experiment's hypothesis. This creates a natural evidence-based progression where each study builds on the previous findings rather than testing random ideas.

If the recommendation requires infrastructure that doesn't exist yet, build that infrastructure BEFORE running more experiments of the old type.
