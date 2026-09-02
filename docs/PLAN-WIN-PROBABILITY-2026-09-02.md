# DomainArena — Highest-Win-Probability Finish-Line Plan

**Target:** DevNetwork API + Cloud + AI Hackathon 2026 — **name.com Domain API Challenge**

**Repository:** https://github.com/prx0r/agentseolab

## Executive decision

Do **not** add another generic domain-search feature.

The strongest possible submission is:

> **DomainArena — A/B testing for domain names in the agentic web.**
> Measure which available domain AI agents actually understand, then acquire and configure the empirically strongest candidate through name.com.

And the above-and-beyond research layer should become:

> **Agent Legibility Lab / DomainBench** — a reproducible benchmark and interactive research exhibit measuring how domain names affect agent comprehension, preference, robustness, and tool selection.

This gives the entry the same “there is a real product, and beneath it is a serious research lab” effect that we want from ProofDesk + AuthorityBench.

The important current-market comparison is now extremely favorable. Cloudflare has spent 2026 explicitly defining the **Agentic Internet** as readable, discoverable, callable and payable; launched **Agent Readiness** to test whether an existing site can be discovered/read/called by agents; launched **AEO Visibility** to measure whether AI assistants recommend a deployed brand; and launched a Registrar API so agents can search/check/register domains. Meanwhile AgentDNS, ANS, DNS-AID, ToolDNS and current academic work are converging on DNS/domain infrastructure as a discovery and identity substrate for agents.

That means the missing layer is increasingly obvious:

> **Before the website exists, before Agent Readiness, before AEO visibility, and before an agent registers the domain: which hostname should the machine audience see?**

That is DomainArena.

It should be presented as **pre-deployment optimization for the machine audience**, not merely automated registration.

---

# 1. Latest push — current judge review

The latest push `3f551191` materially improved the submission:

- strong one-line pitch: “A/B testing for domain names in the agentic web”
- clearer name.com lifecycle diagram
- explicit six-capability sponsor integration
- fixed demo intent
- write guard documentation
- rehearsal/final recording modes
- 2:15–2:40 video script
- honest fallback for inference
- stronger safety language

The repo is much more coherent than the earlier AgentSEOLab incarnation.

However, **it is not submission-pristine yet**.

## P0-1 — CI is still red

Latest GitHub Actions run on `3f551191` fails in Python 3.11 and cancels 3.12.

The immediate error:

```text
ModuleNotFoundError: No module named 'cogym_kernel'
```

`domainarena/world.py` imports:

```python
from cogym_kernel.kernel.contracts import (
    ActionResult,
    ActionSpec,
    CandidateArtifact,
    Metric,
    MetricVector,
    RunReceipt,
    WorldSpec,
)
```

That dependency exists in your local environment but is neither packaged nor installed by `pip install -e ".[dev]"`.

This is exactly the kind of hidden-local-state failure judges punish because the README claims 148 tests passing while a clean GitHub runner cannot even collect the full suite.

### Fix

Choose one clean approach today:

**Preferred hackathon approach:** make DomainArena self-contained.

Create a tiny internal compatibility module containing the exact world-contract types DomainArena uses, e.g.:

```text
domainarena/worldpack/contracts.py
```

If these are your own Cogym contracts, copy the minimal required dataclasses/interfaces with provenance. Then:

```python
from domainarena.worldpack.contracts import ...
```

Do not require a sibling repo or `/root/...` import for the public hackathon package.

Alternative only if Cogym is actually installable from a stable public package/repo: declare it explicitly in dependencies. But I prefer self-contained because the judge path must not depend on another evolving repo.

### Acceptance

```bash
rm -rf /tmp/domainarena-clean
git clone https://github.com/prx0r/agentseolab /tmp/domainarena-clean
cd /tmp/domainarena-clean
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -c "import domainarena; import domainarena.world"
pytest -q
```

Must pass on 3.11 and 3.12.

---

# 2. P0-2 — purge the broken upstream gitlinks

CI checkout still prints:

```text
fatal: No url found for submodule path 'research/upstream/AgentSearchBench' in .gitmodules
```

`research/upstream/` currently contains multiple zero-size gitlink-style entries such as:

```text
AgentSearchBench
FastChat
agentic_geo
alpaca_eval
arena
arena-rank
domain-search-agent
domain-search-mcp
domains
search-arena
...
```

The clean runner checked out ~19,484 paths. This is unnecessary archaeology in the submission surface.

### Fix

Delete dangling gitlinks from canonical Git history/tree.

Keep:

```text
research/upstream/SOURCE_LEDGER.md
```

Expand that ledger to contain:

```text
project
repository URL
commit SHA examined
license
what idea/code informed DomainArena
whether any code was copied
```

