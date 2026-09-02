# DomainArena — Final Win-Probability Dev Plan

## Current verdict

Latest audited push: `66cd8b841cb27386c62b07b9b67212e095eae0d6`.

The product concept and presentation have improved dramatically:

- live Cloudflare Worker deployed
- live name.com search/pricing
- 4-tab demo flow
- before/after framing
- inline API trace
- sponsor-depth explanation
- 8 domains/prices
- full Python lifecycle architecture in the repo
- 16-experiment research foundation across 7+ model families

But **DomainArena is not recording-ready yet** because the deployed Worker has several hard P0 issues that are more important than adding polish.

The winning concept remains excellent:

> **A/B testing for domain names in the agentic web: measure which available name AI agents actually understand, then acquire and configure the winner through name.com.**

The demo should leave the judge remembering:

> “That’s the project that tested the domain names on AI agents and then actually bought/configured the winner.”

---

# P0 SECURITY — ROTATE THE EXPOSED NAME.COM CREDENTIAL NOW

The current public repository contains a hard-coded Basic name.com credential in `worker/index.js`.

I am deliberately not reproducing it here.

## Immediate actions

1. Revoke/rotate the exposed name.com token immediately.
2. Remove the credential constant from `worker/index.js`.
3. Put the replacement credentials in Cloudflare secrets, e.g.:

```bash
wrangler secret put NAMECOM_USERNAME
wrangler secret put NAMECOM_TOKEN
```

4. Construct Basic auth server-side from `env.NAMECOM_USERNAME` and `env.NAMECOM_TOKEN`.
5. Confirm the old token no longer works.
6. Enable GitHub secret scanning if available.

Because the token has been public, deleting the current line is not sufficient; **rotation is mandatory**.

If practical, scrub the secret from git history after rotation, but do not delay token revocation while doing so.

---

# P0 SECURITY — THE PUBLIC WORKER CURRENTLY EXPOSES BILLABLE WRITES

The deployed Worker currently has public routes equivalent to:

```text
/api/register?domain=...
/api/dns?domain=...
```

The register route can call name.com domain registration directly from an arbitrary domain query parameter. The DNS route can write a TXT record.

This bypasses the safe approval-gated lifecycle that exists in the canonical Python `DomainService`.

This is dangerous and also weakens the judge story because the README claims:

- approval token
- write guard
- budget limits
- fresh price check
- price drift guard
- idempotency
- immutable decision basis

while the public Worker currently bypasses those controls.

## Fix before anything else

The public deployed demo must never expose an unauthenticated billable registration primitive.

### Fast robust design

Replace `/api/register` with a single guarded `/api/execute-registration` flow.

It accepts only a server-generated decision token, not an arbitrary domain.

Decision token should bind:

```json
{
  "domain": "winner.com",
  "intent_hash": "...",
  "purchase_price": 12.99,
  "renewal_price": 18.99,
  "expires_at": "...",
  "nonce": "..."
}
```

HMAC-sign it with a server-side Worker secret.

Before write:

1. validate HMAC
2. validate not expired
3. re-run name.com availability
4. re-fetch price
5. enforce first-year budget
6. enforce renewal budget
7. reject price drift
8. require explicit human approval
9. reject duplicate nonce
10. register exact signed domain only
11. create DNS
12. read DNS back
13. produce receipt

### Human approval for the demo

Do **not** put a secret approval token in browser JavaScript.

A practical recording-only approach:

- set `DOMAINARENA_DEMO_APPROVAL_CODE` as Worker secret
- presenter manually types approval code into an approval field
- Worker compares server-side
- code is never sent in page source

Better long-term: durable state + one-time approval token, but the server-side demo approval code is enough for tomorrow if the rest of the constraints are enforced.

Public judges should be able to run search/test/recommend freely but **not spend your money**.

---

# P0 TRUTHFULNESS — THE DEPLOYED “AGENT TEST” IS CURRENTLY HEURISTIC, NOT AI

This is the biggest presentation truth bug.

The Worker’s `/api/infer` currently does substring matching such as:

- if domain contains `fix`, `repair` or `json` → return JSON-repair inference
- if it contains `valid` or `check` → return validation inference
- otherwise generic technology inference

and then adds random score variation with `Math.random()`.

But the website tells the judge:

> blind semantic inversion
> AI agents
> frozen intent
> generator/judge separation
> academic agent-comprehension methodology

The current deployed endpoint does not actually do that.

## This MUST be fixed before recording

