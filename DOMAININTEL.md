Yes. From the current repo, I would **freeze the product direction now** and build toward one very specific submission:

# DomainArena

**“A/B testing for domain names in the agentic web.”**

> **DomainArena searches live name.com inventory, measures which available domain autonomous agents actually understand and prefer, then safely registers and configures the winner.**

Do **not** broaden this back into AgentSEO. The current repo already contains most of the difficult ingredients; the problem is that they are not yet connected into one judge-proof product.

The name.com challenge explicitly rewards API depth, originality, technical execution, viability, and an end-to-end demo. It specifically says multiple endpoints such as search + registration + DNS are favored. ([DevNetwork Hackathon 2026][1])

The deadline remains **September 3, 2026 at 10:00 AM PDT**, which is **September 4 at 00:00 in Phnom Penh**. I would impose an internal deadline of September 3 around 20:00 ICT rather than use the last four hours. ([DevNetwork Hackathon 2026][2])

One administrative point: the current event page lists **18+ eligibility**, so use the official eligibility rules rather than trying to work around them. ([DevNetwork Hackathon 2026][3])

---

# 1. Where the repo actually is

The fundamental architecture is good.

Your current live pipeline already does:

**intent → candidate generation → live name.com Search → inventory intersection → hard feasibility filters → semantic inversion → evidence → Pareto recommendation.**

Your name.com client already contains:

* Search
* CheckAvailability
* GetPricing
* GetDomain
* CreateDomain
* Create DNS record
* List DNS records
* mutation-mode guard
* retries for timeouts/429s
* idempotency key on registration

And the HTTP lifecycle already intends to do:

**approval → fresh availability → fresh pricing → price-drift check → registration → GetDomain confirmation → DNS evidence TXT → DNS read-back.**

That's excellent hackathon material.

The repo also already has real testing infrastructure around Name.com, constraints, receipts, pairwise evaluation, policy, statistics and write guards.

So I would **not rewrite the project**.

There are, however, several P0 problems.

---

# 2. P0: fix these before doing anything visual

| Problem                                                                   | Severity | Fix                                                          |
| ------------------------------------------------------------------------- | -------: | ------------------------------------------------------------ |
| MCP uses fixtures rather than live pipeline                               |       🔴 | Replace with proper live DomainArena tools                   |
| World never commits episodes                                              |       🔴 | Fix state transition / terminal semantics                    |
| World scorer expects `semantic_score`, executor never supplies it         |       🔴 | Separate inference from scoring and use a typed result       |
| Availability recheck appears to inspect wrong response key                |       🔴 | Fix immediately; fail closed                                 |
| Availability recheck defaults to “available” if response isn't understood |       🔴 | Never default a purchase decision to true                    |
| CheckAvailability isn't filtering `purchaseType=registration`             |       🟠 | Add it                                                       |
| UI doesn't expose purchase/DNS lifecycle                                  |       🟠 | Turn it into the demo flow                                   |
| Semantic inversion gets called redundantly                                |       🟠 | Compute once, carry result through pipeline                  |
| Benchmark mixes unrelated NLI data into “domain” cases                    |       🟠 | Separate scorer validation from actual DomainArena benchmark |
| decision state exists only in memory                                      |       🟡 | Persist lightweight decision + lifecycle state               |

## The nasty availability bug

This deserves special attention.

Your lifecycle currently tries to find the availability response with roughly:

```python
a.get("domain")
```

But the current name.com API returns:

```json
{
  "domainName": "example.com",
  "purchasable": true
}
```

according to the current Core API documentation. ([name.com Core API][4])

Worse, if no matching response is found, the code eventually falls back to:

```python
True
```

for availability.

For a purchasing system, that's the exact opposite of what you want.

Make it:

```text
response missing               -> ABORT
domainName doesn't match       -> ABORT
purchasable missing            -> ABORT
purchaseType != registration   -> ABORT
purchasable == false           -> ABORT
price unavailable              -> ABORT
price changed beyond approval  -> REAPPROVE
```

**Everything purchasing-related must fail closed.**

That's also a very good technical-execution point to mention to a judge.

Name.com itself now recommends using `purchaseType=registration` both during Search and again during the final Check Availability before Create Domain. ([name.com Core API][4])

---

# 3. Fix the benchmark before producing another number

The current `DomainArenaWorld` has a correctness defect.

`COMMIT_SCORE` currently returns state unchanged, yet:

