# Field Observation Protocol v1
**Board:** agentseo-field · **Status:** ACTIVE (v1.0, 2026-08-23) · **Scope:** frozen SiteIntents → real search/open/citation traces only

---

## 0. Purpose and estimand

This protocol operationalizes abuse.md sprint item 7 ("Field runner: search-capable agents on frozen SiteIntents; ingest real traces") for the first field intent.

**Estimand (fixed before any run):**
For intent `I` and subject `S` = (provider, model, profile, harness), estimate:

| Metric | Definition |
|---|---|
| `search_activation_rate` | P(≥1 web search issued \| task given) |
| `query_count` | distribution of searches per trial |
| `target_retrieval_rate@10` | P(target URL in top-10 of any result set) |
| `target_open_rate` | P(opened \| retrieved) |
| `target_citation_rate` | P(URL appears in final report) |
| `task_success_rate` | P(final report names ≥1 service with resolvable URL) |
| `search_depth`, `reformulation_count` | behavioral depth |

All metrics are computed **only** from recorded event streams. No metric may be derived from model self-report ("I would search X") or analyst judgment about which results "should" win.

## 1. Frozen SiteIntent contract

An intent is frozen when it exists as a row in `lab.db.site_intents` with a stable
`intent_id` + `intent_hash`. The hash is computed over the canonical payload by
the existing lab tooling (`models.rs canonical_hash`). After freezing:

1. **No mutation.** Any wording change ⇒ new `intent_id`; the old row is never edited.
2. **Downstream references only via `intent_id` + `intent_hash`.** Every trial,
   query, observation carries both.
3. **No candidate leakage.** Per FIELD_TRACE_SPEC: "the agent must not see generated
   candidate domains before its initial search trace." The task prompt contains
   ONLY the intent fields (purpose / primary_job / audiences / capabilities /
   language). No domain suggestions, no example URLs, no expected answers.
4. **Provenance.** `payload_json.metadata.protocol_version` records which protocol
   version ran against this intent.

### 1a. Intent F-001 "find domain availability API" (first frozen field intent)

```json
{
  "purpose": "Locate a public API that checks whether a given domain name is available to register",
  "primary_job": "find-domain-availability-api",
  "audiences": ["autonomous AI agents", "developers"],
  "capabilities": ["domain availability check", "structured API response", "free or metered execution"],
  "language": "en",
  "constraints": {},
  "prohibited_meanings": [],
  "metadata": {"protocol_version": "field-v1", "board": "agentseo-field"}
}
```

## 2. Subjects (real agents, fresh sessions)

A subject is a concrete runnable configuration. Current inventory:

| Subject ID | Harness | Model | Provider | Search-capable? | Notes |
|---|---|---|---|---|---|
| S1 | `hermes --profile scout -z <task>` | mimo-v2.5 | opencode-go | VALIDATED 2026-08-23: live browsing confirmed (whoisxmlapi.com, developer.godaddy.com, rapidapi.com reached) | primary |
| S2 | `hermes --profile curator -z <task>` | mimo-v2.5 | opencode-go | same harness | secondary |
| S3 | `hermes --profile patala -z <task>` | mimo-v2.5 | opencode-go | same harness | secondary |

**Validated network environment (2026-08-23, S1):** Google SERP returns a
captcha interstitial (`/sorry/index`) to the sandbox browser; DuckDuckGo HTML
reachable but organic links render as SPA refs (no stable ranked URL list);
direct vendor sites reachable. Brave API requires a subscription token
(422 without). Consequence: `search_results` events are frequently UNAVAILABLE
as ranked lists in this environment; `search_query` intent is still recorded
from navigation-to-search-engine URLs, and opens/citations carry the evidence.
This is an environment property, recorded per trial in
`network_environment` — never papered over with synthetic SERPs.

Rules:
- **One fresh session per trial** (`-z` oneshot guarantees this). Never continue a session across trials.
- Log provider/model/profile/harness with every trial.
- **No synthetic subjects**: no scripted fake SERPs, no mocked search backends, no replayed traffic presented as live. If a subject cannot reach the open web during a trial, that fact is recorded (`search_activation = 0`) — it is data, not failure to paper over.
- Subjects never receive candidate domains, target URLs, or success criteria beyond the intent itself.

## 3. Event vocabulary (trace-only recording)

Exactly the event types of `docs/FIELD_TRACE_SPEC.md`, encoded into the envelope
of `schemas/observation.schema.json` (`evidence_tier="field"`):

