# EXPERIMENT ROADMAP v2 — from FinalBuilds surface scan + frontier (2026-08-23)

Sources: finalbuilds2 repo audit · finalbuildsdomain oracle/lifecycle · arXiv 2606.04990
(traces→trust survey) · 2607.01641 (Infinite Agentic Loops) · MCPTox/AgentCheck/TrustDesc line.

## Key findings that shape the roadmap

1. **`sensor_agent_visibility` is declared in 6/8 site manifests but has NO implementation.**
   A named empty slot in the fleet. First real agent-visibility data wins immediately.
2. **H2P1 forecast ("agent-facing endpoints ≥3:1 usage vs human") is AWAITING_DATA.** The
   resolver needs `signal.*` series we can generate.
3. **EvidenceClaimV1 schema has no first-class ingest path yet** — venturelab downshifts to
   generic `research.recorded`. Our receipts bundle is ready; the pipe is the bottleneck.
4. **ExperimentEngine exists with deterministic cohort assignment**, and `docs/EXPERIMENTS.md`
   pre-lists treatments: llms.txt structure, markdown alternates, MCP discovery placement,
   pricing presentation. Nobody has run them.
5. **domainnamechecker.dev serves live REST + /mcp** — a REAL agent-invocable surface for L3/L4.
6. **Frontier gap:** IAL paper shows agents loop when feedback is unbounded — nobody has measured
   WHICH tool error styles cause retry storms. Provenance survey makes receipts first-class;
   dell2 already does proof-carrying verification — untested as a selection/trust lever.

## Queue (priority order)

### ASL-004F — Field: llms.txt / MCP-discovery ladder on domainnamechecker  [L4, highest]
Instrument the LIVE product via ExperimentEngine cohorts:
arms = llms.txt absent/present × /mcp listed in llms.txt or not.
Measure: cf-usage api.calls split agent-vs-human (UA + /mcp path), selection via MCP logs.
Feeds: H2P1 resolution, sensor_agent_visibility implementation, convergence-detector queue.
Cost: config + sensor code only; runs continuously.

### ASL-010 — Error-style → retry-storm dose-response  [L2, novel, cheap]
Same broken tool, vary FAILURE STYLE: auth-required / timeout / empty-200 / malformed-JSON /
slow-degrade. Measure repeated invocation count per episode before agent gives up.
Hypothesis: polite structured errors stop loops; empty responses cause Infinite-Agentic-Loop
behaviour. Direct tie to 2607.01641; product implication = error-message design for tools.

### ASL-005 — Parameter-schema complexity vs invocation validity  [L2, queued already]
Simple→complex schemas on identical functionality; valid-invocation rate + latency.
Feeds Hydra's interface-constraint arm of the capability-bottleneck thesis.

### ASL-009 — Verifiable receipts: trust + repeat-use panel  [L2→L3]
Same correct answer with vs without dell2-style proof receipt. Measures: initial selection
(expected null), stated confidence, REPEAT-pick rate across sessions (expected positive).
Ties lab to dell2's existing capability and the provenance-survey agenda.

### ASL-002D — Fluff dose-response curve  [L2, extends running experiment]
Fluff intensity 0/1/2/3 (adjectives → full marketing paragraph). Per-family EC50 of seduction.
Quantifies the benign-MCPTox attack surface; directly reusable as description-audit tooling.

### ASL-PRIX — Pricing presentation effect  [L2, pre-listed by finalbuilds2]
Machine-readable price field vs prose price vs hidden. Selection effect on identical tool.
Zero prior art found in agent literature; x402 capability on platform provides the surface.

## Explicitly deprioritised
- More ASL-001 n-scaling beyond current 206 (direction stable within families).
- ASL-007 name×description factorial until ASL-002 verdict lands (would confound).

## Rule reminders
L2 lab results enter Hydra as EvidenceClaims (receipts bundle); L4 field results land as
signal.* observations via POST /v1/events so convergence-detector sees them. Anomalies only,
never recommendations.