### Preferred fix — real Cloudflare Workers AI

Bind Workers AI:

```toml
[ai]
binding = "AI"
```

Run a real tested model for blind inference:

```js
await env.AI.run(TEST_MODEL, {
  messages: [{role:'user', content: blindPrompt(domain)}]
})
```

Then use a different model for scoring:

```js
await env.AI.run(JUDGE_MODEL, {
  messages: [{role:'user', content: scorePrompt(frozenIntent, inference)}]
})
```

Enforce:

```text
TEST_MODEL != JUDGE_MODEL
```

Return:

```json
{
  "domain": "...",
  "inference": "...",
  "inference_model": "...",
  "judge_model": "...",
  "semantic_score": 0.87,
  "intent_hash": "sha256:...",
  "response_hash": "sha256:...",
  "mode": "LIVE_AI"
}
```

Now the website claim becomes true.

### Reliability fallback

Capture real results ahead of time and support:

```text
LIVE_AI
REPLAY_AI
```

If Workers AI fails during recording, switch to replay and label it explicitly:

> `REPLAY — captured real model responses`

Never fall back silently to heuristic values while leaving an “AI LIVE” label.

### Remove random scoring entirely

`Math.random()` must not determine a scientific recommendation.

If a score is not actually measured, mark it:

```text
PROXY
```

The repo already has the correct evidence ontology for this. Use it.

---

# P0 — MAKE THE DEPLOYED DEMO USE THE SAME SAFETY STORY AS THE REPO

Right now there are effectively two DomainArenas:

1. **Python DomainService** — rigorous state machine, budgets, approval, drift guards, evidence model.
2. **Cloudflare Worker demo** — duplicate lightweight implementation that bypasses some of those guarantees.

A technical judge can notice this.

## Goal

The deployed site must represent the canonical architecture, not a visually similar toy.

### Minimum acceptable parity

The Worker must show the same logical states:

```text
DISCOVERED
→ MEASURED
→ RECOMMENDED
→ PREPARED
→ APPROVED
→ REGISTERED
→ DNS_CONFIGURED
→ VERIFIED
```

And block illegal transitions.

At minimum persist a signed decision object in memory/KV for the short demo workflow.

If using KV is too much, a stateless HMAC-bound decision receipt is acceptable for the hackathon demo.

---

# P0 — FIX CI BEFORE RECORDING

Latest GitHub Actions is still red.

Python 3.12 clean runner collects 103 tests and fails during collection on three import errors:

```text
ModuleNotFoundError: cogym_kernel
ModuleNotFoundError: world
ModuleNotFoundError: sentinel
```

The README says `148 tests passing`, but CI currently proves otherwise.

## Fix strategy

### `cogym_kernel`

Either:

- package the kernel as an actual dependency/importable module,
- vendor the minimal required contracts under `domainarena/`, or
- move worldpack/metascience tests to an optional research test group that installs its dependencies explicitly.

Do not let the canonical `pytest tests/` depend on an undeclared local package.

### `world` / `sentinel`

Tests should import through real package paths, not rely on local root-path hacks.

Use e.g.:

```python
from domainarena.world import ...
```

or package research modules properly.

### Acceptance

GitHub Actions must be green on both:

```text
Python 3.11
Python 3.12
```

Then derive the exact test count from CI and update README.

Do not keep `148 tests passing` unless CI reports that exact current number.

---

# P0 — CLEAN THE NAME.COM ENDPOINT STORY

The website says `6 name.com endpoints`, but the top intent page currently lists only 5 visible operations and omits the explicit fresh availability/check step.

The sponsor story should always be:

```text
1. Search
2. Check Availability
3. Get Pricing
4. Register
5. DNS Create
6. DNS Readback
```

Put all six on the first page.

## API trace needs to show name.com operations, not only your wrapper

Current browser trace shows things like:

```text
POST /api/search
```

That is useful for debugging but weak sponsor proof.

The backend should return a sanitized sponsor trace:

```text
POST /core/v1/domains:search              200   481ms
POST /core/v1/domains:checkAvailability   200   312ms
GET  /core/v1/domains/x:getPricing        200   221ms
POST /core/v1/domains                     200   688ms
POST /core/v1/domains/x/records           200   302ms
GET  /core/v1/domains/x/records           200   190ms
```

No auth headers.

This one visual can almost single-handedly prove deep name.com integration.

---

# P1 — FIX INTENT → SEARCH QUERY EXTRACTION