If you genuinely vendor code, vendor it intentionally with license and no fake submodule state.

### Desired effect

Clean checkout:

```text
0 submodule warnings
0 orphan gitlinks
no mystery upstream repos
```

This will also make the repo feel dramatically more intentional.

---

# 3. P0-3 — CI must test the same thing README claims

`pyproject.toml` says:

```toml
[tool.pytest.ini_options]
testpaths = ["tests", "domainarena"]
```

but GitHub Actions explicitly runs:

```bash
pytest tests/ -v --tb=short
```

The failing runner collected 133 tests before the world import error, while README says 148.

That means the CI command and local command are currently testing different surfaces.

### Fix

Use one canonical command everywhere:

```bash
pytest -q
```

Then derive the public test count from the actual CI run after all failures are fixed.

Better workflow:

```yaml
- name: Import smoke
  run: |
    python -c "import domainarena"
    python -c "import domainarena.api.http"
    python -c "import domainarena.providers.namecom"
    python -c "import domainarena.web.demo"
    python -c "import domainarena.world"

- name: Test
  run: pytest -q
```

Add a wheel/package test too:

```bash
python -m build
pip install dist/*.whl
python -c "import domainarena"
```

Editable installs can hide packaging problems. A wheel install proves the distributable package is real.

---

# 4. P0-4 — clean the top-level repo

The root still exposes too much development archaeology:

```text
DOMAININTEL.md
EXPERIMENT_LOG.md
HACKATHON_NORTHSTAR.md
HANDOVER-2026-08-25.md
HANDOVER-2026-08-30.md
P0_REVIEW.md
PEER_REVIEW_2026-08-23.md
PLAN-FINISH-LINE-2026-09-02.md
...
```

None of these are inherently bad, but a judge should see the **product hierarchy**, not your entire internal history.

### Canonical root

Aim for:

```text
README.md
DEMO.md
RESEARCH.md
HACKATHON_SUBMISSION.md
LICENSE
.env.example
pyproject.toml
Dockerfile

domainarena/
experiments/
analysis/
research/
results/
tests/
docs/
```

Move handovers/peer reviews/old planning into:

```text
docs/archive/
```

The research is a strength. Development clutter is not.

---

# 5. Verify the name.com integration against current CORE docs

The current code is already doing several things correctly that should be explicitly celebrated:

- CORE API base URL
- Search
- CheckAvailability
- `purchaseType=registration`
- pricing
- idempotency key on CreateDomain
- registration
- DNS create
- DNS read-back
- retry/backoff on 429
- fail-closed malformed availability handling
- sandbox/write modes

Current name.com docs explicitly recommend `purchaseType=registration` to avoid aftermarket/non-instant purchase types and explicitly recommend `X-Idempotency-Key` on create. Keep both in the demo/pitch because they prove you read the real operational docs rather than just calling an endpoint.

Official docs:
- https://docs.name.com/api/v1/overview
- https://docs.name.com/api/v1/reference/domains/search
- https://docs.name.com/api/v1/reference/domains/check-availability
- https://docs.name.com/guides/quickstart
- https://docs.name.com/guides/testing-environment

## Sandbox truthfulness

Important: name.com explicitly says sandbox DNS create/read works through the API, but sandbox records **do not resolve publicly**.

Therefore narration should say:

> “In name.com sandbox, DomainArena writes the DNS configuration and then reads it back through the API to verify that the intended state was stored. Production uses the same lifecycle against live DNS.”

Do **not** imply the sandbox hostname is publicly resolving.

## `.env.example`

Make it unambiguous:

```bash
# name.com sandbox
NAMECOM_USERNAME=yourusername-test
NAMECOM_TOKEN=
NAMECOM_BASE_URL=https://api.dev.name.com
NAMECOM_MODE=sandbox
DOMAINARENA_ALLOW_WRITES=0
```

And production-readonly example separately.

name.com docs specifically require the `-test` username plus sandbox token.

---

# 6. The frontier comparison — this is the strategic pitch

## Cloudflare Agent Readiness — April 2026

Cloudflare’s Agent Readiness score asks whether an **existing hostname/site** supports things such as:

- robots.txt
- sitemap.xml
- Link headers
- Markdown content negotiation
- Content Signals
- Web Bot Auth
- API Catalog
- OAuth discovery
- MCP Server Cards
- Agent Skills
- WebMCP

Cloudflare describes the new web as one where agents must be able to find, read and call services.

Source: https://blog.cloudflare.com/agent-readiness/

## Cloudflare AEO Visibility — August 2026

Cloudflare has now moved one step further: after a site exists, measure whether assistants actually **mention/recommend** it for relevant questions.

Source: https://blog.cloudflare.com/aeo/

## Cloudflare Registrar API — April 2026

Cloudflare can already let an agent:

