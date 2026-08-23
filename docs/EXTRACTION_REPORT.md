# domainnamechecker + finalbuildsdomain Extraction Report
*2026-08-23 · Full analysis of importable logic and experiment designs*

## From domainnamechecker

### Verification Pipeline (worker/dist/index.js)
Three-stage evidence: dnsProbe → rdapCheck → status resolver with confidence scores.
Every result carries evidence array, authoritative flag, verified_at, schema_version.

Key rules to adopt:
- "Never map no-DNS-records to available"
- "Conflicts resolve to UNKNOWN + recheck"
- 5-state model: AVAILABLE/TAKEN/RESERVED/PREMIUM/UNKNOWN

### AGENT_PREFERENCE_TESTING.md — Four-Experiment Progression
A: Query generation from frozen intent → search-language corpus
B: Domain generation from intent alone ("choice is the datum")
C: Blind preference tournament w/ AB/BA reversal + BT projection
D: Search-result choice w/ factorial decomposition (DOMAIN+12.8%, TITLE+18.1%, DESC+7.4%)

Plus: evolutionary candidate search, three preference distributions (P_agent/P_human/P_purchase),
evidence hierarchy (model explanation < choice < cross-model < human < registrar < deployment < invocation)

### SCIENTIFIC_METHOD.md — Estimand-first design
Declare estimand per experiment (never one universal score). Immutable SiteIntent hash.
Field-trial protocol: fresh agent + ordinary tools, record only observable traces.
Controlled-lab trio: hostname-only / snippet / machine-readable trials.
Holdout taxonomy: intent holdout, temporal holdout, model-family holdout.
Threats-to-validity checklist §12: position bias, self/family preference, prompt sensitivity,
temporal drift, candidate-set effects, contamination, synthetic-vs-real divergence.

### FIELD_TRACE_SPEC.md + observation.schema.json
Event names: search_query → search_results → result_open → citation → final_choice
Observation envelope adds evidence_tier + event types.
Isolation rules: no candidate leakage pre-trace; don't force equal rankings.

### AGENTSEO_EVIDENCE_LIBRARY.md
Hypothesis records (H-0041 style) + evidence grades A–E:
A=replicated field · B=replicated causal+compatible field · C=controlled · D=exploratory · E=hypothesis only

### FRONTIER_NOTES.md
Five design implications: end-to-end evaluation, execution-grounded ranking,
engine-specific stratification, BRIGHT reasoning retrieval, never equate controlled with field.

### OPTIMIZATION_REPORT.json
15-check agent-readiness battery (llms.txt, OpenAPI, MCP annotations, provenance,
structured errors, batch ops, cache TTL, schema versioning) — each check = factorial treatment variable.

## From finalbuildsdomain

### DomainOracle.decide() — promotion ladder keyed on usage metrics
KEEP_EXPERIMENT (<10 calls) → KEEP_SUBDOMAIN (<100) → PROMOTE_SUBDOMAIN → ACQUIRE_DOMAIN → ACQUIRE_DOTCOM

### calculateValueScore() — 7-metric weighted blend
dailyCalls .30, uniqueCallers .20, recurringCallers .15, agentCalls .15, revenue .10, impressions .05, referrers .05

### validate() — post-deploy health matrix {dns, tls, http, openapi, mcp}
MCP verified by actual tools/list POST — TASK_VERIFIED primitive

### Promotion-is-additive funnel
2000 capabilities → 400 MCP-worthy → 150 UI-worthy → 25 .xyz → 3 .com

## Sandbox Improvements
1. 5-state verification model with confidence + authoritative flags
2. Port dnsProbe + rdapCheck as L2 verifier pair
3. claimed_vs_verified audit primitive
4. Provenance metadata on all outputs
5. Structured errors {code, message, retryable, retry_after_ms}
6. Cache TTL by evidence type
7. generateCandidates() as deterministic control arm
8. Extend observation schema with evidence_tier + FIELD_TRACE_SPEC event names