```python
terminal(state)
```

requires:

```python
state.committed == True
```

So the world can't properly reach its intended terminal state.

Separately, `apply()` reads:

```python
result.payload["semantic_score"]
```

but `LLMInferenceExecutor` returns:

```json
{
  "raw": "...",
  "inference": "...",
  "model": "...",
  "provider": "..."
}
```

with **no semantic score**.

Fix the protocol properly instead of sticking a score into the executor.

### Correct evaluation architecture

```text
DOMAIN
  ↓
INFERENCE MODEL
"What service is this?"
  ↓
raw inference
  ↓
HIDDEN SCORER
compare inference against frozen intent
  ↓
semantic_match
  ↓
COMMIT
  ↓
receipt
```

Define something like:

```text
InferenceResult
  domain
  model_family
  model_id
  inference
  latency_ms
  response_hash

SemanticEvaluation
  intent_hash
  inference_hash
  semantic_score
  match_label
  scorer_version
  scorer_model
```

The model being tested should **never score itself**.

That's important experimentally.

---

# 4. Remove the misleading benchmark material

I would also stop presenting ANLI/MNLI/SNLI/etc. as DomainArena benchmark cases.

Your loader currently maps generic NLI statements into fields called `domain_name`.

Those datasets can still be useful for validating an evaluator, but they aren't evidence that agents understand domain names.

Split it into:

```text
evaluation_validation/
    anli
    mnli
    snli
    ...

domainarena_benchmark/
    lexical_names
    opaque_names
    tld_variants
    misleading_names
    real_service_names
```

Then your claim becomes much stronger:

> “We first validate our semantic evaluator on established datasets, then use it on a purpose-built controlled domain benchmark.”

Rather than:

> “We have 8,000 domain benchmark cases.”

when many aren't domains.

---

# 5. Build one experimentally clean DomainArena benchmark

This is the part that can make the submission substantially more than a hackathon toy.

## Primary question

> **Holding the service constant, does hostname choice affect an autonomous agent's ability to understand and select the service?**

### Experiment A — lexical naming effect

Keep the TLD fixed.

For example:

```text
jsonrepair.dev
jsondoctor.dev
fixmalformed.dev
datahelper.dev
velora.dev
```

Same:

* application
* endpoint
* response
* latency class
* MCP description
* API schema
* HTML
* Markdown representation
* DNS arrangement
* readiness metadata

Only the name varies.

This isolates lexical naming reasonably well.

### Experiment B — TLD effect

Keep the stem fixed:

```text
jsonrepair.com
jsonrepair.dev
jsonrepair.ai
jsonrepair.io
```

Now you're testing TLD preference separately.

**Do not mix Experiment A and B and claim one causal effect.**

That is exactly the sort of detail that makes this look like real evaluation work.

---

# 6. Measure behaviour, not just “which one sounds good”

Your current live pipeline is honest about the fact that most dimensions remain `NOT_MEASURED`: pairwise strength, worst-family performance and task success.

Those are the next three things to implement.

For each candidate collect:

| Signal                 | Meaning                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| Semantic comprehension | What does the model infer from the hostname?                     |
| Intent agreement       | How closely does that inference match the frozen product intent? |
| Pairwise preference    | Domain A vs B, randomized AB/BA                                  |
| First-choice rate      | Which candidate gets picked from a set?                          |
| Tool invocation        | Does the agent actually attempt to call it?                      |
| Task success           | Did the correct downstream task complete?                        |
| Worst-family score     | Does the result survive different model families?                |
| Position bias          | Does reversing candidate ordering change preference?             |
| Tokens to success      | Secondary efficiency signal                                      |
| Latency to success     | Secondary efficiency signal                                      |

Your existing AB/BA scheduler and Bradley–Terry estimator are worth keeping. The commit history says you already tested permutation invariance, disconnected graphs and synthetic recovery, with 93 tests green at that historical checkpoint.

Don't need 20 model families.

For the hackathon:

**3 meaningfully different model families × ~20–30 trials per condition** is enough to show something interesting.

Put the exact sample size on screen.

---

# 7. Pre-register the experiment

Add:

```text
experiments/demo_json_repair_v1.yaml
```

containing:

```yaml
experiment_id: da-json-repair-v1
frozen_at: ...
hypothesis: ...
primary_metric: task_success
secondary_metrics:
  - comprehension
  - pairwise_preference
  - first_choice

candidates:
  ...

models:
  ...

randomization:
  seed: ...
  ab_ba: true

exclusion_rules:
  ...
```