| Event | Source | Payload fields | Extraction rule |
|---|---|---|---|
| `search_query` | assistant `tool_calls` where name ∈ {`web_search`,`browser_navigate`} | `query`/`url`, `tool`, `call_id`, `seq` | verbatim argument text; no paraphrase |
| `search_results` | tool-role message following a search call | `results[] {rank,url,title,domain}`, `query_ref` | rank = order in returned list |
| `result_open` | assistant `tool_calls` `browser_navigate(url≠search-engine)` | `url`, `rank`?, `query_ref`? | rank filled only if derivable deterministically |
| `citation` | final assistant prose containing URL(s); also `read_file`/`terminal` output quoting a fetched URL | `url`, `where` ∈ {final_report, tool_output} | regex URL extraction, deduped, order-preserving |
| `final_choice` | last assistant prose block | `named_services[]`, `report_excerpt≤2000B` | verbatim excerpt; no interpretation |
| `rationale` | optional explicit post-decision rationale (FIELD_TRACE_SPEC allows) | `text` | only if the subject volunteers one; never solicited mid-trace |

Extraction is **deterministic parsing of recorded messages** (Hermes state.db
`messages` table: assistant rows carry `tool_calls`; tool rows carry outputs).
No human annotates events. Unknown/unmappable actions are recorded as
`observation.event_type="tool_invocation"` with `payload.mapped=false` — explicit
UNKNOWN, never guessed into a cleaner category.

## 4. Trial procedure (per trial)

1. Freeze check: intent row exists, hash matches stored value; else abort.
2. Record `trial_start` (utc iso, subject config).
3. Launch fresh session with prompt = intent-derived task (Appendix A template).
4. Wait for completion (hard timeout 600 s; timeout ⇒ `completed_at=null`,
   `task_success=null`, partial trace still ingested).
5. Extract event stream from the session store (Section 3 rules).
6. Persist trial row + queries + observations atomically (one transaction).
7. Compute nothing at ingestion time beyond deterministic extraction. Metrics are projections computed later by analysis code from raw events.

## 5. Ingestion contract

Two sinks, one source of truth (raw JSON first, DB second):

```
runs/field/<ts>_<subject>/trace_raw.json     # immutable raw extraction
lab.db.field_trials                          # 1 row per trial
lab.db.search_queries                        # N rows per trial
lab.db.observations                          # M rows per trial (envelope)
```

- `trace_raw.json` is written BEFORE db insert; db ingest is idempotent on
  `(session_id)` — re-running ingest updates no rows, inserts no duplicates.
- FieldTrial row mirrors Rust `FieldTrial` struct exactly (agent_model,
  agent_version, provider, session_id, started_at, completed_at, final_action,
  task_success).
- Every observation row: `{observation_id, experiment_id=NULL, intent_id,
  evidence_tier='field', event_type, model_family, model_version, provider,
  session_id, created_at, payload_json}` — validates against
  `schemas/observation.schema.json` before insert.
- **Known-bug routing:** the Rust CLI's `record-field-trial` does not populate
  `search_queries` (abuse.md correctness list). Until fixed upstream, ingestion
  goes through the Python ingester (`runner/field.py`) which writes all three
  tables directly and transactionally. The Rust path stays reserved for
  single-trial manual inserts.

## 6. Anti-contamination controls

1. Task prompt built only from frozen intent fields (no examples, no hints).
2. Fresh session per trial — no memory/caching across trials (verified: `-z` sessions are isolated; session store keyed by unique session id).
3. Generator/judge separation: this board records traces only. Judgments (which service is "best") belong to other boards; none are produced here.
4. No chain-of-thought capture (FIELD_TRACE_SPEC prohibition). Only tool/action surfaces and final prose.
5. Subject identity logged per row; cross-subject aggregation happens only at analysis time, stratified by (model, version, date).

## 7. Threats to validity tracked from day one

| Threat | Mitigation / recorded covariate |
|---|---|
| No-web-access environment (sandboxed host) | record `network_environment` covariate per trial from deterministic probes; activation=0 runs kept and labeled, never silently dropped |
| Provider/search-backend drift | every result set stored verbatim incl. ranks; date+model_version on every row |
| Position bias within result lists | full ranked result sets retained, not just opens |
| Prompt sensitivity | prompt template version-pinned (Appendix A); changes ⇒ new template_version |
| Session contamination | fresh `-z` session per trial, session_id uniqueness asserted at ingest |
| Selection effects in citation detection | dual-source rule (final prose AND tool outputs), both recorded |
| Small-N overclaiming | all reports carry N, per-subject breakdowns; no cross-intent claims until holdout intents exist |

## 8. What this protocol does NOT do

- No quality judgments about which domain-availability API is better.
- No ranking of services; `final_choice` stores what the subject named, verbatim.
- No synthetic SERPs, mock searches, or imagined citations.
- No private reasoning capture.
- No edits to lab-tier tables (`pairwise_comparisons`, `experiments`, ...).