The current Worker derives a keyword from the first words of the sentence. With the default intent:

> “A JSON repair API for AI agents...”

this can produce a poor search keyword such as `ajson`.

For the fixed demo, do not improvise.

## Options

Best:

Use a tiny extraction model to convert intent into 2–4 domain-search keywords:

```json
{"keywords":["json repair","fix json","json validate"]}
```

Then call name.com Search for each and merge/dedupe.

Fast deterministic fallback:

Use a stopword remover and select meaningful nouns/verbs:

```text
json
repair
validate
```

For tomorrow, use a fixed canonical input that has been rehearsed and returns good live candidates.

---

# THE WINNING DEMO SCRIPT

Target: **2:35–2:55**.

The product is extremely demo-friendly once the live AI + secure registration path is real.

## 0:00–0:14 — Hook

Screen: Intent tab.

Say:

> “Domain search tools optimize names for humans. But increasingly the customer discovering and choosing your service is an AI agent. Nobody tells you whether the agent actually understands your domain.”

## 0:14–0:27 — Product

> “DomainArena tests live available names against AI agents before you buy them, then name.com acquires and configures the winner.”

Point briefly at the six name.com operations.

## 0:27–0:48 — Live name.com inventory

Click Search.

> “I describe a JSON repair API. DomainArena searches name.com for live inventory and retrieves current availability, purchase price and renewal economics.”

Show LIVE badge + sponsor trace.

## 0:48–1:18 — The magic trick: semantic inversion

Move to Agent Test.

> “Now we reverse the usual branding question. Instead of asking an LLM whether a name sounds good, we remove the product description entirely and ask the model what it thinks actually lives behind each domain.”

Pause on one wrong/funny inference.

> “This one sounds good to a human, but the agent infers the wrong service.”

Pause on the strong candidate.

> “This one transmits the intended function immediately.”

Then:

> “A different model scores that blind interpretation against the frozen intent, so the tested model never judges itself.”

## 1:18–1:38 — Evidence-based recommendation

Show winner and ideally cross-family/repetition evidence.

> “Instead of one subjective rating, DomainArena produces evidence: repeated trials, order controls and cross-model agreement.”

If the live screen only runs one model, say:

> “The live decision uses this measurement; the research tab shows the larger cross-family experiment.”

## 1:38–1:57 — Fresh checkout / human authority

Click prepare.

> “Before any irreversible action, we ask name.com again. Search is discovery, not authority. Availability and price are rechecked, budgets are enforced, and any drift invalidates the decision.”

Show fresh check.

> “The recommendation is autonomous. Spending is not.”

Enter approval code/click approve.

## 1:57–2:18 — Register + DNS

Execute the one intended registration.

> “name.com registers the measured winner. DomainArena then creates DNS and reads it back instead of assuming the write worked.”

Show all six API calls completing.

## 2:18–2:30 — Receipt

Show:

```text
REGISTERED
DNS VERIFIED
receipt hash
intent hash
semantic evidence
purchase price
```

Say:

> “So the lifecycle is search, measure, approve, acquire, configure and prove.”

## 2:30–2:46 — Research / frontier

Open Agent Legibility Lab.

> “This came out of sixteen experiments across seven-plus model families. We found description bias, strong position effects, temporal nondeterminism and family-specific behavior — which is why a single LLM brand score is not enough.”

Show one chart.

## 2:46–2:55 — Close

> “The web is becoming agent-readable and agent-callable. DomainArena adds a missing pre-deployment question: before you buy the address, will the machine audience understand it?”

End on VERIFIED receipt.

---

# EXTRA CREDIT — BUILD THE AGENT LEGIBILITY LAB

The current website has the product flow but does not expose enough of the research program.

This is your strongest extra-credit opportunity, analogous to ProofDesk Trust Lab.

Add a fifth tab:

> **5. Research Lab**

Call the benchmark:

> **DomainBench — measuring agent legibility of domain names**

The UI should be a scientific exhibit, not a wall of text.

## Chart 1 — Model-family disagreement

For a fixed intent/candidate set:

```text
Llama      ████████ 82%
Mistral    █████    54%
Qwen       █████████ 91%
...
```

Metric could be correct blind inference or pairwise preference.

Judge takeaway:

> “Domain quality is model-family dependent.”

## Chart 2 — Position bias

Show your existing SERP/TLD finding visually:

```text
slot 0 █████████████████ 87%
slot 1 ██
slot 2 █
...
```

Then explain why AB/BA/Latin-square controls exist.

