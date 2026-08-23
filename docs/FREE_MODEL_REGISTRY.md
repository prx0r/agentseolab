# CANONICAL FREE LLM REGISTRY — verified 2026-08-23

> Rule: every entry below was **live-tested from this box on 2026-08-23** with a real completion probe.
> "OK" = responded with content. Re-verify before long experiment runs.

## WORKING NOW

### Cloudflare Workers AI (daily neuron allocation, account 954612af...)
| Model | ID | Status | Notes |
|---|---|---|---|
| Llama 3.3 70B fast | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | ✅ OK ~500ms | Primary workhorse |
| Mistral Small 24B | `@cf/mistralai/mistral-small-3.1-24b-instruct` | ✅ OK ~400ms | Cross-family (Meta↔Mistral) |
| GPT-OSS 20B | `@cf/openai/gpt-oss-20b` | ✅ OK ~600ms | OpenAI family |
| Qwen3 30B MoE | `@cf/qwen/qwen3-30b-a3b-fp8` | ✅ OK ~800ms | Alibaba family; high unparseable rate in JSON tasks |
| Llama 3.1 8B | `@cf/meta/llama-3.1-8b-instruct-fp8` | ✅ OK | Small-model datapoint; weak JSON compliance |
| Gemma 26B MoE | `@cf/google/gemma-4-26b-a4b-it` | ✅ OK | Google family |
| Qwen2.5 Coder 32B | `@cf/qwen/qwen2.5-coder-32b-instruct` | ✅ OK | Coding-agent experiments |

**Backend note:** chat models return `result.choices[].message.content`; llama-3.1-8b + qwen2.5-coder return
`result.response`. `backends.py` handles both since 2026-08-23.

### OpenCode Go (weekly quota — ox-alpha-free for most, mimo-v2.5 only for experiments)
| Model | ID | Status | Notes |
|---|---|---|---|
| ox-alpha-free | `ox-alpha-free` | ✅ OK | REASONING model: needs max_tokens≥300, User-Agent header required (urllib default UA → 403), can take >45s |
| MiMo v2.5 | `mimo-v2.5` | ✅ OK | Also reasoning-style output; use ONLY for experiments per owner policy |

**Endpoint quirks:** base `https://opencode.ai/zen/go/v1`; never use other zen models under the Go key.

### OpenRouter :free (key sk-or-v1-a570d...)
| Model | ID | Status | Notes |
|---|---|---|---|
| Nemotron 3 Super 120B | `nvidia/nemotron-3-super-120b-a12b:free` | ✅ OK | Strong free model |
| Nemotron 3 Ultra 550B | `nvidia/nemotron-3-ultra-550b-a55b:free` | ✅ OK | Strongest free model; slow (~3s) |
| Nemotron 3 Nano 30B | `nvidia/nemotron-3-nano-30b-a3b:free` | ⚠️ responds but leaks reasoning into content ("Okay, the user just...") | Strip before parsing |
| GLM 5.2 | `z-ai/glm-5.2:free` | ❌ 429 persistent | Rate-limited even after cooldowns |
| Gemma 4 31B / 26B | `google/gemma-4-{31b,26b-a4b}-it:free` | ❌ 429 persistent | Rate-limited |
| inkling-small | `thinkingmachines/inkling-small:free` | ❌ 403 | Forbidden on this key |

## NOT WORKING / DEAD
| Provider | Key | Error | Verdict |
|---|---|---|---|
| Google Gemini (`AQ.Ab8RN6...`) | user-supplied 2026-08-23 | 401 UNAUTHENTICATED on `/v1beta/models`, `/openai/models`, `?key=` | **DEAD** — looks like an OAuth access token (AQ.*), not an AI Studio API key (AIza*). Need a fresh AI Studio key. |
| CF deepseek-v4-flash | cf token | HTTP 403 Forbidden on this account | Not entitled on this plan |
| muse-spark-1.2-contributor | OpenCode Go | not usable previously | Listed in /models but unusable |

## NOT TRIED YET (no key on box) — from dell PROVIDER-REFERENCE.md Tier 1
- HuggingFace Router `router.huggingface.co/v1` — ⭐ best single add, needs HF token
- Groq `api.groq.com/openai/v1` — free token allowances, ultra-fast
- Cerebras `api.cerebras.ai/v1` — free tier
- Mistral La Plateforme `api.mistral.ai/v1` — free tier
- Z.ai direct — GLM-5.2 free tier (bypasses OpenRouter 429)
- Together / AkashML / DeepInfra / Fireworks — cheap or trial credits
- Petals swarm — free batch research tier (slow)

## EXPERIMENT-READY MATRIX (cross-family requirement: ≥2 orgs)
| Family | Provider | Model |
|---|---|---|
| Meta | CF | llama-3.3-70b-fast |
| Mistral AI | CF | mistral-small-24b |
| OpenAI | CF | gpt-oss-20b |
| Alibaba | CF | qwen3-30b-a3b |
| Google | CF | gemma-4-26b |
| NVIDIA | OpenRouter | nemotron-3-super-120b |
| ox (undisclosed) | OpenCode Go | ox-alpha-free |
| Xiaomi (MiMo) | OpenCode Go | mimo-v2.5 (experiments only) |

8 distinct families available right now → REPLICATED status achievable without spending.