```text
search → check → register
```

from an editor/MCP workflow.

Source: https://blog.cloudflare.com/registrar-api-beta/

### DomainArena’s exact gap

Therefore do not say:

> “Nobody lets an AI agent register domains.”

That is now false.

Say:

> **“Registrars can already let agents buy a domain. Agent-readiness products can tell you whether a deployed site is machine-friendly. DomainArena addresses the decision before both: which available domain will agents correctly understand and prefer before you commit the brand?”**

That is much stronger because it uses the frontier to validate the category while maintaining a clear wedge.

---

# 7. DNS/agent discovery research makes this more important, not less

The literature is converging strongly on DNS as agent infrastructure.

## AgentDNS — 2025

AgentDNS proposes DNS-inspired cross-vendor service discovery for LLM agents.

https://arxiv.org/abs/2505.22368

## Discovering Agents for Discovery: The Case for DNS — June 2026

Uses 119,757 real service endpoints and argues DNS is a suitable substrate for Internet-scale agent discovery, including metadata/trust needs and millisecond-level lookup properties.

https://arxiv.org/abs/2606.02314

## ToolDNS — 2026

“AI Tool Discovery at Scale: All You Need is DNS” builds a benchmark with 33,688 real tools across MCP/A2A/REST/Skill protocols and studies DNS-based semantic pruning.

https://arxiv.org/abs/2607.18242

## ANS / DNS-AID

GoDaddy, Cloudflare and Infoblox are actively backing DNS-based agent identity/discovery standards. ANS uses domain ownership + DNS/PKI to establish agent identities; DNS-AID focuses on publishing capability/endpoint metadata.

This is a critical strategic validation:

> **The hostname is becoming machine infrastructure, not merely human branding.**

DomainArena asks whether the *human-readable name layer itself* communicates the right meaning to models.

That is your long-term research/startup wedge.

---

# 8. Tool-selection frontier also directly validates your old AgentSEOLab findings

Two particularly relevant papers:

## BiasBusters — 2025

Shows LLM tool selection is biased; semantic alignment between query and metadata is a strong predictor, description perturbations materially shift selection, and position/provider effects appear.

https://arxiv.org/abs/2510.00307

## ToolTweak — 2025

Shows adversarial name/description modifications can boost a tool’s selection rate dramatically, with transfer across models.

https://arxiv.org/abs/2510.02554

Also relevant:

## Agent-Facing Information Design in LLM Tool Registries — 2026

17,700+ trials across five LLMs / ten domains; argues tool registries function like advertising markets and proposes measurement/normalization rather than trusting provider copy.

https://arxiv.org/abs/2605.23916

## ToolFlood — 2026

Shows adversarial metadata can dominate semantic retrieval and push valid tools out of top-k.

https://arxiv.org/abs/2603.13950

### Why this helps DomainArena

Your “description seduction,” contrast effects and position primacy are not random experiments anymore. They sit inside an emerging research area showing that **machine choice surfaces are manipulable**.

But do not claim you invented tool-selection bias.

Instead say:

> “Our research independently encountered the same broader phenomenon now being documented in tool-selection research: agent choice is sensitive to presentation and metadata. DomainArena isolates one under-measured variable in that ecosystem — the hostname itself — and converts measurement into a real registration decision.”

That is scientifically defensible and current.

---

# 9. Build the ProofDesk-equivalent research artifact: **Agent Legibility Lab**

This is the one major stretch feature I would add.

Routes:

```text
/lab
/research
```

Name options:

- **Agent Legibility Lab** — best user-facing name
- **DomainBench** — best benchmark name
- **AgentLegibilityBench** — best paper name

Recommended combination:

> **DomainBench — the benchmark**
> **Agent Legibility Lab — the interactive interface**

The product remains **DomainArena**.

---

# 10. Separate the scientific tasks properly

Right now some wording risks conflating different questions.

Create four explicit tasks.

## DA-C — Blind comprehension

Model sees only:

```text
fixjson.dev
```

Question:

> What service do you think is behind this domain?

Hidden scorer compares inference to frozen product intent.

Measures:

```text
semantic transmission
```

This is your most distinctive task.

## DA-P — Pairwise preference

Model sees:

```text
Product: API for repairing malformed JSON

fixjson.dev
jsonrepair.ai
```

AB/BA randomized.

Question:

> Which would you choose?

Measures:

```text
choice preference
```

Your existing runner already supports this with frozen intent hash, AB/BA order, multiple model families, Wilson intervals and evidence hashes.

## DA-R — Robustness

Repeat the same candidates under controlled variation:

```text
position/order
prompt paraphrase
model family
time window
TLD
hyphenation
word order
```

Measures:

```text
stability / sensitivity
```

## DA-X — Execution-grounded choice

