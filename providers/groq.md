# Groq — ultra-fast free inference

**Key:** `GROQ_API_KEY` in `runner/.env` (gsk_... — console.groq.com)
**Endpoint:** `https://api.groq.com/openai/v1` (OpenAI-compatible: `/chat/completions`, `/models`)
**Last verified:** 2026-08-23

## Verified models (GET /models, 2026-08-23)

| Model ID | Type | Experiment use |
|---|---|---|
| `openai/gpt-oss-120b` | chat, REASONING | ✅ primary — flagship, responds OK |
| `openai/gpt-oss-20b` | chat, REASONING | ✅ mid-scale comparison |
| `qwen/qwen3.6-27b` | chat | ✅ Alibaba family replication |
| `groq/compound` / `groq/compound-mini` | agentic system | ⚠️ tool-using wrapper, avoid for pure-selection trials |
| `openai/gpt-oss-safeguard-20b` | safety classifier | not for experiments |
| `allam-2-7b` | chat (Arabic-focused) | small-model datapoint |
| whisper-large-v3(-turbo) | audio | n/a |
| orpheus-v1-english | TTS | n/a |
| llama-prompt-guard-2-{22m,86m} | classifier | n/a |

NOTE: no Llama-3.3-70B on this key (unlike public docs) — model list is key-specific. Re-check `/models`.

## Rate limits (observed from headers 2026-08-23)

| Header | Value |
|---|---|
| x-ratelimit-limit-requests | **1000** |
| x-ratelimit-limit-tokens | **8000 tokens/min** |
| reset-requests | ~90s window |
| reset-tokens | <1s |

8000 tok/min is the binding constraint for reasoning models (they burn hidden reasoning tokens).
→ For gpt-oss-120b keep max_tokens ≤ 1000 and pace >1 call/2s during batches.
→ Log every call via `providers.track_usage.log_call("groq", model, latency, ok, resp.headers)`.

## Quirks
0. **User-Agent required**: urllib default UA → HTTP 403 (Cloudflare front). Always send a UA header.
1. **Reasoning models**: gpt-oss-* put tokens into `message.reasoning` first; with low max_tokens
   you get `"content": ""`. Use max_tokens ≥ 300 (we use 1200).
2. Model IDs are namespaced (`openai/gpt-oss-120b`, not `gpt-oss-120b`).
3. Free tier = dev tier; models rotate. Probe before runs.
4. Groq returns rate-limit info on EVERY response — harvest it.

## Test snippet
```bash
curl -s https://api.groq.com/openai/v1/chat/completions \
 -H "Authorization: Bearer $GROQ_API_KEY" -H "Content-Type: application/json" \
 -d '{"model":"openai/gpt-oss-120b","messages":[{"role":"user","content":"Say OK"}],"max_tokens":300}' \
 | python3 -c "import json,sys; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```
