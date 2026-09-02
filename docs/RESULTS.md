<!-- GENERATED from results/ledger/evidence.json — do not hand-edit -->
# RESULTS — evidence ledger snapshot (2026-08-23)

**Status: 2 CONFIRMED · 1 FAILED_REPLICATION · 1 INVALIDATED · 4 PROVISIONAL**

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

## H-ASL002C — PROVISIONAL
Description seduction is CONTRAST-driven: symmetrizing descriptions (fluff on both candidates) collapses P(pick working) to exactly chance in every family tested, including previously-seduced and resistant ones
*Protocol v2 · Discriminant arm ASL-002B (fluff_both): llama 12/24, mistral 12/24, qwen3 12/24, gpt-oss-20b 12/24 — all exactly 0.50. Rejects absolute plain-description preference AND coherence-penalty accounts for these families; selection tracks the description contrast, not description style per se nor tool identity. n=24/family is pilot power; rerun at n>=30 before promotion.*

- `asl002b-llama70b` meta-llama-3.3-70b       n=24   p=0.5    CI95=[0.32, 0.68]  
- `asl002b-mistral` mistral-small-24b        n=24   p=0.5    CI95=[0.32, 0.68]  
- `asl002b-qwen3` qwen3-30b                n=24   p=0.5    CI95=[0.32, 0.68]  
- `asl002b-gptoss20b` gpt-oss-20b              n=24   p=0.5    CI95=[0.32, 0.68]  

## H-TLD01 — PROVISIONAL
Position primacy dominates SERP-style agent choice (87% pick slot 1); conditional on occupying the top slot, .com wins it (100% vs 79-95% for other TLDs); off-slot .com retains small residual preference (15% vs ~1%)
*Protocol v2 · n=123 decided, 7 families, prereg manifest 89d81af9. CORRECTED ANALYSIS: raw marginal '.com premium' was largely position artifact (.com sat at pos0 29x vs org 19x by chance). Position-stratified estimands are primary: P(pick|pos0): com 29/29, org 18/19, dev 22/28, io 21/26, xyz 17/21. P(pick|off-pos0): com 14/94=0.15 vs others <=0.01. Original predictions partially resolved: P1 hierarchy=WITHIN-SLOT only; P2 task interaction=not detectable at n=18/family; P3 universal .xyz discount=REJECTED pooled (0.138 CI[0.088,0.210] includes 0.2). Family heterogeneity: mimo .com 0.78*, ox-alpha .com 0.47*; uniform families llama/mistral/qwen3/gptoss20b.*

- `tld-v1-pooled` 7-family-pooled          n=123  p=0.35   CI95=[0.271, 0.437] *
- `tld-v1-mimo` mimo-v2.5                n=18   p=0.78   CI95=[0.55, 0.91] *
- `tld-v1-oxalpha` ox-alpha-free            n=15   p=0.47   CI95=[0.25, 0.7]  

## H-NAMING01 — PROVISIONAL
When descriptions are informative, tool NAME style (query-echo / neutral / brand) does NOT affect selection in ANY tested family (ceiling null)
*Protocol v2 · 6 families x 36 trials each, ALL p=1.0 in every arm (216/216 target picked). Description content exhaustively determines choice under easy discrimination; name channel has zero measured marginal effect. Boundary condition established, NOT a law about naming under weak/ambiguous descriptions. NAMING-02 will test degraded-description regime (factorial: name-style x description-strength) to create discriminability headroom.*

- `naming01-ceiling` 6-family-matrix          n=215  p=1.0    CI95=[0.985, 1.0] *

## Open questions

- Does attraction follow description text or tool identity? (ASL-002 running)
- Does schema complexity penalize invocation independently? (ASL-005 next)
- Does deterministic verification raise repeat use without raising initial selection? (ASL-009 planned)
- Do agents read prerequisite/credential requirements? (ASL-003 planned)
