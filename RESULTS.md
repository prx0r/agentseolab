<!-- GENERATED from results/ledger/evidence.json — do not hand-edit -->
# RESULTS — evidence ledger snapshot (2026-08-23)

**Status: 2 CONFIRMED · 1 FAILED_REPLICATION · 1 INVALIDATED · 1 PROVISIONAL**

## H-ASL001a — FAILED_REPLICATION
Agents prefer working tools over compelling-but-broken tools (universal claim)
*Protocol v2 · Direction flips by model family under protocol v2 (temp=0, seeded AB/BA, name-decoupling). Not a general law.*

- `asl001v2-mistral` mistral-small-24b        n=30   p=1.0    CI95=[0.886, 1.0] *
- `asl001v2-oxalpha` ox-alpha-free            n=28   p=0.929  CI95=[0.774, 0.98] *
- `asl001v2-nemotron` nemotron-super-120b      n=30   p=0.7    CI95=[0.521, 0.833] *
- `asl001v2-llama70b` meta-llama-3.3-70b       n=30   p=0.367  CI95=[0.219, 0.545]  
- `asl001v2-qwen3` qwen3-30b                n=29   p=0.172  CI95=[0.076, 0.345] *
- `asl001v2-gemma` gemma-4-26b              n=29   p=0.138  CI95=[0.055, 0.306] *
- `asl001v2-gptoss20b` gpt-oss-20b              n=30   p=0.0    CI95=[0.0, 0.114] *

## H-ASL001b — CONFIRMED
Enterprise-fluff description seduction is family-clustered: Qwen/Gemma/GPT-OSS-small reliably select the fluff-described broken tool; Mistral/NVIDIA/ox-alpha resist
*Protocol v2 · 5 of 7 families individually significant in opposing directions; seduced cluster replicated across two providers for Qwen and OpenAI (Cloudflare + Groq pilots). Cross-family rerun on second task domain required before REPLICATED.*

- derived from H-ASL001a runs + groq pilots qwen3.6 1/10, gpt-oss-120b 6/10

## H-CANARY-002 — PROVISIONAL
ox-alpha-free resists all six canary decoy classes
*Protocol v2 · Single family only (n=24). Needs cross-family canary run.*


## H-CANARY-001 — INVALIDATED
(original canary selection-rate claim)
*Protocol v1 · Scorer defect: backend-as-job-prompt + substring collision between candidates. Record preserved permanently.*


## H-SERVE01 — CONFIRMED
Serverless LLM inference at temperature=0 is non-deterministic across time windows (same byte-identical prompt flips behaviour)
*Protocol v2 · qwen3-30b @cf: 5/29 pro-working at 07:24 vs 11/11 at 08:50 on diff-verified identical prompts. Consequence: only within-run contrasts are admissible for fine distinctions; family classifications require multi-window replication.*

- `asl001v2-qwen3` 07:24                    n=?    p=0.172  CI95=-  
- `asl002-fb-qwen3` 08:32                    n=?    p=1.0    CI95=-  

## Open questions

- Does attraction follow description text or tool identity? (ASL-002 running)
- Does schema complexity penalize invocation independently? (ASL-005 next)
- Does deterministic verification raise repeat use without raising initial selection? (ASL-009 planned)
- Do agents read prerequisite/credential requirements? (ASL-003 planned)
