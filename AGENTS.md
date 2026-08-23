# MODEL POLICY — ALWAYS IN EFFECT (owner directive)

**Owner is broke. Never spend money on inference. Ever.**

## Allowed (all FREE under Cloudflare Workers AI daily neurons)
Rotate across model families for diversity:

### Primary workhorses (strong + free)
- `@cf/meta/llama-3.3-70b-instruct-fp8-fast`
- `@cf/mistralai/mistral-small-3.1-24b-instruct`
- `@cf/qwen/qwen3-30b-a3b-fp8`
- `@cf/deepseek-ai/deepseek-v4-flash-0731`
- `@cf/openai/gpt-oss-20b`

### Secondary (also free, smaller/faster)
- `@cf/meta/llama-3.1-8b-instruct-fp8`
- `@cf/google/gemma-4-26b-a4b-it`
- `@cf/zai-org/glm-5.2`
- `@cf/qwen/qwen2.5-coder-32b-instruct`

### OpenCode Go
- `ox-alpha-free` ONLY (weekly quota; wait for reset)

## Forbidden
- `@cf/openai/gpt-oss-120b` (expensive neuron cost)
- Any paid API or balance-drawdown model
- OpenRouter paid models

## Rule
If a task needs a stronger model: degrade scope, split task, or report limitation.
Model escalation is never autonomous. Rotate families for experiment diversity.