## 9. Acceptance criteria for a valid trial batch

1. ≥1 trial persisted with matching `trace_raw.json`.
2. All observation rows pass schema validation.
3. `intent_hash` recomputed from payload matches stored hash.
4. Zero rows in `observations` with unmapped event_type outside the Section-3 table.
5. Batch summary emitted with counts per event_type and per subject — counts only, no judgments.

**Batch status 2026-08-23 (v1.0, closed):**
- Pilot trial `ft_0f76d3fca4e1` (session 20260823_023900_f63b4b, S1): ingested,
  31 events (2 search_results-context, 6 result_open, 14 citation, 8
  tool_invocation, 1 final_choice), task_success=1. Trace:
  `results/field/20260823T024100Z_scout_f001pilot/trace_raw.json`.
- **Scale-up batch (t_edd74d74, 2026-08-23): n=9** — S1 scout ×5
  (`f63b4b`, `960c77`, `16eddc`, `16f604`, `03c1ed`), S2 curator ×2
  (`c39d9b`, `984e33`), S3 patala ×2 (`5385fb`, `89a70a`).
  Aggregate counts (`runner/field_summary.py --json`): n=9,
  search_activation_rate=0.889, task_success_rate=0.667.
  Per-subject: scout success 3/5 activation 5/5; curator success 1/2
  activation 1/2; patala success 2/2 activation 2/2. Counts only; the §7
  small-N caveat is narrowed but cross-intent claims still prohibited.
- **Attribution correction applied during scale-up:** subject profiles run
  subagent delegation (subagent sessions land in the same profile state.db,
  first-user prompt rewritten by the delegator) and S3 patala shares its
  state.db with a foreign eval workload. The original "latest session"
  heuristic therefore mis-attributed 4 sessions as trials: scout subagent
  `42f7d4` (was `ft_a691f61b735b` — superseding the earlier replication
  entry above; the real trial-2 session is main `960c77`, now ingested as
  `ft_1fb9bb8600c3`), curator subagents `d9484f`/`0bb531`, and one foreign
  patala eval session `1b2b27`. All 4 rows were purged from lab.db and their
  trace dirs quarantined unmodified under `results/field/superseded/`
  (bytes preserved, provenance in dir name). Fix: extraction now requires
  top-level CLI sessions (`parent_session_id IS NULL`, `source='cli'`)
  whose first user message equals the frozen Appendix-A template, and merges
  direct subagent streams into the trial trace with per-event
  `origin_session` provenance (delegation is subject behavior; merge level
  verified non-nested). Runner discovery uses the same deterministic rule;
  regression tests added to `tests/test_field_protocol.py`.
- Acceptance criteria §9 verified 2026-08-23 (scale-up pass):
  (1) 9/9 trials persisted with matching `trace_raw.json` and observations;
  (2) 379/379 field observation rows validate against
      `schemas/observation.schema.json` (jsonschema Draft 2020-12, 0 violations);
  (3) F-001 `intent_hash` recomputed from payload == stored hash
      (bb97d40a…);
  (4) 0 observation rows outside the §3 vocabulary (all sessions);
  (5) batch summary emitted above with per-subject breakdowns —
      counts only, no judgments.
- Self-tests: `tests/test_field_protocol.py` — 27 passed, 0 failed.

---

## Appendix A: Task prompt template (v1)

```
Find a domain availability API: a service that checks whether a domain name is
available to register. Use your web search and browsing tools to find real
services. When you have found one, report its name and URL.
```

Template version-pinned. The prompt contains no candidate names, no example
domains, no evaluation criteria — only the frozen intent's job.

## Appendix B: Subject invocation

```bash
timeout 600 hermes --profile scout -z "$(cat task_prompt.txt)" \
  > stdout.txt 2> stderr.txt
```

Exit code, wall time, and stdout size recorded per trial. Timeout (exit 124)
⇒ partial-trace ingestion per §4.4.

## Appendix C: Extraction mapping (deterministic)

```
assistant.tool_calls[].function.name == "web_search"
    → search_query{query=args.query}
assistant.tool_calls[].function.name == "browser_navigate"
    → url=args.url; search-engine host ⇒ search_results context marker;
      other host ⇒ result_open
tool.role rows following call_id X
    → search_results{results=parse(output)} if X was a search call
last assistant content block
    → final_choice{report_excerpt} + citation{urls in prose}
any tool output containing http(s)://…
    → citation{where="tool_output"}
unmapped tool call
    → tool_invocation{mapped=false}   # UNKNOWN stays explicit
```
