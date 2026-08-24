# DomainArena — North Star

> **DomainArena is not a naming generator. It is an empirical decision engine over name.com's live domain inventory.**
>
> The project succeeds when it can demonstrate that a recommended domain is better under a defined adoption objective using reproducible evidence.
>
> Prioritize, in order:
> `real inventory → controlled semantic proxy → controlled selection → executable task success → cross-model robustness → registration`.
>
> Never substitute more generators, more scoring dimensions, prettier visualizations, evolution machinery, or LLM explanations for evidence that the recommendation improves the target outcome.
>
> If an experiment shows domain names have little effect under a particular audience/task, preserve that finding. DomainArena's value is discovering **when domains matter and how**, not proving that every domain matters.

---

## The most important conclusion

**Do not build a better AI domain generator.** That category is already crowded.

The defensible product is:

> **DomainArena measures whether a candidate domain causes the intended human or AI agent to correctly understand, select and successfully use the product—and then optimizes over real name.com inventory and budget.**

Strongest new research result: AgentSearchBench — across ~10k real agents, semantic similarity between an agent's description and the task is consistently *weaker* than execution-grounded performance for ranking agents. So **Semantic Inversion becomes a cheap proxy stage, not ground truth**.

Real endpoint:

```
UsefulSelection(d) = P(agent selects d ∧ task succeeds)
```

---

## Product pivot