Hash it **before the run**.

Then generate:

```text
experiment config hash
↓
individual trial receipts
↓
aggregate receipt
↓
result hash
```

Now the demo can say:

> “The experiment definition was frozen before the results were generated.”

For a hackathon judge, that is memorable.

---

# 8. Replace the current MCP implementation

This is probably the largest product gap.

Right now the MCP server exposes only:

* `recommend_domain`
* `compare_domains`

and both operate over `_demo_candidates()` rather than the live pipeline.

So the interface you call an “agent product” currently bypasses the interesting product.

I would expose these tools:

```text
search_domains
evaluate_domains
recommend_domain
check_domain
prepare_registration
register_domain
configure_dns
verify_domain
get_evidence_receipt
```

But don't expose low-level complexity unless useful.

The judge-facing agent could perform:

```text
recommend_domain(...)
```

internally doing:

```text
Name.com Search
→ availability/pricing
→ experiment evidence
→ recommendation
```

and then separately:

```text
prepare_registration(domain)
```

returns:

```text
CURRENT AVAILABILITY
CURRENT PRICE
RENEWAL
PREMIUM?
PURCHASE TYPE
PRICE CHANGE?
APPROVAL REQUIRED
```

Then only after affirmative approval:

```text
register_domain(approval_id)
```

Finally:

```text
configure_dns(...)
verify_domain(...)
```

Use an actual MCP SDK rather than maintaining a tiny partial JSON-RPC implementation.

That simultaneously improves:

* technical legitimacy,
* interoperability,
* demoability,
* product viability.

---

# 9. Make name.com maximally central

This is crucial for **winning their track**.

The product should literally be impossible without live domain inventory.

Your pipeline should visibly hit:

### 1. Search

```text
POST /core/v1/domains:search
```

This determines the experimental candidate universe.

### 2. CheckAvailability

```text
POST /core/v1/domains:checkAvailability
```

Used immediately before purchase.

Name.com allows up to 50 domains and recommends `purchaseType=registration`. ([name.com Core API][4])

### 3. GetPricing

```text
GET /core/v1/domains/{domain}:getPricing
```

Current API provides purchase and renewal prices, with duration nuances such as some TLDs requiring multi-year periods. ([name.com Core API][5])

### 4. CreateDomain

```text
POST /core/v1/domains
```

Use an idempotency key.

Name.com's own current reseller guide explicitly recommends final availability checking and an `X-Idempotency-Key` before the billable create operation. ([name.com Core API][6])

### 5. CreateRecord

```text
POST /core/v1/domains/{domain}/records
```

([name.com Core API][7])

### 6. ListRecords

```text
GET /core/v1/domains/{domain}/records
```

Use this to prove the configuration actually stuck. ([name.com Core API][8])

That's **six visibly useful name.com interactions in one workflow**.

Perfect for their stated criterion.

---

# 10. Add one extra name.com trick: Zone Check

This is optional but elegant.

Their newer API includes **Zone Check**, a fast cached preliminary availability signal for larger candidate batches, with standard CheckAvailability recommended afterward for definitive real-time availability/pricing. ([name.com Core API][9])

DomainArena could do:

```text
100 generated candidates
        ↓
Zone Check
        ↓
25 probable candidates
        ↓
Search / CheckAvailability
        ↓
10 purchasable
        ↓
expensive model evaluation
```

That's a legitimate optimization.

But mark this **P2**. Don't let it delay the core demo.

---

# 11. Strengthen the purchase state machine

Don't model approval as one mutable Boolean.

Build:

```text
DISCOVERED
    ↓
EVALUATED
    ↓
RECOMMENDED
    ↓
CHECKED
    ↓
AWAITING_APPROVAL
    ↓
APPROVED
    ↓
RECHECKED
    ↓
REGISTERING
    ↓
REGISTERED
    ↓
DNS_CONFIGURING
    ↓
VERIFIED
```

And states like:

```text
PRICE_CHANGED
UNAVAILABLE
APPROVAL_EXPIRED
PROVIDER_ERROR
REGISTRY_PENDING
DNS_VERIFY_FAILED
```

Store:

```text
decision_id
intent_hash
candidate
quoted_price
quoted_at
latest_price
approval_timestamp
approval_hash
registration_request_hash
provider_response_hash
dns_verification
```

SQLite is enough.

