# Peer Review — all experiments (2026-08-23, pre-launch audit)

Reviewer stance: adversarial. Question every design as if trying to kill the finding.

## QLEX — TWO REAL DEFECTS
1. **temp=0 makes the "lexicon" deterministic, not distributional.** Convergence across
   families (all models emit near-identical queries) is partly an artifact of pinned
   temperature — we sampled MODE points, not the query distribution. The finding "agents
   converge on functional vocabulary" survives (mode agreement IS signal), but claims about
   diversity/frequency require a temp=0.7 companion harvest.
   FIX: rerun elicitation at temp=0.7, label corpora `qlex_greedy` vs `qlex_sampled`.
2. **Corpus B failed** (wrong datasets-server endpoint). Moltbook archive configs are
   posts/agents/comments with split=archive — use /rows endpoint, not /search.
   FIX: switch to /rows?config=posts&split=archive.
3. Known scope limit (documented): first-query only; no reformulation trajectories.

## ASL-002 — VALID but underpowered
- Arms are clean (FB = exact ASL-001 config; FW swaps fluff only). Within-model comparison
  legitimate. ✓
- DEFECT: n=24 → 12/arm → Wilson CI ±~25pp. Can detect flips, not nuances. Accept as
  pilot; any non-null result must be rerun at n≥30/arm before entering ledger above PROVISIONAL.

## TLD — FATAL CONFOUND, FIXED BEFORE LAUNCH
- Original runner gave best result a BETTER DESCRIPTION than others ("step-by-step fix" vs
  "general forum thread"). Then P(open best)=100% regardless of TLD proves nothing about TLD;
  it measures description-following. DESIGN WAS BROKEN.
- FIX (applied): all five candidates get IDENTICAL titles/descriptions; ONLY the domain
  differs. Best-result TLD counterbalanced; measure raw P(TLD picked). Now a true TLD test.

## VERIF — spec sound, not yet run
- Badge markers are truthful-by-construction; measuring marker-as-text effect is the point. ✓
- Add control: badge placed on a NON-best candidate once per block (checks blind badge
  attraction vs badge×quality interaction). Added to prereg checklist.

## ASL-001 v2 — stands, limits documented
- Threats: single task/domain; 5 of 7 models share Cloudflare host (host artifact possible);
  llama borderline (37%, CI includes .5) — classify families only after task-2 replication.

## SENTINEL — honest limitation
n=6/trial/day ⇒ noise ±40pp. Detects catastrophic flips only. Relabel output as
"canary-flip detector", not drift estimator. (Cheap upgrade later: n=12.)

## Verdict table
| Exp | Status | Action |
|---|---|---|
| ASL-001 v2 | LEGIT (limits noted) | keep; add task-2 replication |
| ASL-002 | LEGIT pilot | finish; rerun significant arms at n=30 |
| QLEX | PARTIALLY INVALID | relabel greedy corpus; add temp=0.7 pass; fix Moltbook endpoint |
| TLD | WAS BROKEN | fixed (identical snippets); then launch |
| VERIF | READY | launch after TLD |

## ADDENDUM (08:55) — CRITICAL: provider-side nondeterminism discovered

Byte-identical prompts (diff-verified), temp=0, same model/provider:
qwen3-30b @cf picked working 5/29 (07:24 run) vs 11/11 (08:50 run).
Position ruled out (overcame position in both directions in both runs).

Implications:
1. Serverless "temperature=0" is NOT deterministic (fp8 MoE expert-routing / replica variance).
2. ALL cross-run comparisons on Cloudflare are unreliable for fine distinctions. Family
   classifications from single passes (incl. parts of our own scoreboard) carry a
   run-window hazard.
3. WITHIN-RUN contrasts remain valid (arms interleaved in one time window). ASL-002's
   swap design is exactly the right instrument — its FB-vs-FW deltas stand:
     llama -0.20 · mistral -0.19 · qwen3 -0.60 (fluff-on-working collapses correct picks)
4. Ledger action: register H-SERVE01 (nondeterministic serving) PROVISIONAL; mark qwen
   family classification UNSTABLE until N replicate passes agree.
5. Sentinel upgraded in importance: it is the instrument that detects this class of drift.
