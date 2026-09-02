# DomainArena — Finish-Line Dev Plan for name.com Submission

## Goal

Get `github.com/prx0r/agentseolab` into a clean, judge-proof submission state for the **name.com** track, with one canonical product story, green CI, a reproducible clean-clone setup, a deterministic rehearsal path, and one polished 2–3 minute live demo.

The product is already substantially built. Do **not** add major new features. The work now is packaging, reliability, demo discipline, and making the technical depth easy for judges to discover.

---

# 1. Canonical product definition

## Product name
**DomainArena**

## One-line pitch
**Measure which domains AI agents actually understand, then safely acquire and configure the winner with name.com.**

## Core thesis
The web is becoming agent-consumed as well as human-consumed. Existing domain recommenders optimize for human brandability, SEO, or arbitrary LLM taste. DomainArena asks a different question:

> If an autonomous agent sees this domain with no context, does the name actually transmit the intended product meaning?

DomainArena tests candidate domains across models, measures semantic comprehension, incorporates price/availability constraints, and then uses name.com to perform the real domain lifecycle.

## Canonical flow

1. User supplies product intent + budget constraints.
2. name.com search returns candidate domains.
3. AI models are shown candidate names blind and infer what product/service sits behind each domain.
4. A separate evaluator scores alignment with the frozen product intent.
5. DomainArena recommends the strongest candidate.
6. name.com is queried again for fresh availability + pricing.
7. Human approves the irreversible purchase.
8. DomainArena registers the domain.
9. DomainArena creates DNS records.
10. DomainArena reads DNS back and produces a verified receipt.

The sponsor API should visibly be central from discovery through execution, not a decorative lookup at the end.

---

# 2. Current state

The good news: the product itself is largely there.

Already implemented:

- name.com domain search
- availability checks
- pricing
- domain registration
- DNS creation
- DNS read-back verification
- approval-gated registration
- MCP interface
- HTTP/API layer
- interactive hackathon demo
- evidence receipts
- research system for measuring agent comprehension
- pairwise experiments with AB/BA order control
- Wilson confidence intervals
- generator/judge separation
- frozen intent hashes
- multiple model families
- verified full name.com lifecycle from previous testing
- ~148 locally reported tests

The primary remaining risk is **submission engineering**, not product ideation.

---

# 3. P0 — fix packaging and CI before anything else

## Problem

Latest GitHub Actions is red even though local tests were reported as passing.

`pip install -e ".[dev]"` succeeds, but the installed package cannot import modules such as:

- `domainarena.api`
- `domainarena.arena`
- `domainarena.providers`
- `domainarena.constraints`
- `domainarena.world`

The repository also contains a top-level `src/` directory with old Rust/stale package metadata, while the actual current Python package is `domainarena/`.

This means setuptools package discovery is ambiguous/incomplete.

## Required fix

Make package discovery explicit in `pyproject.toml`.

Suggested shape:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["domainarena*"]
exclude = ["src*", "tests*", "research*", "archive*"]
namespaces = true
```

Add explicit package markers where appropriate:

```text
domainarena/api/__init__.py
domainarena/arena/__init__.py
domainarena/providers/__init__.py
domainarena/web/__init__.py
```

If `experiments` is intentionally imported by the canonical test suite, either:

- make `experiments` an explicit installable package too, or
- stop requiring experimental modules from package-install tests.

Do not leave tests in a half-installed state where they work only because the repository root happens to be on `sys.path` locally.

## Remove stale packaging artefacts

Delete committed stale egg-info such as:

```text
src/domain_intelligence_lab.egg-info/
```

Do not commit generated package metadata.

Add appropriate entries to `.gitignore`:

```text
*.egg-info/
.eggs/
build/
dist/
```

## Fix dangling submodule/gitlink debris

Actions cleanup currently reports warnings around old imported research repositories such as `research/upstream/AgentSearchBench` without matching `.gitmodules` configuration.

Resolve this cleanly:

- either restore valid `.gitmodules` entries if these are intentional submodules,
- or convert them to normal directories / remove stale gitlinks.

A judge should not see Git complaining during a clean CI run.

## Acceptance test

Do not consider packaging fixed until this exact sequence works in a totally new directory:

```bash
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -c "import domainarena; import domainarena.api.http; import domainarena.providers.namecom"
pytest tests/ -v --tb=short
python -m domainarena.web.demo
```

And GitHub Actions must be green for both:

- Python 3.11
- Python 3.12

No exceptions. A green badge is part of the submission package.

---

# 4. P0 — establish one canonical repo layout

The repository has accumulated substantial research and previous AgentSEO work. Do not delete useful work, but stop forcing judges to infer what is current.

## Desired top-level hierarchy

Aim for something visually like:

```text
README.md
DEMO.md
SUBMISSION.md
pyproject.toml
.env.example

