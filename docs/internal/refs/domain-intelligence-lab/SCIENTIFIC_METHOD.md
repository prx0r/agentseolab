# Scientific Method for Agent Discovery / AgentSEO Experiments

## 1. Define the estimand first

Every experiment must state exactly what it estimates.

Examples:
- P(domain A is selected before domain B | intent, model, controlled snippet)
- probability a real search-capable agent retrieves/open/cites a target site for an intent
- causal effect of changing only hostname while title/description/body remain fixed
- causal effect of adding structured metadata while content remains fixed

Do not mix these into one "AgentSEO score."

## 2. Capture immutable SiteIntent

Collect the site's exact purpose before candidate generation. Store:
- detailed purpose
- primary user job
- audiences
- capabilities
- geographic/language scope
- commercial model
- constraints
- prohibited meanings/associations
- desired TLD/length/word rules

Hash the canonical JSON. All downstream observations reference the intent_id and intent_hash.

## 3. Field trials: observe actual search behavior

Primary protocol for learning "what agents search":

1. Give a fresh search-capable agent only the frozen SiteIntent/task.
2. Provide the normal search/browse interface.
3. Do not mention candidate domains.
4. Record every observable action:
   - query issued
   - query order
   - result set and rank
   - URL/domain shown
   - result opened
   - subsequent reformulation
   - citation/source selected
   - final answer/action
5. Repeat across model families, versions, providers, and sessions.

Primary outcomes:
- search_activation_rate
- query_token/phrase frequencies
- target_retrieval_rate@k
- target_open_rate
- target_citation_rate
- task_success_rate
- search depth and reformulation count

Important: only log observable tool/action traces exposed by the agent system. Do not attempt to collect private chain-of-thought.

## 4. Controlled lab trials

Use lab experiments to isolate causal variables.

### Hostname-only trial
Keep title, description, visible content, ranking position and metadata identical. Change only hostname.

### Snippet trial
Keep hostname and landing content fixed. Change exactly one of:
- title
- description
- displayed path

### Machine-readable trial
Keep human-visible content constant. Change exactly one of:
- JSON-LD/schema
- OpenAPI operation names/descriptions
- MCP server/tool names/descriptions
- robots/crawler directives
- sitemap presence
- machine-readable capability manifest

For every treatment:
- randomize assignment/order;
- reverse pair order;
- use fresh sessions;
- block/stratify by model family;
- record model version and date.

## 5. Preference measurement

Prefer pairwise choices over arbitrary 1-10 ratings.

Store raw comparisons:
A, B, ordering, chosen, abstained, model, run.

Fit Bradley-Terry (or Plackett-Luce for ranked lists) as a projection. Never throw away raw comparisons.

Measure:
- position consistency
- repetition stability
- abstention
- judge-family effects

## 6. Explanations

After the choice, optionally ask for:
- short public rationale
- structured reason codes
- runner-up
- runner-up weaknesses
- up to 3 challenger suggestions

Reason codes should be bounded, e.g.:
SEMANTIC_MATCH, ACTION_ORIENTED, SHORT, PRONOUNCEABLE,
KNOWN_TECH_TERM, LOW_AMBIGUITY, TRUST_SIGNAL, TLD_SIGNAL.

Treat these as self-reported interpretation, not proof of causality.

New suggestions enter the *next* experiment round. They must not alter the current trial.

## 7. Evolutionary candidate search

Round N:
- deterministic candidates
- model-generated candidates
- human candidates
- prior winners

Then:
availability -> deduplicate -> blind tournament -> select elites.

Ask independent generators for mutations/challengers.
Round N+1 tests them fresh.

Maintain lineage:
candidate_id, parent_ids, generator, prompt_version, created_at.

## 8. Real-world outcome hierarchy

Evidence strength is contextual, but downstream behavior should be retained:

model rationale
-> repeated controlled choice
-> cross-model choice
-> human preference
-> registrar click
-> registration transition
-> deployment
-> real retrieval/open/citation
-> actual API/MCP invocation

Do not call registration-transition evidence proof that *your* user bought the domain.

## 9. Holdouts and generalization

Maintain:
- intent holdout: unseen categories
- temporal holdout: future model versions
- model-family holdout where feasible

A rule discovered on "developer APIs" is not universal until it transfers to unrelated intents.

## 10. Statistical reporting

For each claim store:
- hypothesis_id
- preregistered primary metric
- N
- model families
- intents
- effect estimate
- uncertainty interval
- test/estimator
- exclusions
- experiment version
- date range
- replication status

Use clustered/bootstrap uncertainty when observations share intent/model/session. Correct for multiple comparisons in broad exploratory sweeps. Mark exploratory findings separately from confirmatory tests.

## 11. Evidence library

Do not store prose "SEO rules" as timeless truth.

Store hypotheses such as:

H-0041: Explicit interface nouns in titles improve selection for API-task intents.
Status: replicated / provisional / failed
Effect: ...
CI: ...
Models: ...
Intents: ...
Date range: ...
Known moderators: ...

AgentSEO recommendations are generated from the current evidence library and include the evidence IDs behind each recommendation.

## 12. Threats to validity

Always test/report:
- position bias
- provider/search-engine confounding
- model self/family preference
- prompt sensitivity
- temporal drift
- personalization/location effects
- candidate-set effects
- contamination from prior candidate generation
- synthetic SERP vs real-search differences
- retrieval vs reranking vs generation/citation stage

The purpose is not to claim universal "LLM preferences." It is to estimate behavior under a reproducible protocol and track how it changes.
