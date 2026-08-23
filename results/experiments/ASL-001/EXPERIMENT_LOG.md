# ASL-001 Experiment Log

## Run History

| Date | Model | n | Correct Sel | Task Success | Status | Notes |
|------|-------|---|-------------|-------------|--------|-------|
| 2026-08-23 02:44 | llama-3.3-70b (CF) | 10 | 8 | 8 | ✅ Validated | CI [0.49, 0.943] borderline |
| 2026-08-23 02:46 | mistral-small-24b (CF) | 10 | 10 | 10 | ✅ Validated | CI [0.722, 1.0] significant |
| 2026-08-23 05:28 | llama-3.3-70b (CF) | 10 | 0 | 0 | ⚠️ PROMPT_SENSITIVITY | Same model flipped! Minor format change |
| 2026-08-23 06:11 | llama-3.3-70b (CF) | 10 | 0* | 0* | ❌ PARSING_BUG | tool=None for all trials |
| 2026-08-23 06:14 | llama-3.3-70b (CF) | 10 | 0* | 0* | ❌ PARSING_BUG | Same parsing issue persists |

*tool=None means parser returned None, NOT that model didn't respond.
Direct testing confirms model responds with valid JSON.
Parsing bug: nested braces in arguments break regex pattern.
Fix identified but not yet applied to all code paths.

## Key Finding: Prompt Format Sensitivity

llama-3.3-70b gave OPPOSITE results between two runs with nearly identical prompts:
- Run 1 (02:44): picked domain_check 8/10 (correct)
- Run 2 (05:28): picked dominatron_pro 10/10 (wrong)

Difference between runs: minor formatting changes in how tools are presented.
This means single-run experiments are unreliable for this model.

## Cross-Family Summary (validated runs only)

Both Meta and Mistral AI models prefer the working tool over the broken one,
but llama-3.3-70b's result is unstable across prompt formats while mistral's is consistent.

## Known Parsing Bug

`re.search(r'\{[^{}]*"tool"[^{}]*\}', raw)` fails on nested JSON:
```json
{"tool": "domain_check", "arguments": {"domain": "example-name.com"}}
```
because `"arguments": {"domain": ...}` contains `{}` which `[^{}]*` excludes.
Fix: use `json.loads(raw)` directly instead of regex extraction.
