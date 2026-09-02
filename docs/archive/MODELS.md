# Model Registry — verified 2026-08-30

## Cloudflare Workers AI
Account: 954612afb5a97bb15dddcdc70176813d
Token: REDACTED

| Model ID | Status | Notes |
|---|---|---|
| @cf/meta/llama-3.3-70b-instruct-fp8-fast | ✅ WORKS | Primary, reliable responses |
| @cf/mistralai/mistral-small-3.1-24b-instruct | ✅ WORKS | Primary, reliable responses |
| @cf/meta/llama-3.1-8b-instruct-fp8 | ⚠️ EMPTY | Returns empty on short prompts |
| @cf/qwen/qwen2.5-coder-32b-instruct | ⚠️ EMPTY | Returns empty on short prompts |
| @cf/google/gemma-4-26b-a4b-it | ⚠️ EMPTY | Returns empty on short prompts |
| @cf/openai/gpt-oss-20b | ✗ BROKEN | NoneType error |
| @cf/deepseek-ai/deepseek-v4-flash | ✗ 403 | Forbidden |

## Groq (free tier)
Key: GROQ_API_KEY (gsk_...) — console.groq.com
Endpoint: https://api.groq.com/openai/v1

| Model ID | Type | Status | Notes |
|---|---|---|---|
| qwen/qwen3.6-27b | REASONING | ✅ WORKS | Emits <think> tags, strip before parse |
| openai/gpt-oss-20b | REASONING | ✅ WORKS | Mid-scale comparison |
| openai/gpt-oss-120b | REASONING | ✅ WORKS | Flagship, expensive on other platforms |

### Groq Gotchas
- User-Agent REQUIRED: urllib default UA → HTTP 403
- Reasoning models need max_tokens ≥ 300 (hidden reasoning tokens)
- qwen3.6 wraps output in <think> tags
- 8000 tok/min limit, pace >1 call/2s

## Approved Experiment Models (AGENTS.md)
Minimum for REPLICATED status: ≥2 model families from different organizations

| Family | Model | Org |
|---|---|---|
| llama | @cf/meta/llama-3.3-70b-instruct-fp8-fast | Meta |
| mistral | @cf/mistralai/mistral-small-3.1-24b-instruct | Mistral |
| qwen | qwen/qwen3.6-27b (Groq) | Alibaba |