This is the strongest new experiment.

Expose two functionally identical tools/services to an agent:

```text
same capability
same schema
same description
same latency fixture
same output quality
DIFFERENT PROVIDER DOMAIN
```

Ask the agent to solve the task and record which provider it actually calls.

This answers:

> **Does hostname semantics transfer from stated preference into real tool invocation?**

That connects DomainArena to BiasBusters/ToolTweak but isolates the domain identity variable.

Label this experimental until actually measured.

---

# 11. Implement multi-candidate Bradley–Terry now

README currently marks Bradley–Terry planned.

This is one stretch algorithm worth implementing because it directly improves both product and science.

name.com Search returns multiple candidates. A real arena should not reduce them to one arbitrary pair.

For top `k=4–6` feasible domains:

```text
all/balanced pairings
× 3 model families
× AB/BA randomized trials
```

Fit Bradley–Terry latent strengths:

```text
P(i beats j) = exp(s_i) / (exp(s_i) + exp(s_j))
```

Output:

```text
Domain             BT strength      95% bootstrap CI
fixjson.dev        1.42             [1.16,1.73]
jsonrepair.ai      0.81             [0.64,1.03]
repairjson.dev     0.40             [0.28,0.58]
...
```

Then recommendation is no longer:

> “LLM scored this one 0.84.”

It becomes:

> “Across randomized pairwise trials and three model families, this domain has the strongest estimated selection propensity.”

That is a large quality jump.

---

# 12. Create a real **Agent Legibility Card**

Every live candidate should get a structured card:

```text
fixjson.dev

name.com
  available           YES
  first-year          $X
  renewal             $Y
  premium             NO

Agent legibility
  blind comprehension       0.88
  pairwise preference       67%
  cross-family agreement    3/3
  order robustness          PASS
  prompt robustness         PASS
  temporal stability        0.91

Evidence
  measured dimensions       5/6
  proxy dimensions          1/6
  n                         180
  evidence hash             sha256:...

Recommendation
  VALIDATED
```

Do not hide uncertainty behind one arbitrary “AI score.”

Show each dimension and evidence status.

If you want one summary score, call it **Agent Legibility Index**, but only compute it from measured dimensions and publish the formula.

---

# 13. Interactive Lab — the visual wow factor

The equivalent of ProofDesk’s Trust Lab should be an **interactive experiment explorer**, not a decorative dashboard.

## Hero

> # Do AI agents understand your domain?
> Explore controlled experiments across model families, TLDs, position, descriptions and domain names.

## Panel 1 — Semantic inversion

Judge types:

```text
jsonrepair.dev
```

Show responses from:

```text
Llama
Mistral
Qwen
```

Then frozen target intent and separate scorer results.

The visual point:

> Same hostname. Different machine interpretations.

## Panel 2 — Pairwise arena

Two domain cards physically face each other:

```text
fixjson.dev   VS   jsonrepair.ai
```

Display:

```text
Llama       14–6
Mistral     11–9
Qwen        15–5

pooled      40–20
Wilson CI   ...
```

Toggle:

```text
[AB] [BA]
```

so the judge sees you controlled order effects.

## Panel 3 — Model-family disagreement

Heatmap:

```text
                   Llama   Mistral  Qwen  Gemma  ...
fixjson.dev        ...
jsonrepair.ai      ...
...
```

This makes the “there is no universal AI consumer” insight visually obvious.

## Panel 4 — Robustness toggles

```text
TLD        .com .dev .ai .io .xyz
Position   1 2 3 4 5
Context    name-only / task-visible / description-visible
Window     run A / run B
```

Show measured choice shift.

## Panel 5 — Name.com frontier

This should be the hero sponsor graph.

Scatter plot:

```text
x = annual/renewal cost
y = measured agent legibility
bubble/opacity = confidence/stability
```

Now name.com pricing is not a checkout footnote — it directly enters the optimization problem.

A candidate can be:

```text
more machine-legible but too expensive
cheaper but semantically weak
strong and robust but premium renewal
Pareto-optimal
```

This is the **economics + semantics frontier**.

---

# 14. Add a Cloudflare-frontier comparison panel

A tiny static section in `/lab` or README:

```text
                    BEFORE LAUNCH        AFTER LAUNCH

DomainArena         Which domain         —
                    will agents
                    understand?

Agent Readiness     —                    Can agents discover,
                                         read and call the site?

AEO Visibility      —                    Do assistants recommend it?
```

Then:

```text
DomainArena → name.com acquisition → Agent Readiness → AEO measurement
```

This is an excellent startup roadmap and prevents a judge from thinking Cloudflare invalidates the project.

Cloudflare actually validates your timing.

---

# 15. Add **Agent-Ready Launch** as a small post-registration extension — not a new product

