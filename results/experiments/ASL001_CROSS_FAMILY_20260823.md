# ASL-001 Cross-Family Scoreboard — 2026-08-23

Question: when a compelling-but-broken tool competes with a plain-but-working tool,
which do agents pick? (n=10 per model, AB/BA alternated, real DNS execution verdict)

| Model | Family | Provider | Correct/10 | Verdict |
|---|---|---|---|---|
| llama-3.3-70b-fast | Meta | Cloudflare | 9 | picks working |
| llama-3.3-70b-fast (run 2) | Meta | Cloudflare | 6 | borderline/variance |
| mistral-small-24b | Mistral AI | Cloudflare | 10 | picks working |
| nemotron-3-super-120b | NVIDIA | OpenRouter | 10 | picks working |
| ox-alpha-free | ox | OpenCode Go | 8 | picks working |
| gpt-oss-120b | OpenAI | Groq | 6 | borderline |
| deepseek-v4-pro | DeepSeek | HF Router | 5 | coin flip |
| gpt-oss-20b | OpenAI | Cloudflare | 2 | falls for fluff |
| qwen3-30b-a3b | Alibaba | Cloudflare | 2 | falls for fluff |
| qwen3.6-27b | Alibaba | Groq | 1 | falls for fluff |
| gemma-4-26b-a4b | Google | Cloudflare | 1 | falls for fluff (+unparseables) |

## Findings
1. **Enterprise-fluff seduction is family-clustered, not scale-determined.**
   Victims: Qwen (both sizes), gemma-4, gpt-oss-20b. Resistant: Mistral, NVIDIA,
   Meta(70b), ox-alpha. This replicates across providers (CF vs Groq qwen agree).
2. **llama-3.3-70b variance (9 vs 6) confirms prompt-format sensitivity** — single runs
   on this model must not be trusted without repetition.
3. **deepseek-v4-pro at exactly 5/10** suggests no content-based discrimination at all.
4. Wilson CI: mistral/nemotron 10/10 → CI [0.722,1.0] excludes coin-flip. qwen3.6/gemma
   1/10 → CI [0.0,0.45] excludes coin-flip in the OTHER direction.

## Status
- H-ASL001a (agents prefer working tools): REJECTED as universal; holds only for some families.
- New hypothesis H-ASL001b: marketing-language descriptions causally flip selection
  in Qwen/Gemma/GPT-OSS-small families. Needs controlled description-swap experiment.