After deeper research, DomainArena must move beyond "which domain do humans like?" toward confirmed task success, tool behavior, cost, recovery and causal real-world outcomes (mirroring Arena.ai's evolution).

Machine-facing hierarchy:
`semantic understanding → agent selection → successful invocation → task success → stability across model families → reuse → economics`

Human aesthetics are a tiny component for machine-facing products; for consumer brands human recall/pronunciation/spelling/trust become major again. Hence **audience-conditioned policies**, never one universal score.

### The missing piece (and why name.com)

Given this product, this audience and this budget: **which domain from name.com's actual inventory should the agent buy?**

name.com's API provides exactly the needed variables: purchasability, premium status, purchase price, renewal price, purchase type. Search results are explicitly unordered → room for an intelligent ranking layer. Railway does 1,700+ registrations/month via embedded name.com purchasing, so another autonomous buyer isn't novel — the recommendation intelligence layer (`recommend_domain(intent, audience, constraints)`) in front of their API is. Judges reward central, multi-endpoint, unexpected API applications.

---

## Competitor landscape

| Competitor | Already does | What we do differently |
| --- | --- | --- |
| Atom | AI-ranked names, availability, USPTO screening, AI compare, real human testing | Human testing is NOT our moat; measure agent understanding/selection/execution + model robustness |
| Namelix | Styles, length/TLD filters, learns from saves | Generator diversity isn't enough |
| Namecheap Beast Mode | 5,000 names, price/TLD filters, bulk checkout | Budget-constrained search is commodity |
| GoDaddy/registrar AI | Generate→buy→site ecosystem | Don't compete on "launch everything" |
| gregm711/agent-domain-service-mcp | name.com pricing, budget filter, MCP, AI 1–10 scores | Direct competitor; our edge = empirical evaluation vs subjective scores |
| dorukardahan/domain-search-mcp | MCP, Qwen naming model, anti-slop ranking | Its README admits scores are heuristic — exactly our gap |
| faizul666/domain-search-agent | RDAP verify, weighted 10-dim score | Perfect baseline to beat experimentally |
| bitbuilder-io/domains | Cloudflare/React UX | Useful UI source only |

Existing approach: `description → generate → check availability → AI rates 1-10 → buy`.
DomainArena: `freeze intent → diverse generators → real inventory → hard constraints → semantic inversion → pairwise arena → agent discovery → actual invocation → hidden verifier → cross-model robustness → Pareto frontier → recheck → register`.

Previous name.com judging (Domain Roulette: YourBusiness Cards won) emphasized creative interpretation, execution, polish, domain-product connection. Current challenge wants API depth + originality + technical execution + viability + demo, multiple endpoints, unexpected applications. So: **scientifically interesting but visually simple**. No research-paper UI.

name.com strategic angle: they own the transaction layer; we can be the recommendation intelligence layer (`build app → need domain → DomainArena → recommend best purchasable domain → name.com`).

---

## Repos to clone into research/upstream/ (with SOURCE_LEDGER.md)

| Priority | Repo | Take from it |
| --- | --- | --- |
| P0 | Bingo-W/AgentSearchBench | Execution-grounded relevance, probing (MIT) |
| P0 | lmarena/arena-rank | Bradley–Terry implementation (Apache-2.0) |
| P0 | tatsu-lab/alpaca_eval | Annotator abstraction, caching, bias analysis |
| P0 | dorukardahan/domain-search-mcp | MCP UX, caching, failure handling, baseline |
| P1 | lmarena/search-arena | Real search traces, BT analysis |
| P1 | lm-sys/FastChat | Randomized anonymous Arena battles (study) |
| P1 | macanderson/arena | ABBA scheduling, Wilson/McNemar/bootstrap |
| P1 | faizul666/domain-search-agent | Weighted-score competitor baseline |
| P1 | bitbuilder-io/domains | React UI components |
| P2 | AIcling/agentic_geo | MAP-Elites + surrogate critic (post-MVP) |
| P2 | OpenEvolve | Checkpoints/islands/MAP-Elites (study) |

Avoid: Sra1Phani/domain-finder (Elastic-2.0 license — research only).

Maintain `research/upstream/SOURCE_LEDGER.md`: repo, commit SHA, license, what we learned, what was reused.

---

## Reading queue (12 papers)

1. **AgentSearchBench** — descriptions are poor proxies; make selection+execution strongest tier.
2. **Arena.ai causal methodology** — beyond preference votes: confirmed success, tool reliability, recovery, cost.
3. **Chatbot Arena (2403.04132)** — pairwise + Bradley–Terry foundation.
4. **Pairwise Preference Search (2403.16950)** — uncertainty-driven pair selection, avoid O(n²).
5. **Judging the Judges (2406.07791)** — position bias ⇒ AB/BA/permutation controls mandatory.
6. **Self-Preference Bias (2410.21819)** — generator ≠ judge; holdout families.
7. **Dissecting Human and LLM Preferences (2402.11296)** — justifies audience-conditioned objectives.
8. **Length-Controlled AlpacaEval (2404.04475)** — length is a confounder.
9. **Search Arena (2506.05334)** — perceived credibility ≠ grounded quality.
10. **Trust LLM Search Agents? (2606.16821)** — susceptibility varies by family ⇒ worst-family metric.
11. **TRUSTDESC (2604.07536)** — descriptions alter selection; derive from implementations, hold constant.
12. **AgenticGEO (2603.20213)** — surrogate critic + QD archive (post-MVP).

Plus: **EvoPrompt (2309.08532)** — evolutionary text optimization works; **Credibility of Automatic Appraisal of Domain Names (1811.03415)** — never put "Domain Score: 94/100" at the center.

---

## Is human preference irrelevant?

**Sometimes almost yes; universally no.**

- Pure agent-facing API: funnel EXPOSED→UNDERSTOOD→SELECTED→INVOKED→VALID PARAMS→SUCCEEDED→REUSED. Human taste may be irrelevant.
- B2B SaaS: both matter (agents discover; humans approve/pay).
- Consumer brand: recall/pronunciation/sharing dominate.

So ask WHO MUST UNDERSTAND IT (consumers/businesses/developers/agents/mixed) and change **the experiment suite**, not just weights.

---

## Experimental hierarchy

```
TIER 0 — FEASIBILITY        name.com inventory, budgets, premium/TLD policy
TIER 1 — NAME PROPERTIES    pronounceability, length, spelling, ambiguity
TIER 2 — SEMANTIC PROXY     Semantic Inversion ("what would X.dev do?")
TIER 3 — CHOICE             Pairwise selection, controlled context
TIER 4 — AGENT DISCOVERY    realistic task + candidates → which selected?
TIER 5 — EXECUTION          agent invokes the service
TIER 6 — VERIFIED OUTCOME   hidden deterministic verifier confirms success
TIER 7 — ROBUSTNESS         across model families / time windows
TIER 8 — FIELD OUTCOME      impressions → selections → registrations → usage
```

**Tier 6 is the scientific moat.** Most competitors stop at Tier 1–3.

Central architecture:

```
PRODUCT INTENT
  ↓ WHO MUST UNDERSTAND IT? (human/developer/agent/mixed)
NAME GENERATOR POPULATION
  ↓ NAME.COM REAL INVENTORY
HARD BUDGET / RENEWAL / TLD CONSTRAINTS
  ↓ SEMANTIC INVERSION
CONTROLLED AGENT SELECTION
  ↓ ACTUAL INVOCATION + TASK SUCCESS
MODEL-FAMILY STABILITY
  ↓ OPTIONAL HUMAN MEMORY/TRUST TESTS
PARETO FRONTIER
  ↓ BEST DOMAIN FOR THIS ADOPTION PATH
NAME.COM RECHECK → APPROVE → REGISTER + DNS RECEIPT
```

---

## Build checkpoints

| Gate | Demonstrate before proceeding |
| --- | --- |
| CP0 Preserve baseline | Tag HEAD, tests green, evidence ledger kept, source ledger added |
| CP1 Competitor baseline | `LLM → names → heuristic score → availability` |
| CP2 name.com feasibility | Real price/renewal/premium; $20 budget means >$20 impossible (removed, not penalized) |
| CP3 Semantic Inversion | Frozen intent, blind inference, multi-model, deterministic scoring |
| CP4 Pairwise Arena | AB/BA, randomized order, Bradley–Terry, CIs |
| CP5 Useful Selection | Task + candidate services; different hostnames; actual execution; hidden verifier — **the crucial novelty gate** |
| CP6 Cross-family robustness | ≥5 healthy families; mean/range/variance/worst-family reported separately |
| CP7 TLD causal trial | Same SLD/title/description/tool except TLD; preregistered |
| CP8 E2E lifecycle | Search → recheck → sandbox register → DNS receipt → read-back |
| CP9 Competitive ablation | Baseline vs semantic-only vs pairwise vs execution-grounded under same budget |
| CP10 Polished demo | 3 deterministic fixtures, <4 min |
| CP11 Evolution if justified | EvoName must beat strong best-of-N at identical inference budget |

Rule: **CP5 before EvoName.**

---

## Killer ablation

30–50 product intents × methods {A single-LLM self-rating, B heuristic, C semantic inversion, D multi-model pairwise, E execution-grounded} evaluated against held-out agent task success. Illustrative targets: 52% / 57% / 66% / 71% / 79% Useful Selection.

Also build the "human taste can fail" benchmark: e.g. VELORA.AI vs JSONREPAIR.DEV for a JSON repair API. Either result is interesting — do not force the hypothesis.

---

## Build exceptionally well

Controlled experiment runner · execution-grounded selection environment · name.com inventory/price integration · model-family provenance · AB/BA controls · generator/judge separation · evidence receipts · failure/abstention states · three spectacular fixtures · final registration experience.

## Explicitly NOT now

Logos/brand books · trademark filing infra · crowdsourcing · custom naming LLM · social-handle checking · 1,400-TLD exploration · DNS dashboard · website builder · SEO analytics · HydraDB · evolutionary trees before evolution wins · arbitrary weighted scoring · blended quality score · twelve half-working experiments.

## Demo moments

1. **Budget changes the answer**: citation-verification agent, <$20 first year, <$30 renewal — infeasible names eliminated, not down-scored.
2. **Model disagreement table**: peak preference vs cross-family robustness.
3. **Actual behavior**: identical tool descriptions, different domains → selected % / valid invocation % / task verified %. Data must come from real trials.

## Post-MVP frontier

Surrogate evaluator (AgenticGEO): expensive arena → training data → cheap surrogate screens thousands → uncertain/high-value back to real arena → recalibration.

## Final framing

The moat is not "our AI picks better names." It is:

# **DomainArena discovers the causal rules governing internet identity in an agent-mediated web.**

And name.com monetizes the decision when the winner gets registered.