domainarena/        # canonical product
experiments/        # research experiments that support product
results/            # selected validated evidence only
docs/
  RESEARCH.md
  ARCHITECTURE.md
  NAMECOM_INTEGRATION.md
  FUTURE.md

tests/
archive/            # clearly old / noncanonical material
```

If old Rust/AgentSEO code remains, either move it under `archive/legacy/` or clearly label it as noncanonical.

The README should make it impossible to misunderstand which code judges should run.

---

# 5. P0 — rewrite README around the name.com judge

The first screen of README should answer five questions immediately:

1. What is DomainArena?
2. Why does it matter?
3. Where is name.com used?
4. Can I run it now?
5. What makes this more than an LLM domain recommender?

## Suggested README opening

```markdown
# DomainArena

**A/B testing for domain names in the agentic web.**

DomainArena measures whether AI agents understand what a domain name means, then uses name.com to safely search, price, register, configure and verify the winning domain.

> Human domain tools ask: “Does this name sound good?”
> DomainArena asks: “Does an AI agent infer the right product from this name with no context?”
```

Immediately below, include a simple flow:

```text
INTENT
  ↓
name.com SEARCH
  ↓
AGENT COMPREHENSION TEST
  ↓
EVIDENCE-BASED RANKING
  ↓
name.com FRESH PRICE + AVAILABILITY
  ↓
HUMAN APPROVAL
  ↓
name.com REGISTER
  ↓
DNS CREATE + READ-BACK
  ↓
