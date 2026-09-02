# HuggingFace Router

**Key:** `HF_TOKEN` in `runner/.env` (hf_... — inference.serverless scope)
**Endpoint:** `https://router.huggingface.co/v1` (OpenAI-compatible)
**Quota:** ~$0.10/mo free credits included with free accounts; PRO $2/mo.
**Last verified:** 2026-08-23

## Probed models (2026-08-23)

| Model ID | Status | Notes |
|---|---|---|
| `deepseek-ai/DeepSeek-V4-Pro-0813` | ✅ OK | DeepSeek family replication; ASL-001 5/10 |
| `meta-llama/Llama-3.3-70B-Instruct` | ✅ OK | independent llama endpoint (cross-check CF) |
| `Qwen/Qwen3-32B` | ⚠️ EMPTY | reasoning model; retry with max_tokens ≥ 1200 |
| `mistralai/Mistral-Small-24B-Instruct-2501` | ❌ 400 | wrong model id; check router /v1/models |

Hundreds of models available — one key, effectively a free OpenRouter. Check
`GET /v1/models` for the live catalog before adding new families.
