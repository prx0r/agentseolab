# MODEL POLICY — ALWAYS IN EFFECT (owner directive)

**Owner is broke. Never spend money on inference. Ever.**

## Allowed (free tiers only)
1. **Cloudflare Workers AI** — free daily neuron allocation. Use CHEAP small models:
   - `@cf/meta/llama-3.2-3b-instruct` (default workhorse)
   - `@cf/meta/llama-3.1-8b-instruct`, `@cf/qwen/qwen2.5-coder-32b-instruct`,
     `@cf/mistralai/mistral-small-3.1-24b-instruct` (rotate for variety)
   - ❌ NEVER `@cf/openai/gpt-oss-120b` (expensive neuron cost)
2. **OpenCode Go** — `ox-alpha-free` ONLY. When weekly quota hits, stop and wait for reset.
   - ❌ NEVER any other zen model under the Go key (burns the same quota pool)

## Forbidden
- OpenRouter (unless a free:model variant is explicitly used)
- Any paid API, any balance-drawdown model, any "enable usage from balance" prompt

## Rule for agents
If a task seems to need a stronger model: degrade scope, split the task,
or report limitation. Model escalation is never autonomous.
