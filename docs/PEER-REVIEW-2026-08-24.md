# PEER REVIEW — DomainArena full audit + dev plan
Reviewed: prx0r/agentseolab @ 3c4d157 · 2026-08-24 · DevNetwork hackathon, deadline Sep 3 10am PDT

## Executive assessment
DomainArena moved fast into a credible product skeleton. Strongest progress:
live name.com production search, hard economic feasibility, web/API layer,
tamper-evident receipts, R2 archival, containerization, preserved AgentSEOLab
lineage. Currently in a dangerous middle state: README/Devpost narrative
describes the intended scientific product more strongly than the live path
implements. Next phase = TRUTH CONVERGENCE, not feature expansion.

## Biggest blockers (reviewer's list)
1. Live recommender uses placeholder evidence: pairwise_strength/task_success
   unset; model_stability is a structural length/vowel proxy mislabeled.
2. Registration is a stub — recheck-and-register doesn't actually recheck,
   refresh pricing, register, write DNS, or read back.
3. Ablation synthetic (reverse-alphabetical baseline etc.) — machinery test only.
4. PROOF_OF_CONCEPT.md / EXPERIMENT_LOG.md contradict corrected evidence —
   mark SUPERSEDED by RESULTS.md.
5. Pairwise scheduling doesn't guarantee balanced AB/BA; Bradley–Terry needs
   reference validation; semantic inversion defaults to one family;
   missing evidence converted to zero in optimizer.

## Key fixes directed by review
- EvidenceValue with explicit status: MEASURED | PROXY | NOT_MEASURED | STALE
  (+ protocol, n, families, windows, receipt_ids). Never call a structural
  proxy "model_stability".
- Missing evidence ≠ failure: renormalize weights over measured dimensions or
  block policy when mandatory dims missing; expose coverage ≥0.70 gate and
  INSUFFICIENT_EVIDENCE status; provisional recommendation label.
- Pareto front should RESTRICT selection, not just decorate it.
- Null price = infeasible/unknown, never free (fix -(price or 0)).
- Exact AB/BA scheduler: paired blocks randomized in order, not existence;
  test balanced first-position counts.
- Bradley–Terry: validate against choix/lmarena/statsmodels golden fixtures;
  test closed two-player, 3-player synthetic, disconnected graph, ties,
  permutation invariance.
- Semantic inversion LIVE mode requires ≥2 healthy families; visible
  execution mode {LIVE_MULTI_FAMILY|HEURISTIC_FALLBACK}; never mix heuristic
  fallback into live averages; frozen intent concept set for scoring; store
  raw response/provider/model/latency/session/serving-window in receipt.
- Execution moat redesign: capability-assignment Latin square (json_repair /
  timezone_convert / extract_url_hostname / normalize_email), domains rotated
  over implementations, one correct capability per task, hidden verifier
  checks exact result ⇒ P(correct capability ∧ verified | domain assignment).
- Stability: no pooled headline when zero stable families →
  INSUFFICIENT_REPLICATION with raw stats kept.
- API: explicit DOMAINARENA_MODE=live|fixture; live failures surface as
  errors/degraded, NEVER silent fixture fallback; fixtures labeled
  FIXTURE/NOT EVIDENCE; thread real intent_hash into Decision+receipts.
- name.com client: centralized _require_write_mode() on ALL mutating methods;
  default production-readonly; bounded backoff on 5xx; never retry 4xx except 429.
- Security: rotate CF token (was committed historically); gitleaks in CI;
  secret scanning pre-commit.
- Docker: pin deps (fastapi uvicorn pydantic httpx; pytest/respx dev-only);
  UI bind DOMAINARENA_HOST=0.0.0.0 in containers; revalidate api.name.com base.
- CI now: unit tests + import smoke + docker build + secret scan; distinguish
  offline deterministic vs provider-mock vs live-manual smoke.
- Repo hygiene: research/upstream/litellm full-tree vendor → submodule/source
  ledger w/ pinned SHAs; export SQLite→JSONL/CSV; drop ad-hoc API logs;
  compact index for the 105-page name.com docs import.
- UI: six-screen evidence product (intent → reality-filter funnel counts →
  arena matrix w/ MEASURED/PROXY badges → family disagreement → execution
  funnel EXPOSED→SELECTED→INVOKED→VALID_PARAMS→VERIFIED → decision/acquisition
  w/ DNS receipt).

## Checkpoints CP-A…CP-J
CP-A truthful live mode · CP-B name.com sandbox lifecycle (search→availability
→pricing→approval→CreateDomain idempotent→GetDomain→TXT receipt→read-back)
· CP-C arena math validated · CP-D ≥2-family real semantic inversion ·
CP-E execution Latin-square experiment (≥3 capabilities, counterbalanced,
UsefulSelection w/ CI) · CP-F cross-family replication (≥5 families, ≥30
trials/arm, 2 windows — reduce claims not rigor if impossible) · CP-G real
ablation on held-out execution tasks (or omit honestly) · CP-H UI evidence
productization · CP-I CI+deploy green · CP-J submission freeze 24–48h early.

## Schedule
Aug24–25 integrity+acquisition (rotate CF token, CI, live/fixture split, real
intent hash, optimizer missing-evidence semantics, write guards, sandbox
lifecycle, contact sponsor re 403) · Aug26 arena correctness · Aug27–28 real
experiment moat + capability world + DA-T4/T6 trials + second window ·
Aug29 ablation-or-omit, pick 2–3 strongest findings · Aug30 product UI ·
Aug31 reliability/deploy/fresh-machine/error UX/secret scan · Sep1 submission
package · Sep2 demo freeze (record video, regression only) · Sep3 buffer.

## What NOT to build
EvoName, HydraDB integration, crowdsourcing infra, logos/trademark workflows,
huge TLD catalogs, portfolio management, site deployment, second product,
SEO dashboard, SerpApi integration before name.com core is green, more
upstream clones.

## Claim tiers for final submission
VERIFIED PRODUCT FACTS (live inventory powers feasibility; hard budgets;
real purchase/renewal/premium data; hashed intent+evidence receipts;
approval-gated registration; idempotent sandbox lifecycle once CP-B done) ·
MEASURED RESEARCH FINDINGS (only current-ledger items w/ status labels:
serverless temp=0 serving-window variance CONFIRMED; family clustering
CONFIRMED; informative-description ceiling PROVISIONAL; position-vs-TLD
confound PROVISIONAL-corrected) · PRODUCT HYPOTHESES (clearly labeled:
execution-grounded ranking improves held-out agent success; some names/TLDs
more robust across agents; DomainArena improves registration conversion).
Do not convert hypotheses to facts until experiments land.

## Scored assessment (as reviewed tonight)
Concept/originality 9.5 · name.com centrality 8 · technical architecture 8.5 ·
scientific credibility 7 (real/proxy/mock mixing) · demo readiness 6.5 ·
startup story 9. After checkpoints: genuinely exceptional entry.

## Top five immediate
1 Truthful live/fixture/proxy semantics · 2 name.com sandbox lifecycle ·
3 AB/BA + Bradley–Terry correctness · 4 capability Latin-square experiment ·
5 UI evidence productization, then FREEZE THE DEMO.

## North-star sentence
A judge can trace a real product intent → real name.com inventory → measured
agent behavior → transparent recommendation → safely registered sandbox
domain — without any mock evidence being mistaken for reality.

---
## Credentials appended (SEPARATE from this file — stored in .env, gitignored)
Sandbox: tradesprior@gmail.com-test @ api.dev.name.com (token provided)
Production: tradesprior@gmail.com @ api.name.com (token provided, use readonly)