Don't build Postgres infrastructure for a four-day hackathon.

---

# 12. Improve retry handling

Your client already handles timeouts and 429 retrying.

Current name.com documentation additionally distinguishes provider errors. Their 2026 changelog says:

* `502`: safe for immediate exponential backoff.
* `504`: verify system status before retrying operations where duplication could matter. ([name.com Core API][10])

Implement endpoint-aware retry behavior.

Especially:

```text
READ calls:
generous retry

CREATE DOMAIN:
idempotency key
+
careful retry

DNS POST:
check before duplicate retry
```

---

# 13. Tests I would require before demo recording

Your existing Name.com tests already check parsing, TLD filters, errors, availability bounds, idempotency header, DNS roundtrip and timeout behavior.

The HTTP API tests only get as far as confirming that registration is blocked before approval; they don't execute the complete lifecycle.

Add this matrix:

| Suite                              | Must prove                                                                                    |
| ---------------------------------- | --------------------------------------------------------------------------------------------- |
| `test_namecom_contract.py`         | current response schemas from every used endpoint                                             |
| `test_availability_fail_closed.py` | malformed/missing `domainName`, null `purchasable`, false availability all abort              |
| `test_purchase_type.py`            | aftermarket/etc rejected                                                                      |
| `test_price_drift.py`              | quote `$9.99` → `$15` invalidates approval                                                    |
| `test_premium.py`                  | premium explicitly displayed and approved                                                     |
| `test_registration_idempotency.py` | duplicate retry can't double-create                                                           |
| `test_lifecycle_e2e_mock.py`       | Search → recommendation → approval → recheck → price → register → GetDomain → DNS → read-back |
| `test_write_guard.py`              | live writes impossible without explicit mode                                                  |
| `test_decision_persistence.py`     | restart doesn't silently lose approval state                                                  |
| `test_mcp_contract.py`             | initialize/list/call/error semantics                                                          |
| `test_mcp_live_pipeline.py`        | MCP recommendation actually calls live pipeline adapter                                       |
| `test_world_terminal.py`           | every valid episode reaches terminal                                                          |
| `test_world_score_contract.py`     | inference → evaluator → score schema                                                          |
| `test_abba_balance.py`             | left/right positioning exactly balanced                                                       |
| `test_bt_recovery.py`              | known synthetic strength recovered                                                            |
| `test_reproducibility.py`          | fixture+seed produces identical aggregate                                                     |
| `test_receipt_integrity.py`        | changed trial invalidates aggregate hash                                                      |
| `test_semantic_failure.py`         | invalid model response becomes explicit error, not zero-quality observation                   |
| `test_demo_e2e.py`                 | exact demo fixture completes                                                                  |
| `test_secrets.py`                  | API credentials never appear in repo/output                                                   |

Also run:

```text
pytest -q
ruff check .
```

I'd add GitHub Actions for those two only.

Don't suddenly introduce a strict type checker if it creates 200 unrelated fixes.

---

# 14. Live integration test tier

Have three test tiers.

### Tier 1 — offline

Runs on every commit.

```text
pytest -m "not live"
```

No credentials.

### Tier 2 — Name.com read-only

With sandbox credentials:

```text
search
check availability
pricing
```

No mutation.

### Tier 3 — lifecycle

Explicit:

```text
DOMAINARENA_DESTRUCTIVE_TEST=1
```

Use sandbox.

Execute:

```text
find unused cheap sandbox candidate
→ registration
→ GetDomain
→ create TXT
→ read TXT
```

One lifecycle test is enough.

Never make destructive tests execute automatically.

---

# 15. Build a judge-specific UI, not a general dashboard

The current UI is basically:

**form → recommendation → inference cards → inventory table**, and it ends by saying registration is disabled.

That cannot be your final demo.

Build one page with a vertical execution trace:

```text
YOUR INTENT
"JSON repair API for autonomous agents"

        ↓

1  LIVE DOMAIN DISCOVERY
   Powered by name.com
   83 candidates → 11 purchasable

        ↓

2  AGENT COMPREHENSION
   Claude     ...
   GPT        ...
   MiMo       ...

        ↓

3  DOMAIN ARENA
   60 randomized trials
   position balanced

        ↓

4  WINNER
   some-real-domain.dev
   comprehension ...
   preference ...
   task success ...

        ↓

5  LIVE CHECKOUT
   Available ✓
   Price $...
   Renewal $...
   registration inventory ✓

          [Approve registration]

        ↓

6  NAME.COM REGISTRATION
   CreateDomain ✓

        ↓

7  DNS
   CreateRecord ✓
   ListRecords ✓

        ↓

8  VERIFIED
   evidence receipt sha256:...
```