VERIFIED RECEIPT
```

Then a sponsor-depth table:

| name.com capability | DomainArena use |
| --- | --- |
| Search | discover candidate domains |
| Availability | fail closed before purchase |
| Pricing | enforce purchase + renewal budgets |
| Registration | execute approved acquisition |
| DNS create | configure acquired domain |
| DNS read | verify configuration actually landed |

This should be one of the most obvious multi-endpoint sponsor integrations in the hackathon.

---

# 6. P0 — lock down live vs fixture semantics

The current demo correctly distinguishes:

- `live` when `NAMECOM_USERNAME` exists
- `fixture` otherwise

Keep that behavior.

But make the distinction explicit everywhere:

- UI badge
- README
- `DEMO.md`
- CLI output
- video narration

Never let a judge wonder whether a purchase or search was simulated.

## Required states

### REHEARSAL MODE
Safe, deterministic, no accidental registration.

- fixture domain discovery allowed
- recorded name.com responses allowed
- model evaluation can be live or cached
- registration button should be disabled or require explicit special flag

### LIVE DEMO MODE
Actual name.com sandbox/API credentials.

- real search
- real availability
- real pricing
- explicit approval
- one registration
- DNS create
- DNS read-back
- receipt

Consider requiring something like:

```bash
DOMAINARENA_ALLOW_WRITES=1
```

before registration/DNS write methods execute.

This protects you during rehearsal and demonstrates serious handling of irreversible API actions.

---

# 7. P0 — audit write safety

name.com explicitly rewards good API usage and edge-case handling. The purchase path is where you can show maturity.

Verify all of the following before demo freeze:

## Registration guard

A purchase must require:

- candidate still available
- fresh price known
- fresh renewal price known if provided
- price under user-defined first-year budget
- renewal under renewal budget
- explicit human approval
- decision ID matches approved recommendation
- registration not already completed
- write mode enabled

Fail closed on any ambiguity.

## Idempotency

Ensure clicking approval twice cannot silently buy/register twice.

Persist or memoize a terminal state such as:

```text
RECOMMENDED
PREPARED
APPROVED
REGISTERED
DNS_CONFIGURED
VERIFIED
```

Reject illegal repeated transitions.

## API failure handling

Test deliberately:

- search timeout
- malformed response
- domain unavailable between search and checkout
- price changes between initial ranking and checkout
- purchase budget exceeded
- renewal budget exceeded
- registration API failure
- partial DNS failure
- DNS creation succeeds but readback does not match
- credentials missing
- HTTP 401/403
- HTTP 429
- HTTP 5xx

The product should never invent success.

---

# 8. P0 — one complete name.com lifecycle test

Create a single explicit integration test/script whose only job is to prove:

```text
SEARCH → CHECK → PRICE → APPROVE → REGISTER → DNS WRITE → DNS READ → RECEIPT
```

Prefer a script such as:

```bash
python scripts/live_namecom_smoke.py --domain <sandbox-domain>
```

Output should be concise and machine-readable:

```text
[PASS] search
[PASS] fresh availability
[PASS] pricing
[PASS] budget guard
[PASS] registration
[PASS] DNS create
[PASS] DNS readback
[PASS] receipt hash
```

Do not run this on every CI push because it performs irreversible writes. Keep it as an explicit manual live integration test.

Record the latest successful run in a checked-in sanitized receipt or `docs/LIVE_VERIFICATION.md`.

Do not expose credentials.

---

# 9. P1 — freeze the experimental scoring logic

The actual research differentiation is strong. Do not change the methodology now unless there is a bug.

Canonical comprehension test should remain conceptually:

1. freeze user intent
2. hash frozen intent
3. present domain to tested model with no contextual description
4. ask what product/service the model believes sits behind the domain
5. use a different model/system to evaluate semantic alignment
6. randomize pairwise order when comparing candidates
7. aggregate repeated trials
8. produce confidence/evidence, not one arbitrary score

## Important methodological claims to preserve

- tested model does not score itself
- intent is frozen before candidate evaluation
- presentation order is controlled/randomized
- cross-family testing is supported
- non-determinism is acknowledged
- confidence intervals are used
- evidence has lifecycle states rather than every result being called “confirmed”

Do not overclaim provisional findings as universal laws.

---

# 10. P1 — research extra credit worth surfacing

The previous AgentSEOLab work should be framed as the **research program that produced DomainArena**, not as unrelated legacy work.

Strong findings to surface:

## Description seduction
Some model families selected broken tools when they had more persuasive enterprise-style descriptions.

Implication:
Agent discovery systems can be manipulated by presentation rather than actual capability.

## Contrast-driven selection
When both alternatives receive similar descriptive treatment, apparent preference can collapse.

Implication:
Agents often make relative rather than absolute judgments.

## Serverless nondeterminism
Identical prompts at temperature zero produced materially different choices across time windows.

Implication:
One-shot domain ratings are scientifically weak; DomainArena should replicate across windows/models.

## Position primacy
SERP-style ordering can dominate TLD/name effects.

Implication:
Domain preference tests need position randomization.

## Cross-model heterogeneity
Different model families interpret and select tools differently.

Implication:
A domain cannot really be called “agent legible” based on one model.

## Adversarial decoy resistance
Different models show different robustness to semantic decoys and capability mirages.

Implication:
Agent-native discovery becomes partly a security/evaluation problem.

These findings establish that DomainArena is not just “ask ChatGPT what domain sounds best.”

---

# 11. P1 — make the product/research bridge explicit

Create a short README section:

## Why we built DomainArena

```text
AgentSEOLab research finding          → DomainArena design choice