## Chart 3 — Description seduction

Per family, show probability of selecting the broken tool when only it receives enterprise-fluff language.

This proves you studied the broader agent-selection problem before productizing it.

## Chart 4 — Domain pairwise arena

For the exact demo intent:

```text
fixjson...      73% [Wilson CI ...]
jsonultra...    27%
```

Run AB/BA ordering and real multiple trials.

This is the chart most directly tied to the product.

## Chart 5 — Temporal drift / nondeterminism

Show the same byte-identical prompt in different time windows yielding different choice rates.

Judge takeaway:

> “One call is not a measurement.”

Do not show all five in the video. Show one or two. Let judges explore the rest afterwards.

---

# HIGH-VALUE NEW EXPERIMENT — DOMAIN-SPECIFIC CROSS-FAMILY BENCHMARK

Your existing research is broader than domains. To make the paper/product connection undeniable, run one clean domain-specific study now.

Suggested minimal protocol:

- 10 product intents
- 4 candidate domains per intent
- 3 model families
- 10–20 repetitions per pair where affordable
- AB/BA order randomization
- frozen intent hashes
- separate judge model
- Wilson CIs

Questions:

1. Can a model infer the intended product from the domain alone?
2. Do model families agree?
3. Does position change selection?
4. Does TLD change selection after controlling position?
5. Does pairwise winner correlate with blind semantic-inference score?

Produce one committed JSON run and automatically generated figures.

This transforms “16 experiments” from background lore into direct evidence for the product.

---

# TECHNICAL PREPRINT

If the benchmark run is complete, create a 5–7 page technical preprint:

**Do AI Agents Understand Domain Names? Measuring Agent Legibility Before Domain Acquisition**

Structure:

1. Introduction — domains now have machine audiences
2. Related work — AgentDNS / DNS-based agent discovery / AEO
3. DomainArena semantic inversion
4. Experimental controls
5. Cross-family results
6. Position/TLD effects
7. From measurement to name.com acquisition
8. Limitations
9. Conclusion

Call it a technical preprint, not arXiv unless actually submitted.

Every figure must be regenerated from committed result files.

---

# FRONTIER POSITIONING — THIS IS THE IMPORTANT STRATEGIC FRAME

Do not claim “agents can buy domains” as the innovation anymore.

Cloudflare now explicitly provides:

- Registrar API: agents can search/check/register domains programmatically
- Cloudflare MCP support for registrar operations
- Agent Readiness: checks whether deployed sites are readable/discoverable/callable/payable by agents
- AEO Visibility: measures whether AI assistants recommend/cite a deployed brand
- April 2026 work showing agents can create accounts, buy domains and deploy

Useful current references:

- https://developers.cloudflare.com/registrar/registrar-api/
- https://blog.cloudflare.com/agent-readiness/
- https://www.cloudflare.com/press/press-releases/2026/cloudflare-adds-aeo-visibility-dashboard-to-its-aeo-suite-showing-brands-whether-ai-assistants-are-recommending-them/
- https://blog.cloudflare.com/the-agentic-internet/
- AgentDNS: https://arxiv.org/abs/2505.22368
- DNS agent-discovery research: https://arxiv.org/abs/2606.02314

This is good for DomainArena, not bad.

It validates the market.

Your positioning becomes:

```text
DOMAIN REGISTRARS
What is available and what does it cost?

DOMAINARENA
Before deployment: which address transmits the right meaning to agents?

AGENT READINESS
After deployment: can agents read/call/pay the site?

AEO VISIBILITY
After deployment: do assistants recommend/cite it?
```

DomainArena owns the **pre-acquisition measurement layer**.

That is a much clearer startup wedge.

Put a small “Where DomainArena fits” diagram on the Research Lab page, not the main demo path.

---

# NAME.COM SHOULD BE PRESENTED AS THE EXPERIMENTAL SUBSTRATE

The best sponsor framing is not:

> “After our AI chooses a name, we register it with name.com.”

It is:

> **“name.com provides the live inventory and market constraints that make DomainArena’s experiment actionable. We measure real purchasable candidates, then use the same API to revalidate and execute the measured decision.”**

Thus name.com is involved both **before** and **after** the research step.

That is sponsor-central.

---

# WEBSITE — EXACT REQUIRED CHANGES

## Intent tab

- keep current explanation
- list all six name.com operations
- add one sentence: `Live inventory is the experimental candidate set.`

## Discovery tab

