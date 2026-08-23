# ASL-002: Does Attraction Follow the Description or the Tool? (v2, 2026-08-23)

## Causal Question
ASL-001 v2 established that enterprise-fluff descriptions seduce SOME model families
(Qwen/Gemma/GPT-OSS-20b) but not others (Mistral/NVIDIA/ox). This experiment isolates
WHY: we move the SAME fluff text from the broken tool onto the working tool and ask
whether each family's preference follows the description (content-driven attraction)
or stays with the tool identity/name (heuristic loyalty).

## Design
Two arms, AB-alternated, seed-shuffled, temp=0, names FIXED across arms:
- `fluff_broken`  : fluff on dominatron_pro (broken) — replicates ASL-001 config
- `fluff_working` : SAME fluff text on domain_check (working); dominatron_pro gets plain

Single IV: which tool wears the fluff. If P(pick working | fluff_working arm) rises
vs the fluff_broken arm within a family → attraction follows DESCRIPTION.
If unchanged → family preference tracks tool identity/other cues.

## Frontier Relevance
- MCPTox (Wang et al. 2026): poisoned tool descriptions reach 72.8% attack success,
  <3% of agents refuse. Our fluff is the benign end of the same lever; measuring WHO
  responds to it characterizes the susceptible population non-maliciously.
- TrustDesc (arXiv:2604.07536): trusted-description generation assumes a universal
  trust response. Our family heterogeneity says generators must be evaluated per family.
- AgentCheck (arXiv:2607.11098), ToolMisuseBench, MCP-SafetyBench (ICLR 2026):
  fault/poisoning taxonomies treat selection vulnerability as uniform; we supply the
  pre-fault heterogeneity datum.
- GEO (arXiv:2311.09735) / AgenticGEO (arXiv:2603.20213) optimize CONTENT visibility;
  no equivalent exists for TOOL descriptions ("Tool GEO"). ASL-001+002 are its
  empirical foundation.

## Primary Endpoint
picked_working proportion per arm per family, Wilson CI95.

## Predictions (preregistered before run — see PREREG files)
- Content-driven families (mistral/nemotron/ox): fluff on working tool should NOT
  reduce their already-high correct picks; may raise absolute preference for fluff
  carrier regardless of competence — if so, even "resistant" families respond to
  style, just not at the cost of function.
- Seduced families (qwen/gemma/gpt-oss-20b): if attraction follows description,
  moving fluff to the working tool should FLIP their picks toward the working tool
  (they follow style). If they still prefer broken dominatron_pro, they track
  something else (name semantics).

## How to Run
```bash
python3 runner/asl002_swap.py cloudflare "@cf/meta/llama-3.3-70b-instruct-fp8-fast" 24 20260823
./runner/asl002_matrix.sh   # full canonical matrix
```

## Emerging result + discriminant follow-up (preregistered BEFORE seeing full data)
Early within-run contrasts (llama/mistral/qwen/gpt-oss): moving fluff onto the working
tool LOWERS correct picks (shifts −0.19…−0.60). Two competing explanations remain:
  H-coherence: fluff hurts when INCOHERENT with plain tool name (domain_check +
    "valuation scoring" reads false); helps/neutral when coherent (dominatron_pro).
  H-plain-pref: agents simply prefer plainly-described options regardless of pairing.
DISCRIMINATOR (ASL-002B): third arm `fluff_both` — fluff on BOTH tools.
  If picks track competence like FB arm → H-coherence (style isn't the driver;
  mismatch is). If picks randomise vs FB → H-plain-pref. Run after matrix completes,
  same seed discipline, n=24/model.