Do not build a whole hosting platform.

But after DNS registration, generate a machine-readable launch checklist/artifact showing what the new site should publish next:

```text
robots.txt
sitemap.xml
llms.txt
Accept: text/markdown
/.well-known/mcp/server-card.json
/.well-known/agent-skills/index.json
/.well-known/api-catalog
WebMCP support
Web Bot Auth / agent identity
```

Call it:

> **Agent-Ready Launch Manifest**

This connects the chosen domain to the rest of the 2026 agentic-web stack without competing with Cloudflare.

Keep it generated/documented unless implementation is trivial.

Optional wow move: use name.com DNS to create one **TXT metadata record** for the DomainArena experiment receipt or future agent identity pointer, then read it back.

Example concept:

```text
_domainarena TXT "v=1; evidence=sha256:..."
```

Do **not** present this as a standard. Label it a DomainArena provenance record.

Longer-term, mention ANS/DNS-AID/SVCB integration as future standards work.

Do not fake ANS compliance unless actually implemented against the current spec.

---

# 16. Research paper / technical preprint

You already have an `analysis/paper_pack.py` that generates methods/results from experiment artifacts. This is an excellent foundation.

But it currently hardcodes paths like:

```python
ROOT = "/root/agentseolab"
```

Fix all research tooling to be repo-relative.

Create:

```text
research/paper/
  main.tex
  references.bib
  figures/
  tables/
```

Suggested title:

> **Names for the Machine Audience: Measuring Domain Legibility in LLM Agents**

Subtitle:

> **DomainBench: A Controlled Benchmark of Hostname Comprehension, Preference and Selection Bias**

Paper structure:

```text
Abstract
1. Introduction
2. The agentic web and the hostname problem
3. DomainBench
4. Experimental controls
5. Blind semantic comprehension
6. Pairwise selection
7. Position/TLD/context effects
8. Cross-family and temporal instability
9. Execution-grounded tool choice
10. DomainArena + live registration
11. Limitations
12. Related work
13. Conclusion
```

Keep it 6–9 pages.

Call it a **technical preprint** unless actually submitted to arXiv.

---

# 17. Every research figure must come from committed artifacts

No hand-written “illustrative” result graphs in the scientific layer.

Every run should save:

```json
{
  "run_id": "...",
  "git_sha": "...",
  "timestamp": "...",
  "intent_hash": "...",
  "candidate_hash": "...",
  "protocol_version": 2,
  "models": [...],
  "seed": 20260831,
  "temperature": 0,
  "time_window": "...",
  "raw_results_hash": "..."
}
```

Then:

```bash
make research
make figures
make paper
```

A judge should be able to regenerate the figures from JSON.

The research artifacts themselves should have hash receipts.

---

# 18. Best figure set

Only produce figures that tell a story.

## Figure 1 — DomainArena lifecycle

```text
INTENT → name.com inventory → agent trials → evidence → fresh checkout → approval → register → DNS → receipt
```

## Figure 2 — Cross-family semantic heatmap

Domain × model-family comprehension.

## Figure 3 — Pairwise preference forest plot

For candidate comparisons, show selection rate + Wilson 95% CI.

## Figure 4 — Position/TLD interaction

This is especially strong given your current position-primacy result.

## Figure 5 — Temporal instability

Same prompt/model/candidates across time windows.

Do not just show two anecdotal percentages. Add repeated windows if possible.

## Figure 6 — Agent Legibility Frontier

```text
cost vs measured legibility
```

with name.com pricing.

## Figure 7 — Tool execution choice

Preference vs actual invocation rate.

If DA-X isn't completed, omit it rather than inventing it.

## Figure 8 — Evidence lifecycle

```text
PROPOSED → PREREGISTERED → RUNNING → PROVISIONAL → CONFIRMED → REPLICATED
```

with counts of current hypotheses in each status.

---

# 19. Scientific claim hygiene

Your RESEARCH.md is already much better than typical hackathon research because it distinguishes CONFIRMED and PROVISIONAL.

Keep tightening.

## “First benchmark” claim

README currently says:

> “This is the first benchmark that asks: given only a domain name, can an AI model infer what service runs behind it?”

That may be true, but it is hard to prove comprehensively.

Safer:

> “DomainBench directly evaluates whether an AI model can infer a service’s intended function from a hostname alone.”

Or:

> “We have not found an existing benchmark focused specifically on hostname-only semantic comprehension.”

The second is strong but defensible.

## Position result

“87% pick slot 0” should always carry:

```text
n
model set
time window/protocol
status=PROVISIONAL
```

## Serverless non-determinism

Do not imply Cloudflare itself is broken.

Say:

> “Repeated temperature-zero calls to serverless model endpoints exhibited material output instability across observation windows in our protocol.”