- live sponsor trace
- explicit availability + purchase + renewal price
- make source `name.com LIVE` obvious

## Agent Test tab

- replace heuristic/random endpoint with actual models
- show model IDs
- show LIVE_AI / REPLAY_AI
- show intent hash
- show blind inference text
- show judge score
- no invented score

## Result tab

- show recommendation evidence
- fresh availability + price
- budget gate
- human approval
- secure registration
- DNS create
- DNS readback
- final receipt

## Research Lab tab

- 3–5 real graphs
- 16-experiment overview
- DomainBench run
- technical preprint
- frontier positioning

---

# REPO PRESENTATION

After CI is fixed, root README should begin with:

```text
[Live Demo] [Demo Video] [Research Lab] [Technical Preprint]
```

Then:

1. one-line pitch
2. 8-line lifecycle
3. one screenshot/GIF
4. name.com 6-operation table
5. research summary
6. clean quickstart

Move/archive old internal handovers and P0 reviews so the root feels like a product repository rather than a development diary.

Do not remove the research; organize it.

---

# CLAIM HYGIENE

Current README says:

`pytest tests/ -v # 148 tests passing`

That must change until CI is green.

The public page also must not call heuristic inference `MEASURED AI`.

Use the existing ontology rigorously:

- `MEASURED` = actual experiment/model call
- `PROXY` = heuristic
- `NOT_MEASURED` = no data

Similarly:

- “CONFIRMED” only when the experiment lifecycle gates actually support it
- “PROVISIONAL” otherwise

This honesty is part of the research moat.

---

# DO NOT BUILD BEFORE SUBMISSION

Do not:

- add another registrar
- add blockchain domains
- redesign MCP
- add billing
- build user accounts
- run dozens of new unrelated research hypotheses
- rewrite frontend framework
- create autonomous production spending

Everything should serve this story:

```text
live name.com inventory
→ real agent-legibility measurement
→ evidence-backed recommendation
→ fresh name.com check
→ human approval
→ registration
→ DNS
→ verified receipt
```

---

# EXECUTION ORDER

## Block 1 — Emergency security/truth

1. rotate leaked name.com token
2. move replacement to Worker secrets
3. disable public unauthenticated registration/DNS
4. replace heuristic `/api/infer` with real Workers AI or explicit replay

Do not record until these four are done.

## Block 2 — CI

1. fix `cogym_kernel`
2. fix `world` import
3. fix `sentinel` import
4. green 3.11 + 3.12
5. update exact test count

## Block 3 — One canonical live lifecycle

1. fixed JSON-repair intent
2. live name.com candidates
3. real agent inference
4. measured winner
5. fresh check
6. guarded approval
7. one registration
8. DNS write
9. DNS readback
10. receipt

Rehearse writes disabled until the final intended take.

## Block 4 — Research extra credit

1. build Research Lab tab
2. render existing real experiment results
3. run one domain-specific cross-family benchmark
4. generate 2–3 paper-quality figures
5. optional preprint

## Block 5 — Presentation

1. replace DEMO.md with exact final website sequence
2. record 2:40-ish screencast
3. no slides in main flow
4. 1–2 hard cuts maximum
5. end on VERIFIED receipt
6. Devpost links Live Demo + GitHub + research

---

# FINAL ACCEPTANCE CHECKLIST

- [ ] exposed name.com token revoked
- [ ] no credentials committed
- [ ] write endpoints protected
- [ ] browser cannot register arbitrary domain
- [ ] fresh availability check before every registration
- [ ] price + renewal budgets checked server-side
- [ ] human approval required server-side
- [ ] real Workers AI inference OR clearly labelled captured replay
- [ ] no Math.random scientific scores
- [ ] generator/judge separation actually true
- [ ] all 6 name.com operations visible
- [ ] sponsor trace shows actual name.com operation names
- [ ] DNS readback verifies write
- [ ] receipt binds intent + evidence + purchase + DNS
- [ ] CI green Python 3.11/3.12
- [ ] README test count equals CI
- [ ] Research Lab shows real data only
- [ ] fixed demo input rehearsed
- [ ] video under 3 minutes

## Final positioning

> **DomainArena measures agent legibility before a domain is purchased. name.com provides the live candidate market, executes the approved acquisition, and verifies the resulting DNS infrastructure.**

This is much more novel than a domain-search chatbot, and the current frontier makes the story more timely: the Internet is actively being rebuilt for agents, but there is still no standard measurement for whether the machine audience understands the address you choose.
