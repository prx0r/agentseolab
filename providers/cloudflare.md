# Cloudflare Workers AI

**Key:** `CF_TOKEN` in `runner/.env` · Account: `CF_ACCOUNT_ID=954612afb5a97bb15dddcdc70176813d`
**Endpoint:** `https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/ai/run/<MODEL>`
**Quota:** daily neuron allocation (free plan). Neuron cost printed in each response `usage.neurons`.
**Last verified:** 2026-08-23

## Working models (probed 2026-08-23)

| Model ID | Family | Latency | Notes |
|---|---|---|---|
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | Meta | ~500ms | primary workhorse; prompt-format sensitive |
| `@cf/mistralai/mistral-small-3.1-24b-instruct` | Mistral | ~400ms | cleanest JSON compliance so far |
| `@cf/openai/gpt-oss-20b` | OpenAI | ~600ms | prefers impressive-but-broken tools (2/10 ASL-001) |
| `@cf/qwen/qwen3-30b-a3b-fp8` | Alibaba | ~800ms+ | REASONING: needs max_tokens≥1200 else empty content |
| `@cf/meta/llama-3.1-8b-instruct-fp8` | Meta | fast | weak JSON compliance |
| `@cf/google/gemma-4-26b-a4b-it` | Google | ~700ms | prefers broken tool (1/10); high unparseable rate |
| `@cf/qwen/qwen2.5-coder-32b-instruct` | Qwen | fast | coding experiments |

## Dead on this account
- `@cf/deepseek-ai/deepseek-v4-flash` → HTTP 403 Forbidden (not entitled)

## Response format gotcha (fixed 2026-08-23 in backends.py)
Chat models return `result.choices[].message.content`.
Instruct-style models (llama-3.1-8b, qwen2.5-coder) return `result.response` instead.
backends.py now handles both.

## Quirks
- No rate-limit headers; quota is neurons/day. Watch `usage.neurons` in responses.
- Empty content + ok=True usually = reasoning model out of token budget → raise max_tokens.
- backends.py hardcodes max_tokens=1200 since 2026-08-23.