That's the product.

You don't need React.

Replace the current hand-written page with clean vanilla HTML/CSS/JS if necessary.

---

# 16. Add a visible “API trace” panel

This is a hackathon optimization.

Right side:

```text
name.com API
─────────────────────────
✓ POST domains:search
  184 ms

✓ POST domains:checkAvailability
  121 ms

✓ GET domain:getPricing
   82 ms

✓ POST domains
  633 ms

✓ POST records
  141 ms

✓ GET records
   87 ms
```

Never expose auth headers.

This makes **API integration depth visually undeniable**.

Judges shouldn't have to infer that you're using the sponsor.

---

# 17. Don't run the large experiment during the video

Precompute the serious experiment.

Store:

```text
experiment config
trial receipts
aggregate
hash
timestamp
model versions
```

Then during the demo:

* show the existing verified large result,
* optionally press **“Run 4 live trials”** to demonstrate it is executable.

You do not want 90 seconds of the video watching LLM requests spin.

The expensive evidence can be precomputed **as long as it is real, reproducible, dated and clearly presented as a prior run**.

---

# 18. The exact demo prompt

Use this as the canonical golden-path fixture:

> **“I'm launching an API that repairs malformed JSON for autonomous agents. Find me a domain under $25 for the first year and $35 renewal that agents are likely to correctly understand and select. Show me the evidence. Do not register anything until I approve.”**

This gives you:

* recognizable product purpose,
* hard constraints,
* agent-specific relevance,
* semantic experiment,
* name.com search,
* price filtering,
* approval boundary,
* registration payoff.

It's much better than “find me a cool startup domain.”

---

# 19. Exact 3–3½ minute demo

This is the script I would record.

**[0:00 — Product screen, no slides]**

“Autonomous agents are increasingly able to read websites and call tools. But before an agent can use a service, it has to decide which service it thinks a domain represents.

DomainArena measures that missing layer: which available domain do AI agents actually understand and select?”

**[0:15 — Enter prompt]**

“I’m launching a JSON repair API for autonomous agents. I want a domain under twenty-five dollars for the first year and thirty-five dollars renewal. And I don’t want anything purchased without my approval.”

Submit:

“I’m launching an API that repairs malformed JSON for autonomous agents. Find me a domain under $25 for the first year and $35 renewal that agents are likely to correctly understand and select. Show me the evidence. Do not register anything until I approve.”

**[0:35 — Live discovery]**

“DomainArena now searches live name.com inventory.”

Show the API trace visibly recording:

`POST /domains:search`

Point briefly at real candidates, purchase prices, renewal prices, premium status and eliminated candidates.

“These aren't invented suggestions. The candidate space is live purchasable name.com inventory, and hard budget constraints eliminate candidates before they're scored.”

**[0:55 — Agent understanding]**

“Now we perform semantic inversion. The model sees the domain without the product description and tells us what it thinks exists behind that hostname.”

Show three or four real candidate cards:

Domain
Model inference
Intent agreement

“The system isn't asking the model which name it likes. It's measuring whether the name transmits the intended function.”

**[1:15 — Arena result]**

“Semantic comprehension alone isn't enough, so DomainArena runs controlled agent trials.”

Open the experiment result.

“All candidates use the same service and tool interface. Candidate position is randomized and pairwise comparisons are run in both directions. We measure selection, comprehension and actual task success.”

Show:

* experiment ID
* number of real trials
* model families
* AB/BA balanced indicator
* primary metric
* real rankings
* confidence/uncertainty
* experiment hash

“This experiment was frozen before execution and every run produces an evidence receipt.”

**[1:45 — Recommendation]**

Show the real winner.

“So for this intent, DomainArena recommends this domain. Here is why: the live price satisfies the budget, agents correctly infer its purpose, it performs strongly in randomized selection, and its task-success result survives across the tested model families.”

Show the factors separately. Do not show one unexplained magic score.

**[2:05 — Checkout safety]**

Click **Prepare registration**.

“Domains are live inventory, so we never purchase from a stale recommendation.”

API trace:

`POST /domains:checkAvailability`
`GET /domains/{domain}:getPricing`