Model families disagree              → cross-family evaluation
Position biases choices              → AB/BA randomization
Description can seduce models        → blind domain-only inference
Serverless inference drifts          → repeated trials / evidence lifecycle
Relative contrast drives choice      → pairwise arena evaluation
One-shot scores are unreliable       → statistical aggregation
```

This table is extremely valuable because it shows the product architecture emerged from experiments rather than hackathon theatre.

---

# 12. P1 — improve evidence receipt

The final receipt should be the visual payoff of the demo.

Include:

```json
{
  "intent_hash": "sha256:...",
  "decision_id": "...",
  "domain": "...",
  "semantic_score": 0.87,
  "models_tested": ["..."],
  "purchase_price": 12.99,
  "renewal_price": 18.99,
  "approved_by": "human",
  "namecom_registration_status": "REGISTERED",
  "dns_expected": [...],
  "dns_observed": [...],
  "verification_status": "VERIFIED",
  "created_at": "...",
  "receipt_hash": "sha256:..."
}
```

If possible, make the final demo page include:

- domain
- semantic fit score
- price
- approval status
- registration status
- DNS status
- name.com API trace
- receipt hash

A name.com judge should be able to visually see that their API drove the entire transaction.

---

# 13. P1 — API trace panel

Keep / improve the provider trace panel.

For each name.com call show:

```text
METHOD
ENDPOINT / operation
HTTP status
latency
live/fixture
```

Do not expose auth headers or credentials.

Ideal video sequence:

```text
SEARCH             200  182ms
CHECK AVAILABILITY 200  107ms
PRICE              200   94ms
REGISTER           200  241ms
DNS CREATE         200  121ms
DNS READ           200   88ms
```

This is probably the single easiest way to prove integration depth without explaining source code.

---

# 14. P1 — demo should use one fixed intent

Pick one product prompt today and do not improvise during recording.

It should produce candidate names that are intuitively different enough for viewers to understand why semantic testing matters.

Good pattern:

> “An API for AI agents to verify JSON, repair malformed JSON and return the corrected machine-readable result.”

Potential candidates might expose obvious differences such as:

```text
fixjson...
jsonrepair...
agentjson...
```

But use whatever your live name.com search actually returns cleanly.

Requirements:

- inexpensive
- available in sandbox/live environment
- clear semantic contrast
- no trademark issue
- likely stable enough for rehearsal

Record exact chosen input in `DEMO.md`.

---

# 15. P1 — canonical video script

Target: **2:15–2:45**.

No facecam needed.

## 0:00–0:15 — problem

Narration:

> “Domain names were designed for humans. But agents increasingly discover, choose and invoke services themselves. We wanted to know: does an AI agent actually understand what a domain name means?”

Show DomainArena home screen.

## 0:15–0:35 — intent + name.com discovery

Enter frozen demo intent.

Narration:

> “I give DomainArena the product intent and budget. name.com provides the live candidate inventory, availability and pricing.”

Show LIVE badge and name.com search trace.

## 0:35–1:00 — semantic inversion

Show blind model inference for several candidates.

Narration:

> “Instead of asking an LLM whether a domain sounds nice, we remove the product description and ask multiple agents what they think actually lives behind each domain.”

Show one good inference and one poor inference.

## 1:00–1:15 — evidence-based recommendation

Show winner.

Narration:

> “A separate evaluator compares those blind interpretations against the frozen intent. The tested model never scores itself.”

Briefly expose cross-family score / evidence.

## 1:15–1:35 — fresh checkout

Show fresh name.com availability and current price.

Narration:

> “Before any irreversible action, DomainArena checks name.com again. If availability changed, price moved outside budget, or evidence is missing, it fails closed.”

## 1:35–1:50 — human approval

Click approve.

Narration:

> “Recommendation is autonomous. Purchase authority is not. A human approves the final spend.”

## 1:50–2:10 — register + DNS

Show name.com registration and DNS setup.

Narration:

> “name.com registers the selected domain, DomainArena configures DNS, then reads the DNS back instead of assuming the write succeeded.”

## 2:10–2:25 — receipt

Show verified receipt and API trace.

Narration:

> “The result is a verified domain lifecycle: search, measure, approve, acquire, configure and prove.”

## 2:25–2:40 — research/future

Narration:

> “This grew out of 16 experiments across seven-plus model families showing that agents are vulnerable to description bias, position effects and model-specific interpretations. DomainArena is the first step toward measuring agent legibility as a property of internet infrastructure.”

End on receipt / logo.

---

# 16. P1 — rehearse without spending/registering repeatedly

This matters.

Create a safe rehearsal path where:

- Steps 1–5 can be repeated freely.
- Approval can be visually simulated or disabled before actual write.
- registration requires a one-time explicit environment flag.
- DNS operations only run once the intended final registration exists.

Suggested guard:

```bash
DOMAINARENA_ALLOW_WRITES=1
```

Without it:

```text
WRITE BLOCKED — set DOMAINARENA_ALLOW_WRITES=1 to allow name.com registration/DNS writes
```

For tomorrow's recording, rehearse the complete narration several times with writes disabled.

Then enable writes for the intended final take.

---

# 17. P1 — exact clean-clone judge instructions

README quick start should be short.

Example:

```bash
git clone https://github.com/prx0r/agentseolab.git
cd agentseolab
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
python -m domainarena.web.demo
```

Then:

```text
open http://127.0.0.1:8777
```

Document environment variables separately:

```text
NAMECOM_USERNAME=
NAMECOM_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
DOMAINARENA_ALLOW_WRITES=0
```

Judge should be able to run a fixture/replay demo with zero credentials.

Credentials should upgrade it to live mode automatically.

---

# 18. P1 — tests specifically worth showing judges

Do not brag about “148 tests” unless CI proves the exact current number.

Derive and display the current count automatically.

Important test classes:

## name.com client tests

- search response parsing
- pricing parsing
- error handling
- availability
- registration guard
- DNS write/read

## lifecycle tests

- invalid transition rejected
- unavailable domain cannot be purchased
- budget violation blocked
- write without approval blocked
- duplicate purchase blocked
- DNS mismatch produces non-verified receipt

## research tests

- AB/BA randomization
- deterministic seeded ordering
- intent hash stable
- Wilson calculation
- generator/judge separation
- malformed model response -> abstention / not invented score

## package test

Add a CI smoke step before pytest:

```bash
python -c "import domainarena; import domainarena.api.http; import domainarena.providers.namecom; import domainarena.web.demo"
```

This would have caught the current packaging bug immediately.

---

# 19. P2 — Devpost write-up structure

Do not turn the main submission into a research paper.

## Project title
**DomainArena — A/B Testing for Domains in the Agentic Web**

## Elevator pitch
**Measure which domains AI agents actually understand, then safely acquire and configure the winner with name.com.**

## Inspiration

As agents increasingly discover and invoke online services, domain names are no longer read only by people. We found almost no infrastructure for measuring whether AI systems infer the correct purpose from a domain name.

## What it does

DomainArena:

1. searches live domain inventory through name.com,
2. tests what multiple AI models infer from candidate domains without seeing the original description,
3. statistically ranks semantic fit,
4. re-checks availability and price,
5. requires human approval,
6. registers through name.com,
7. configures DNS,
8. verifies DNS read-back and issues an evidence receipt.

## How name.com is central

Explicitly state all six API operations.

Do not bury this.

## What makes it novel

Most domain tools optimize human brandability or ask one LLM for a subjective score. DomainArena uses blind semantic inversion, generator/judge separation, cross-model experiments, order controls and evidence-backed decision receipts.

## Challenges

Mention:

- package reliability
- non-deterministic model inference
- fresh availability between recommendation and checkout
- irreversible purchase safety
- separating recommendation authority from spend authority
- DNS write verification

## Accomplishments

Mention only validated claims:

- six name.com operations in one lifecycle
- verified sandbox/live lifecycle
- research program across 7+ model families
- evidence/replication framework
- MCP interface
- human-gated irreversible action

## What we learned

Use three memorable research findings only:

- models disagree materially
- description/order can bias agent choice
- one-shot LLM scoring is therefore insufficient

## What's next

See startup section below.

---

# 20. P2 — startup / future implications

The future is larger than automatic domain registration.

## 1. Agent-legibility score

Create a standardized measurement for:

> “If an autonomous system sees this domain, how reliably does it infer the intended service?”

Potential users:

- domain registrars
- registries
- startups naming products
- agent marketplaces
- API providers
- SEO/agent-optimization tooling

## 2. Agent-native domain recommendation

Human tools optimize memorability and SEO.

DomainArena could add a new dimension:

```text
human brandability
+ search visibility
+ price
+ trademark risk
+ agent semantic legibility
```

## 3. Registry / TLD intelligence

Test whether `.com`, `.ai`, `.dev`, `.io`, `.xyz`, etc. change how agents infer service intent after controlling for position and wording.

Registries could use this as actual agent-era TLD research.

## 4. Agent discovery security

The AgentSEOLab findings suggest agents can be manipulated by:

- persuasive descriptions
- rank/order
- semantic decoys
- capability mirages
- prerequisite blindness

That points toward a broader security product for measuring how safely agents discover tools and infrastructure.

## 5. Outcome learning

Eventually collect real downstream behavior:

- which domain an agent selects
- whether it calls the service
- whether it returns
- conversion/success

Then train a true empirical “agent legibility” model from deployed outcomes rather than synthetic ratings alone.

## 6. Autonomous business launch

Long-term flow:

```text
business intent
→ domain search
→ agent-legibility testing
→ acquisition
→ DNS
→ hosting/tool configuration
→ machine-readable service description
→ ongoing measurement
```

name.com becomes a natural execution layer for an agent that can launch internet-native products safely.

---

# 21. Things NOT to build before submission

Do not spend time today on:

- new registrars
- blockchain/domain-token integration
- another frontend framework
- elaborate authentication
- billing
- production multi-user database architecture
- autonomous repeated purchases
- dozens of new experiments
- full research-paper publication
- redesigning the core scoring algorithm
- broad SEO functionality

Those all dilute the submission.

---

# 22. Finish-line schedule

## Block A — package repair

- explicit setuptools discovery
- package `__init__.py` markers
- remove stale egg-info
- resolve dangling gitlinks
- clean clone
- Python 3.11 green
- Python 3.12 green

**Exit condition:** GitHub Actions green.

## Block B — lifecycle hardening

- verify state machine
- write guard
- idempotency
- fresh availability check
- fresh pricing check
- DNS read-back
- sanitized live integration receipt

**Exit condition:** one full lifecycle passes intentionally.

## Block C — demo freeze

- fixed intent
- fixed budget
- rehearsal mode
- one planned live domain
- exact commands in `DEMO.md`
- exact narration
- fallback path if Cloudflare inference/provider is slow

**Exit condition:** can rehearse full video with no improvisation.

## Block D — repo presentation

- README rewrite
- `SUBMISSION.md`
- research bridge
- sponsor integration table
- screenshot-ready final receipt
- current test count only

**Exit condition:** judge understands project in <60 seconds from repo landing page.

## Block E — tomorrow

- open clean environment
- run smoke tests once
- rehearse with writes disabled
- start screen recording
- enable write guard only for final live lifecycle
- register
- configure DNS
- show receipt
- upload video immediately
- finish Devpost fields

---

# 23. Final submission acceptance checklist

Do not call DomainArena finished until all are true:

- [ ] Devpost project created
- [ ] name.com challenge selected
- [ ] public repo accessible
- [ ] README has one canonical product story
- [ ] clean clone works
- [ ] editable install works
- [ ] Python 3.11 CI green
- [ ] Python 3.12 CI green
- [ ] current test count derived from CI, not stale docs
- [ ] no secrets committed
- [ ] no stale egg-info
- [ ] no dangling submodule warnings
- [ ] fixture/rehearsal demo works without credentials
- [ ] live mode clearly labelled
- [ ] write operations require explicit approval
- [ ] duplicate registration protected
- [ ] fresh availability checked before purchase
- [ ] fresh price checked before purchase
- [ ] DNS is read back after write
- [ ] final receipt clearly displays name.com lifecycle
- [ ] one verified integration run recorded/sanitized
- [ ] `DEMO.md` has exact recording path
- [ ] research section distinguishes CONFIRMED vs PROVISIONAL findings
- [ ] old AgentSEO work clearly marked as research/legacy rather than current product
- [ ] 2–3 minute video recorded
- [ ] Devpost explanation explicitly names all six name.com operations

---

# Bottom line

DomainArena is not far from submission. The interesting work is already done.

The highest-value remaining change is **not another feature**. It is converting a research-heavy repo that works in the development environment into a judge-proof product that installs cleanly and demonstrates one undeniable lifecycle:

> **intent → live name.com inventory → agent comprehension experiment → evidence-backed recommendation → fresh checkout → human approval → registration → DNS → verified receipt**

The extra-credit research gives the project its originality. The six-part name.com lifecycle gives it sponsor depth. The approval/write guards give it technical credibility.

Get those three things visually obvious, and this becomes a very strong name.com submission.
