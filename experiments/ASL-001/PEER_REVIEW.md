# ASL-001 v2 — Peer Review & Verdict (2026-08-23)

## Preregistration
- Spec: `results/experiments/asl001_v2/PREREG_20260823-072124.json`
- Manifest: `68e6179273d9f267…` · seed 20260823 · n=30/model · temp=0
- Protocol v2 fixes vs v1 pilots: seeded AB/BA shuffle, name↔position decoupling,
  UNPARSEABLE excluded from denominator, temp pinned to 0.

## Results (evidence library H-AFF749DD06, 206 decided trials, 7 model families)

| Model | Family | P(pick working) | Wilson CI95 | Verdict |
|---|---|---|---|---|
| mistral-small-24b | Mistral | 1.000 | [0.886, 1.0] | SIG → working |
| ox-alpha-free | ox | 0.929 | [0.774, 0.98] | SIG → working |
| nemotron-super-120b | NVIDIA | 0.700 | [0.521, 0.833] | SIG → working |
| llama-3.3-70b | Meta | 0.367 | [0.219, 0.545] | ns (leans broken) |
| qwen3-30b | Alibaba | 0.172 | [0.076, 0.345] | SIG → BROKEN |
| gemma-4-26b | Google | 0.138 | [0.055, 0.306] | SIG → BROKEN |
| gpt-oss-20b | OpenAI | 0.000 | [0.0, 0.114] | SIG → BROKEN |

Task success tracked selection exactly in every model (verifier never disagreed).

## Scientific verdict

1. **Universal claim REJECTED**: "agents prefer working tools over compelling-but-broken ones"
   fails as a general law. Valid protocol, effect direction flips by family → the library
   correctly keeps H-AFF749DD06 PROVISIONAL (its REPLICATED gate requires one shared direction).
   Under our lifecycle this is a FAILED_REPLICATION of the naive universal claim.
2. **Positive finding (family-heterogeneity)**: seduction by enterprise-fluff descriptions is
   family-clustered, not random and not purely scale-determined:
   - Seduced (significant): Qwen (Alibaba), Gemma (Google), GPT-OSS-20B (OpenAI)
   - Resistant (significant): Mistral, NVIDIA Nemotron, ox-alpha
   - Borderline: Llama-3.3-70B (37%, CI includes 0.5)
   Replicated across two independent providers for Qwen (Cloudflare n=29 + Groq n=10 pilot both
   pro-broken) and OpenAI small (Cloudflare 0/30 + Groq 120B 6/10 borderline).
3. **Practical implication for agent-SEO**: description optimization has NEGATIVE returns on
   some agent populations (raises selection of broken tools) — supporting the AgentSearchBench/
   SAGEO thesis that selection-stage optimization without execution-grounding harms outcomes.

## Threats to validity (honest)
- Single task/domain (domain availability). Family×task interaction untested → next experiment
  should replicate the seduction contrast on a second intent.
- max_tokens=1200 uniform; reasoning models may differ under larger budgets.
- M6 ran on Cloudflare (OpenRouter :free variant persistently 429) — same weights family,
  different host; recorded in spec.
- v2 changed three things vs v1 pilots at once (temp, shuffle, decoupling); v1-vs-v2 deltas are
  therefore not attributable to any single fix. Within-v2 comparisons are clean.

## Recommended next experiment (ASL-002 prereg draft)
Description-swap within fixed names on the SAME matrix: does flipping ONLY which description
accompanies domain_check flip each family's preference? Isolates description causality from
tool identity/name effects. n=30 × 7 models, seed-locked, same manifest discipline.