“The domain is checked again immediately before purchase. If availability changes, the operation aborts. If price changes beyond the approved range, the original approval becomes invalid.”

Show:

Available ✓
Registration inventory ✓
Current price
Renewal price
Premium status
**Human approval required**

**[2:30 — Explicit approval]**

Click **Approve & register**.

“This is the irreversible boundary. Evaluation is autonomous; registration requires explicit approval.”

API trace:

`POST /domains`

Show success.

“name.com now performs the actual domain registration using an idempotent request.”

**[2:45 — DNS configuration]**

“DomainArena then configures and verifies DNS rather than stopping at checkout.”

API trace:

`POST /domains/{domain}/records`
`GET /domains/{domain}/records`

Show `_domainarena` TXT evidence record and the read-back verification.

**[3:00 — Evidence receipt]**

Show final receipt:

Intent hash
Experiment hash
Selected domain
Name.com provider steps
Registration confirmation
DNS verification
Receipt hash

“The entire decision—from product intent to experimental evidence to the registered domain—is reproducible and auditable.”

**[3:15 — Final screen]**

“DomainArena isn't another domain generator. It measures which domain autonomous agents actually understand and use, then closes the loop through name.com.”

On screen:

**DomainArena**
*Measure the identity your agents will choose.*
**Powered by the name.com Core API**

That is the entire story. Do not interrupt it with architecture slides.

---

# 20. The UI should expose evidence, not a magic 0.83

Avoid:

```text
AI domain score: 87
```

Prefer:

```text
jsonrepair.dev

LIVE INVENTORY
First year       $12.99
Renewal          $14.99
Premium          No

AGENT EVIDENCE
Comprehension    91%    n=60
Preference       68%    n=120
Task success     94%    n=60
Worst family     82%

EXPERIMENT
3 model families
AB/BA balanced
Frozen protocol da-json-v1
```

Even better if the judge can click each result and see the underlying observations.

---

# 21. Turn evidence coverage into a feature

You have already built a provenance distinction between:

* `MEASURED`
* `PROXY`
* `NOT_MEASURED`

and the recommendation machinery handles absent evidence explicitly.

Surface that.

For instance:

```text
Semantic transmission     MEASURED ✓
Pairwise preference       MEASURED ✓
Task success              MEASURED ✓
Worst model family        MEASURED ✓
Human recall              NOT MEASURED
```

Then:

**Evidence coverage 80%**

This is far more credible than silently substituting heuristics.

---

# 22. Add a “quick” and “deep” mode

This turns it into a plausible product.

### Quick

```text
~seconds
Name.com live search
semantic inversion
budget filtering
```

Useful when someone wants ideas immediately.

### Deep

```text
~minutes
multi-family agent tournament
AB/BA randomized selection
task execution
statistical ranking
```

Useful immediately before buying/launching.

That gives DomainArena an actual commercial model:

> **“Spend $1–$5 evaluating an identity before committing hundreds or thousands of dollars and years of branding to it.”**

---

# 23. Real-world customers

Don't pitch it as merely a research toy.

There are three clear customers:

**AI-native builders:** “Which domain will agents understand?”

**registrars / domain marketplaces:** add an **Agent Comprehension** signal beside price and availability.

**AI website builders:** user describes product → platform identifies and purchases an agent-legible domain automatically.

The strongest name.com-specific commercial pitch is:

> **DomainArena could become an intelligence layer inside domain search: not merely what is available, but what machine customers are likely to understand.**

That's much stronger than “start an AgentSEO SaaS.”

---

# 24. Your name.com judge mapping

Current name.com judging is unusually favorable to this entry. ([DevNetwork Hackathon 2026][1])

| Criterion                 | What you show                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| **API integration depth** | Search → CheckAvailability → GetPricing → CreateDomain → CreateRecord → ListRecords                    |
| **Creativity**            | Controlled experiment on how agents interpret domain identity                                          |
| **Technical execution**   | AB/BA randomization, BT ranking, fail-closed checkout, idempotency, price-drift invalidation, receipts |
| **Real-world viability**  | intelligence layer for registrars, builders and agent-first services                                   |
| **Presentation**          | one prompt becomes a measured, registered, configured domain                                           |

This is a very strong fit.

---

# 25. Competition strategy

The official gallery is **still unpublished**, so don't convince yourself you know the complete competitive field. ([DevNetwork Hackathon 2026][11])

