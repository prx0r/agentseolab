# OpenRouter :free

**Key:** `OPENROUTER_API_KEY` in `runner/.env` (sk-or-v1-...)
**Endpoint:** `https://openrouter.ai/api/v1` (OpenAI-compatible)
**Quota:** per-model daily limits on :free variants; 429s are common and persistent for popular models.
**Last verified:** 2026-08-23

## Probed (2026-08-23)

| Model ID | Status | Notes |
|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | ✅ 10/10 ASL-001 | clean JSON, fast — best OpenRouter option |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | ✅ OK | strongest free model; slow ~3s+ |
| `nvidia/nemotron-3-nano-30b-a3b:free` | ⚠️ | leaks reasoning into content ("Okay, the user just...") |
| `z-ai/glm-5.2:free` | ❌ 429 persistent | even after 30s cooldowns |
| `google/gemma-4-{31b,26b-a4b}-it:free` | ❌ 429 persistent | |
| `thinkingmachines/inkling-small:free` | ❌ 403 | forbidden on this key tier |

18 :free models listed total (`GET /models`, filter `:free`). Nemotron family is the reliable one.
Old model IDs from earlier sessions (llama-3.3-70b:free etc.) now 404 — catalog rotates fast.

## Quirks
- 429 = per-key daily cap on that model, not per-minute. Waiting seconds doesn't help; wait a day or switch model.
- Some models prepend chain-of-thought to content — strip before JSON parsing.
