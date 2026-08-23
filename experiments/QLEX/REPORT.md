# QLEX REPORT — Agent Query Lexicon (2026-08-23)

## Data
- Greedy corpus (temp=0): 70 queries, 30 unique · 4 families × 6 task-families × 3 reps
- Sampled corpus (temp=0.7): 71 queries, 49 unique
- Moltbook spot-check: 99 posts (scale-up pending; /rows endpoint now verified)

## Findings
F1. **First-query convergence (greedy)**: across independent model families the first
    search query for a task is near-canonical. Examples emitted verbatim by ≥3 families:
    "availability of domain name {domain}"
    "cheapest managed postgres database tier pricing"
    "convert heic to png linux command line"
    "python ModuleNotFoundError installed package fix"
    → Agent first-moves are functional noun-phrases: VERB-OBJECT-SPECIFIER. No brand
    words, no marketing adjectives, no site names.

F2. **Sampled diversity keeps functional core**: temp=0.7 spreads surface forms
    (+60% unique) but top tokens stay identical (cheapest, managed, tier, convert).
    The mode is stable; variance is syntactic, not lexical.

F3. **Observatory gap**: in 99 real agent posts, "api"(10)/"tool"(10)/"check"(8) dominate;
    "verify/verified"(2), "mcp"(3), "x402"(0), "llms.txt"(0). Verification vocabulary is
    vendor language, not organic agent language. (Feeds VERIF: do markers still work
    even though agents don't spontaneously use them?)

## Product implications (for llms.txt / titles / descriptions)
1. Lead with exact functional pairs agents emit: *availability*, *cheapest … pricing*,
   *convert … command line*, *validate … email*, *check … domain*.
2. Match the query HEAD NOUN ("database tier pricing" not "flexible plans").
3. Do NOT expect verification badges to match existing agent vocabulary — if VERIF shows
   they work, it's because they're novel signals, not familiar ones.

## Limits
First-query only (no reformulation loops); 99-post observatory sample; greedy/sampled
corpora never pooled; single prompt template.

## Next
Scale Moltbook sample to 5k posts; add reformulation-trajectory harvest (multi-turn);
cross-validate elicited lexicon against finalbuilds2 live search logs when available.