One already-visible submission, LaunchPilot, does use the name.com Core API, but its published known boundaries explicitly say domain purchase and registration remain outside its agent boundary. ([Devpost - The home for hackathons][12])

That reinforces the strategic importance of your full loop.

You want your judge to see:

```text
Most entry:
"AI suggests a domain."

DomainArena:
"AI discovers live inventory,
we experimentally measure the identity,
we safely recheck it,
register it,
configure it,
verify it,
and preserve the evidence."
```

---

# 26. Dev schedule from here

## August 30 — correctness day

**Do not touch aesthetics until this is done.**

P0:

1. fix CheckAvailability parsing and fail-closed behavior;
2. add `purchaseType=registration`;
3. fix DomainArenaWorld state transitions;
4. implement separate semantic scorer contract;
5. add world terminal/scoring tests;
6. replace MCP fixture recommendation with live pipeline;
7. expose the correct Name.com lifecycle through MCP/API;
8. close provider clients reliably;
9. re-run full offline suite;
10. publish exact test count rather than relying on the August 25 “93 green” commit message.

Exit gate:

```text
all offline tests green
no purchase fail-open path
MCP uses real pipeline
world produces valid receipts
```

## August 31 — product day

Build:

```text
persistent decision state
prepare-registration endpoint
real approval token/state
registration lifecycle
DNS verification
complete lifecycle E2E mocks
sandbox lifecycle integration test
API trace representation
```

Exit gate:

```text
one command can perform the entire sandbox lifecycle
```

## September 1 — evidence day

Create:

```text
demo_json_repair_v1
```

Run:

* controlled candidate experiment,
* 2–3 model families,
* sufficient repeated trials,
* AB/BA balance,
* actual task execution,
* aggregate results,
* evidence hashes.

Then inspect the results.

**Do not decide the winner before running it.**

If the finding is weak, that's okay. The product still measures it.

Exit gate:

```text
one credible, reproducible real experiment
```

## September 2 — demo/product polish

Build the judge UI:

```text
prompt
→ discovery
→ comprehension
→ arena
→ recommendation
→ approval
→ registration
→ DNS
→ receipt
```

Add:

* API trace,
* clear live/recorded labels,
* result drill-down,
* no secrets,
* loading/error states,
* screenshot-quality styling.

Then run the exact demo repeatedly.

Record the final video.

## September 3 — submission only

No architectural work unless something is broken.

Do:

```text
clean-clone installation test
pytest
ruff
sandbox smoke
README
screenshots
video upload
Devpost text
links
submission
```

Submit hours early.

---

# 27. README structure

Replace the current short README with:

```text
# DomainArena

One sentence

[hero screenshot]

## The problem
## What DomainArena measures
## 30-second example
## Why this isn't another domain generator
## How name.com is central
## Architecture
## Experimental methodology
## Current results
## Evidence / reproducibility
## Safety and purchase approval
## MCP tools
## API
## Quickstart
## Tests
## Limitations
## Hackathon demo
```

Put the hackathon reviewer experience first.

The current README correctly says this is an agent domain preference benchmark and MCP, but it's too thin for a judge landing cold on the repository.

---

# 28. The diagram I want in the README

```text
                  ┌─────────────────────┐
                  │   PRODUCT INTENT    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ name.com SEARCH API │
                  │ live inventory      │
                  └──────────┬──────────┘
                             │
                    hard constraints
                             │
                             ▼
              ┌─────────────────────────────┐
              │        DOMAIN ARENA         │
              │                             │
              │ semantic comprehension      │
              │ randomized pairwise choice  │
              │ task success                │
              │ cross-model robustness      │
              └─────────────┬───────────────┘
                            │
                            ▼
                    RECOMMENDATION
                            │
                            ▼
                   CheckAvailability
                            │
                       GetPricing
                            │
                            ▼
                     HUMAN APPROVAL
                            │
                            ▼
                      CreateDomain
                            │
                            ▼
                  Create DNS record
                            │
                     List/read-back
                            │
                            ▼
                  VERIFIED RECEIPT
```

That's the whole project in one picture.

---

# 29. Things I would explicitly **not** build

Until submission, do **not** spend time on:

* generic AgentSEO audits,
* llms.txt tooling,
* blogging/content optimization,
* Search Engine Optimization features,
* five more LLM providers,
* user accounts,
* billing,
* a marketplace,
* sophisticated hosted infrastructure,
* broad Cloudflare integration,
* a giant dashboard,
* domain resale,
* transfer support,
* DNSSEC,
* complete registrar functionality,
* more unrelated benchmark datasets.