The source could be model/runtime/backend versioning or other nondeterminism.

## Description seduction

The new literature means this result is now well contextualized. Position it as independent evidence and a foundation for hostname-specific study, not singular discovery of the entire phenomenon.

---

# 20. The name.com-specific demo should be even more obvious

Official challenge judges explicitly favor multiple endpoints and grade:

1. API integration depth
2. creativity/originality
3. technical execution
4. real-world viability
5. presentation/demo

Your product can hit all five directly.

## Integration depth

Show the **actual lifecycle trace** in one collapsible panel:

```text
name.com CORE

POST domains:search                  200   312ms
POST domains:checkAvailability       200   184ms
GET  domains/x:getPricing            200   151ms
POST domains                         200   402ms
POST domains/x/records               200   133ms
GET  domains/x/records               200   120ms
```

Sanitize auth.

The judge should not have to trust narration.

## Creativity

The API isn't being used for a domain-store clone.

It creates the live experimental candidate pool and commits the result of a scientific agent-selection process.

## Technical execution

Expose:

```text
fail-closed availability
purchaseType registration
price drift
renewal budget
approval token
write guard
idempotency
DNS readback
evidence hashes
cross-family judge separation
```

## Viability

Pitch customers:

```text
AI-native startups
registrars
TLD registries
brand agencies
agent marketplaces
API companies
AEO platforms
```

## Presentation

Use one story. No repo archaeology.

---

# 21. Revised 2:40 demo — stronger than current script

## 0:00–0:15 — Current-market hook

> “Cloudflare can now tell you whether a site is agent-ready after launch. Registrars can let an agent buy a domain. But there is an earlier unanswered question: which domain should the agent buy?”

Screen: DomainArena.

> “DomainArena A/B tests available domains on the machine audience before you commit the brand.”

This is immediately differentiated.

## 0:15–0:35 — live name.com candidate market

Enter fixed JSON repair intent and budgets.

Show `LIVE name.com`.

> “name.com provides the candidate market: real availability, first-year price and renewal price.”

Show API trace very briefly.

## 0:35–1:00 — blind semantic inversion

Open two candidates.

> “We remove the product description and ask multiple agents what they think each hostname means. A separate model compares the answer against a frozen intent; the tested model never judges itself.”

Show model disagreement if possible.

## 1:00–1:20 — arena / research

Show pairwise result + CI or multi-candidate leaderboard.

> “We randomize order, repeat across model families and keep the evidence. This is measured selection behavior, not an LLM vibe score.”

If Bradley–Terry is ready, show it.

## 1:20–1:32 — Research Lab flash

Open Agent Legibility Lab.

Show one heatmap and the cost/legibility frontier.

> “This grew out of sixteen controlled experiments on agent choice, including description bias, position effects and cross-model instability.”

Do not explain all sixteen.

## 1:32–1:52 — fresh checkout

Click winner.

> “The research result is not enough to buy. DomainArena asks name.com again immediately before purchase. Availability, registration price, renewal price and purchase type must still satisfy the frozen policy.”

## 1:52–2:06 — human approval

> “Selection can be autonomous. Spend authority is explicitly human.”

Click approve.

## 2:06–2:25 — registration + DNS

Show name.com CreateDomain, then CreateRecord and read-back.

> “name.com registers the winner, DomainArena configures DNS, and then reads the state back through the API instead of assuming the write worked.”

Explicit sandbox note in small badge:

```text
NAME.COM SANDBOX — no real charge / no public DNS resolution
```

## 2:25–2:36 — receipt

Show:

```text
intent hash
experiment evidence hash
approved price
registration/order
DNS read-back
receipt hash
```

> “The final receipt connects the brand decision to the evidence and the live domain lifecycle.”

## 2:36–2:45 — future

> “As the web becomes readable, discoverable and callable by agents, domain names become machine-facing infrastructure. DomainArena measures that layer before launch.”

Done.

---

# 22. Build the exact demo fixture now

Fixed intent remains good:

> “An API for AI agents to verify JSON, repair malformed JSON and return the corrected machine-readable result.”

But do one live rehearsal today and verify name.com actually returns candidates under the current TLD/budget filters.

Freeze:

```text
intent
budget
TLD filters
candidate count
chosen sandbox registration target
DNS record payload
```

Do **not** rely on a specific live search result still being available tomorrow.

Fallback plan:

1. show a genuine live name.com Search call
2. if desired demo candidates aren't returned, use a captured/signed candidate set for semantic trials
3. perform fresh availability/price check on the chosen sandbox domain before registration
4. label every replay/fixture surface explicitly

No fake “LIVE” labels.

---

# 23. Make the research page a Devpost screenshot factory

Capture five screenshots:

1. **Live name.com candidate market**
2. **Blind agent comprehension / cross-family disagreement**
3. **Pairwise arena with confidence intervals**
4. **Agent Legibility Frontier: price vs measured legibility**
5. **Verified name.com registration + DNS receipt**

These five images alone explain the entire product.

---

# 24. README rewrite — final canonical hierarchy

Above the fold:

```text
# DomainArena
A/B testing for domain names in the agentic web.

[Demo] [Agent Legibility Lab] [Research] [Reproduce]

Live name.com inventory
→ blind agent comprehension
→ cross-family A/B testing
→ evidence-backed recommendation
→ fresh checkout
→ human approval
→ registration
→ DNS verification
```

Then immediately:

## Why now

Use current frontier:

> Cloudflare now measures Agent Readiness and AEO visibility after deployment, while agent registrars can make domains programmatically purchasable. DomainArena addresses the decision before deployment: whether the hostname itself transmits the intended meaning to agents.

Then sponsor integration.

Then demo.

Then research.

Then safety.

Then architecture.

Then limitations.

Move detailed historical findings lower down or into RESEARCH.md.

---

# 25. Devpost one-line pitch

Best version:

> **DomainArena A/B tests live name.com domains on AI agents, measures which hostname they actually understand, then safely registers and configures the evidence-backed winner.**

Alternative shorter:

> **A/B testing for domain names in the agentic web — measure what AI agents understand, then acquire the winner with name.com.**

---

# 26. Devpost problem statement

Use this core argument:

> Domains have always been optimized for human memory, trust and search behavior. But agents are becoming a second audience: they discover services, choose tools and increasingly act on users’ behalf. Cloudflare’s 2026 Agent Readiness and AEO products already measure whether deployed sites can be consumed and recommended by agents, while new DNS-based agent-discovery standards make hostnames part of machine infrastructure. Yet domain selection is still mostly intuition. DomainArena turns it into an experiment.

Then:

> It starts with live name.com inventory, runs blind semantic-comprehension and randomized selection trials across model families, keeps statistical evidence and only then allows a human-approved name.com registration. DNS is configured and read back through the API, producing a verifiable receipt from intent to infrastructure.

---

# 27. “Why name.com does the real work” paragraph

Even though name.com does not require the Nutrient-style one-line explanation, make it explicit:

> **name.com is DomainArena’s live market and execution layer. Search and availability define the candidate set; pricing and renewal data define which candidates are feasible; a fresh availability/pricing check protects the recommendation at checkout; CreateDomain turns the experiment winner into owned infrastructure; and DNS create/read-back verifies that the domain was actually configured. Without name.com, DomainArena would be an offline naming benchmark rather than an end-to-end product.**

That directly addresses integration depth.

---

# 28. Real-world business story

Do not pitch only to people naming hobby projects.

The larger product is:

> **machine-audience brand testing.**

Potential customers:

### Registrars

Add an “Agent Legibility” dimension to search results.

Instead of:

```text
available
price
premium
```

also:

```text
machine comprehension
cross-model robustness
agent preference
```

### TLD registries

Measure whether `.dev`, `.ai`, `.io`, `.com`, `.xyz`, etc. alter agent interpretation for different task categories.

### AI-native startups

Before buying their identity, test it against the audience that will actually discover/call them.

### Brand agencies

A/B test human branding and machine branding separately.

### Agent marketplaces / directories

Measure how names, descriptions and positions alter selection fairness.

### AEO platforms

DomainArena becomes the **pre-launch** layer feeding into post-launch Agent Readiness and AEO measurement.

---

# 29. Strong long-term moat

Every experiment can become a growing dataset:

```text
intent
candidate hostname
TLD
position
prompt condition
model family
model version
time window
semantic inference
pairwise choice
tool invocation
name.com availability
price
renewal price
later deployed outcomes
```

Over time you can answer things nobody can answer from generic language-model priors:

```text
Which lexical structures transfer across model families?
Which TLDs help/hurt particular agent tasks?
Which names are robust to model upgrades?
Which names look semantically good but lose actual tool selection?
Does agent-legible naming correlate with AEO recommendation later?
```

That becomes the data asset.

---

# 30. Reproducibility commands

Add a Makefile:

```text
make install
make test
make demo
make research-smoke
make figures
make paper
make clean-clone-check
```

`make research-smoke` should use committed evidence and require no external credentials.

`make research-live` can require Cloudflare.

`make namecom-smoke` can require sandbox credentials.

Every external mode must clearly say LIVE/SANDBOX/REPLAY.

---

# 31. Security and write-path checks

Before recording, explicitly test:

```text
writes disabled → register = denied
writes disabled → DNS create = denied
missing approval → register = denied
stale/used approval token → denied
availability false → denied
availability malformed → denied
purchaseType != registration → denied
purchase price > budget → denied
renewal price > budget → denied
price drift > policy → approval invalidated
duplicate CreateDomain retry with same idempotency key → safe
DNS create succeeds → list/read-back contains expected record
DNS create fails → receipt not VERIFIED
```

Also inspect provider traces to guarantee Basic Auth is never displayed.

Run:

```bash
git grep -Ei '(token|secret|authorization|basic |api[_-]?key)'
```

and manually inspect every result.

---

# 32. Today’s exact execution order

## Gate A — repo integrity

1. Remove hidden `cogym_kernel` dependency.
2. Delete dangling `research/upstream` gitlinks.
3. Run fresh clone.
4. Run `pip install -e ".[dev]"`.
5. Run canonical `pytest -q`.
6. Make both 3.11 + 3.12 GitHub Actions green.
7. Update test count only after CI is green.

**Do nothing presentation-heavy until this gate passes.**

## Gate B — name.com lifecycle

1. Confirm current CORE sandbox credentials.
2. Confirm username uses `-test` convention.
3. `GET /hello` smoke.
4. live Search.
5. CheckAvailability with `purchaseType=registration`.
6. getPricing.
7. create sandbox domain with idempotency key.
8. DNS create.
9. DNS read-back.
10. save sanitized trace/receipt.

## Gate C — research upgrade

1. Package the existing DA-C + DA-P results cleanly.
2. Implement Bradley–Terry for top 4–6 candidates.
3. Generate cross-family heatmap.
4. Generate pairwise forest plot.
5. Generate price × legibility frontier using live name.com price snapshots.
6. If time permits, run DA-X identical-tool execution experiment.

## Gate D — Agent Legibility Lab

Build `/lab` from **precomputed real artifacts**.

Do not make the judge wait for 100 model calls.

One button can optionally rerun a small live trial.

## Gate E — preprint

1. Fix repo-relative paper tooling.
2. Generate methods/results from artifacts.
3. Create 6–9 page technical preprint.
4. Link it from README.
5. Do not submit to arXiv unless trivial; the repo PDF is enough for the hackathon.

## Gate F — presentation

1. Rehearse exact fixed intent.
2. Freeze browser tabs.
3. Verify write guard off during rehearsals.
4. Capture screenshots.
5. Record 2:40 demo.
6. Upload video immediately.
7. Finish Devpost prose after video is safe.

---

# 33. If time is tight, cut in this order

Do **not** cut:

```text
CI green
clean clone
live name.com Search
fresh availability/pricing
sandbox registration
DNS create/read-back
research screenshot
credible Devpost story
```

Next priority:

```text
Bradley–Terry
Agent Legibility Lab
price × legibility frontier
```

Then:

```text
technical preprint
DA-X execution experiment
Agent-Ready Launch manifest
```

Do not burn time on another unrelated feature.

---

# 34. Definition of pristine

Submission is ready only when:

```text
[ ] Latest GitHub Actions green on 3.11 and 3.12
[ ] No hidden cogym sibling dependency
[ ] No dangling gitlinks/submodule warnings
[ ] Fresh wheel/import test succeeds
[ ] README test count equals CI result
[ ] Root repo is clean and intentional
[ ] Fixture demo works without credentials
[ ] Live semantic experiment clearly labelled LIVE
[ ] name.com sandbox search works
[ ] CheckAvailability uses purchaseType=registration
[ ] fresh pricing checked before purchase
[ ] budget and renewal policy enforced
[ ] writes gated
[ ] registration uses idempotency key
[ ] DNS configuration written and read back
[ ] sandbox non-public-DNS limitation stated honestly
[ ] auth never exposed in traces
[ ] Agent Legibility Lab displays only real/captured experiment data
[ ] all research graphs derive from committed artifacts
[ ] CONFIRMED vs PROVISIONAL claims remain distinct
[ ] Cloudflare/ANS frontier section positions DomainArena correctly
[ ] 5 clean Devpost screenshots exist
[ ] 2:15–2:45 demo rehearsed twice
[ ] final Devpost pitch foregrounds name.com
```

---

# Final judge framing

The submission should leave Katie Wokasch / the name.com judges with this thought:

> **“Most entrants used our API to find or buy a domain. These people made live domain inventory the input to a new measurement problem: how domains perform with AI agents, then completed the entire acquisition and DNS lifecycle through name.com.”**

That is the differentiation.

Cloudflare’s 2026 launches are actually excellent evidence that the market is forming: Agent Readiness covers whether a deployed hostname is technically consumable; AEO covers whether it is recommended; registrar APIs make buying machine-native; DNS/ANS research makes the domain itself infrastructure.

**DomainArena owns the missing decision immediately before all of that: choosing a domain empirically for the machine audience.**

That is the story I would freeze and execute now.
