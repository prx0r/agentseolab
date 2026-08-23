# OpenCode Go

**Key:** `OPENCODE_GO_API_KEY` in `runner/.env` (sk-fv9...)
**Endpoint:** `https://opencode.ai/zen/go/v1` (`/chat/completions`, `/models`)
**Policy (AGENTS.md):** ox-alpha-free ONLY for general use. mimo-v2.5 allowed for experiments.
Never any other zen model under the Go key. Weekly quota — when exhausted, stop and wait.
**Last verified:** 2026-08-23

## Working models

| Model ID | Status | Notes |
|---|---|---|
| `ox-alpha-free` | ✅ | REASONING model; ASL-001 8/10 correct selection |
| `mimo-v2.5` | ✅ | REASONING model; experiments only per owner policy |

## Critical quirks
1. **User-Agent required**: Python urllib default UA → HTTP 403. Always send a UA header
   (e.g. `User-Agent: asl-lab/2.0`). curl works without it.
2. **Reasoning budget**: both models emit `reasoning_content` first. max_tokens < 300 → empty content.
   We use 1200. Latency can exceed 45s — use timeout ≥ 120s.
3. Weekly quota resets; 403 on previously-working key = likely quota, not auth.

## Model list (GET /models 2026-08-23) — DO NOT USE under Go key except the two above
minimax-m3/m2.7/m2.5 · kimi-k3/k2.7-code/k2.6/k2.5 · glm-5.3/5.2/5.1/5 · deepseek-v4-pro/
v4-flash/v4-flash-vision-exp · qwen3.8-max/3.7-max/3.7-plus/3.6-plus/3.5-plus · mimo-v2-pro/
v2-omni/v2.5-pro/v2.5 · hy3/hy3-preview · gpt-5.6-luna · grok-4.5 · muse-spark-1.2-contributor