Name.com's own reseller docs have lots of further functionality—contacts, privacy, renewals, transfers, webhooks, nameservers, etc.—but their guide explicitly presents those as extensions beyond the basic Search → Register → Manage flow. ([name.com Core API][6])

You need **depth down one path**, not breadth.

---

# 30. Definition of done

I would refuse to call it finished until all of these are true:

```text
[ ] MCP recommendation uses live Name.com-backed pipeline
[ ] No hidden fixture can masquerade as live evidence
[ ] DomainArenaWorld terminates correctly
[ ] Tested model never evaluates its own semantic success
[ ] Proper purpose-built domain benchmark exists
[ ] CheckAvailability fails closed
[ ] purchaseType=registration enforced
[ ] stale availability stops purchase
[ ] price drift invalidates approval
[ ] registration is idempotent
[ ] purchase requires explicit approval
[ ] registration succeeds in sandbox
[ ] DNS is created
[ ] DNS is read back
[ ] decision + experiment + lifecycle produce receipts
[ ] one real multi-model experiment exists
[ ] AB/BA/randomization is visible
[ ] API trace visibly shows Name.com endpoints
[ ] exact golden demo passes repeatedly
[ ] offline tests are all green
[ ] sandbox integration smoke passes
[ ] clean setup instructions work
[ ] README tells the story in under 30 seconds
[ ] 2–4 minute video is recorded
[ ] Devpost submitted well before deadline
```

## The main strategic change

Right now the codebase feels like **several clever research and infrastructure experiments that happen to touch domains**.

By submission it should feel like **one inevitable transaction**:

> **Tell DomainArena what you're building → Name.com supplies the real possible identities → agents experimentally evaluate them → DomainArena proves the winner → you approve → name.com registers it → DNS proves the decision happened.**

That is the version I think has a legitimate shot at the **name.com first-place prize**, and it is also sufficiently unusual and technically rigorous to be understandable as an overall-hackathon contender rather than merely “AI domain search.”

[1]: https://api-cloud-ai-hackathon-2026.devpost.com/?ref_feature=challenge&ref_medium=discover&utm_source=chatgpt.com "DevNetwork [API + Cloud + AI] Hackathon 2026: Join the nation's largest challenge-driven API + Cloud + AI hackathon @ API World 2026! - Devpost"
[2]: https://api-cloud-ai-hackathon-2026.devpost.com/details/dates?utm_source=chatgpt.com "DevNetwork [API + Cloud + AI] Hackathon 2026: Join the nation's largest challenge-driven API + Cloud + AI hackathon @ API World 2026! - Devpost"
[3]: https://api-cloud-ai-hackathon-2026.devpost.com/?utm_source=chatgpt.com "DevNetwork [API + Cloud + AI] Hackathon 2026: Join the nation's largest challenge-driven API + Cloud + AI hackathon @ API World 2026! - Devpost"
[4]: https://docs.name.com/api/v1/reference/domains/check-availability?utm_source=chatgpt.com "Check Availability - name.com Core API"
[5]: https://docs.name.com/api/v1/reference/domains/get-pricing-for-domain?utm_source=chatgpt.com "Get Pricing For Domain - name.com Core API"
[6]: https://docs.name.com/guides/quickstart?utm_source=chatgpt.com "Reseller Quickstart - name.com Core API"
[7]: https://docs.name.com/api/v1/reference/dns/create-record?utm_source=chatgpt.com "Create Record - name.com Core API"
[8]: https://docs.name.com/api/v1/reference/dns/list-records?utm_source=chatgpt.com "List Records - name.com Core API"
[9]: https://docs.name.com/api/v1/reference/domains/zone-check?utm_source=chatgpt.com "Zone Check - name.com Core API"
[10]: https://docs.name.com/api/v1/changelog?utm_source=chatgpt.com "Changelog - name.com Core API"
[11]: https://api-cloud-ai-hackathon-2026.devpost.com/project-gallery?utm_source=chatgpt.com "DevNetwork [API + Cloud + AI] Hackathon 2026: Join the nation's largest challenge-driven API + Cloud + AI hackathon @ API World 2026! - Devpost"
[12]: https://devpost.com/software/launchpilot-q1ykc4?utm_source=chatgpt.com "LaunchPilot | Devpost"
