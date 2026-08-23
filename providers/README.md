# PROVIDERS — canonical registry

One file per provider. Every provider doc MUST contain: key location, endpoint, verified models,
rate limits (observed), quirks/gotchas, and last-verified date. Update after every session.

## Index

| File | Provider | Key env var | Status (2026-08-23) |
|---|---|---|---|
| [cloudflare.md](cloudflare.md) | Cloudflare Workers AI | `CF_TOKEN` | ✅ 7 models working |
| [opencode-go.md](opencode-go.md) | OpenCode Go | `OPENCODE_GO_API_KEY` | ✅ ox-alpha-free + mimo-v2.5 |
| [openrouter.md](openrouter.md) | OpenRouter :free | `OPENROUTER_API_KEY` | ⚠️ nemotron works; gemma/glm 429 |
| [huggingface.md](huggingface.md) | HF Router | `HF_TOKEN` | ✅ deepseek-v4-pro + llama-70b |
| [groq.md](groq.md) | Groq | `GROQ_API_KEY` | ✅ gpt-oss-120b + qwen3.6 |
| [google-gemma.md](google-gemma.md) | Google Gemma key | `GEMMA_API_KEY` | ❌ 401 — needs correct endpoint or new key |

All keys live in `runner/.env` (gitignored). NEVER commit keys.

## Rules
1. Before any experiment run: probe each backend you plan to use (`Reply with exactly: OK`).
2. After each call, log rate-limit headers to `usage.csv` (see provider docs for header names).
3. A model that returns empty content 3x in a row = mark degraded in its provider doc.
4. Re-verify this whole index at the start of every session. Models rot fast on free tiers.

## Usage tracking
`python3 providers/track_usage.py "provider" "model"` → appends a row with remaining quota
headers to `providers/usage.csv`. Run it inside your request loop.
