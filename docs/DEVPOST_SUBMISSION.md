# Devpost Submission Draft — DomainArena

> Paste into the Devpost project page. Fill [brackets] before submitting.

## Project name
DomainArena — evidence-based domain selection for humans and agents

## One-line pitch
Not another AI name generator: DomainArena tests whether a domain actually causes
agents to select and successfully use your product, then recommends the best
purchasable option on name.com under your real budget.

## The problem
Every builder — human or agent — picks domains by vibes. Existing tools generate
hundreds of names and score them with arbitrary 0–10 "brandability" heuristics.
Nobody measures whether a domain *works*: does an autonomous agent given a task
pick your service? Does it invoke it correctly? Can it afford the renewal?

## What we built
An empirical decision engine over **name.com's live inventory**:

1. **Freeze the intent** (hash-locked before any generation).
2. **Intersect with reality**: heterogeneous candidate generators ∩ live name.com
   Search results, with real purchase/renewal/premium prices.
3. **Hard constraints**: a $20 budget REMOVES infeasible candidates — they are
   never scored lower. Premium/aftermarket/TLD policy fail-closed.
4. **Measure transmission**: blind Semantic Inversion across model families —
   can an evaluator infer the job from the hostname alone?
5. **Controlled arena**: AB/BA pairwise trials with position-bias controls and
   Bradley–Terry aggregation.
6. **The moat — execution-grounded selection**: agents get equivalent services
   differing only in hostname; they must choose AND invoke; a hidden
   deterministic verifier confirms the outcome. Funnel recorded as separate
   stages: SELECTED → INVOKED → VALID_PARAMS → TASK_VERIFIED.
7. **Robustness**: per-family × serving-window matrix; worst family reported separately.
8. **Decision**: audience-conditioned Pareto frontier → explained recommendation
   → approval gate → fresh availability recheck → registration with idempotency key
   → DNS TXT evidence receipt written and read back.

## name.com API integration depth (multi-endpoint)
- `POST /core/v1/domains:search` — inventory IS the optimization space
- `POST /core/v1/domains:checkAvailability` — batch verify + pre-purchase recheck
- `GET /core/v1/domains/{domain}:getPricing` — finalist pricing refresh
- `POST /core/v1/domains` (+ `X-Idempotency-Key`) — gated, approval-required registration
- DNS records — write + read-back the DomainArena experiment receipt

## Why it's unexpected
We turned domain selection into a controlled experiment: preregistered protocols,
frozen intents, injective verifiers, position-stratified estimands, abstention
allowed, failures never counted as selections, tamper-evident receipts. If the
data says hostname doesn't matter for some audience, we report that — the value
is discovering WHEN domains matter.

## Real-world viability
`recommend_domain(intent, audience, constraints)` is the missing recommendation
layer for every AI app-builder (Lovable/Railway/Replit-class) that embeds domain
purchase. Every successful recommendation converts directly into a name.com
registration. Railway already drives 1,700+ registrations/month through embedded
name.com purchasing — the decision layer is what's missing.

## Demo video script (2–4 min)
1. [0:00] Problem: "AI scores 94/100" vs evidence.
2. [0:30] Live: intent form → name.com search → budget elimination moment
   ("$20 means impossible, not penalized").
3. [1:30] Evidence: semantic inversion table; model-family disagreement;
   worst-family honesty.
4. [2:15] Execution-grounded trial: agent selects jsonrepair.dev over velora.com,
   invokes it, hidden verifier confirms.
5. [3:00] Recommendation → approval gate → register → DNS receipt read-back.
6. [3:30] Architecture recap + lineage disclosure.

## Screenshots needed
- [ ] Intent form UI
- [ ] Feasible/eliminated table with real name.com prices
- [ ] Recommendation card with explanation
- [ ] Execution funnel stats
- [ ] DNS receipt record

## Repos & lineage
Public repo: https://github.com/prx0r/agentseolab (history preserved from
AgentSEOLab lab; baseline tag `pre-domainarena-hackathon-2026-08-24`;
source ledger for all third-party references).
