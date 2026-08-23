# AgentSEOLab Dev Plan — Experimental Validity Hardening
**2026-08-23 02:40 UTC · supersedes sprint order in abuse.md until items 1–10 complete**

## Prime directive
No effect enters the evidence library unless the experiment itself has passed validation.
Unit of output: a replicated experimental effect with provenance and uncertainty.

## P0 findings (this review)
1. H-CANARY-001 INVALIDATED — CANARY_IMPLEMENTATION_DEFECT:
   a) backend object passed as `job` positional arg
   b) parameter_trap scored impossible (real.name == decoy.name ⇒ substring
      exclusion contradiction ⇒ 0/2 guaranteed by scorer, not discovered)
2. Statistics mislabeled: 2-option proportion + broken bootstrap ≠ Bradley–Terry.
   Use Wilson/exact binomial CI for 2 candidates; BT reserved for multi-item
   latent-strength tournaments.
3. Evidence library promoted on backend prefix (session_id[:3]) not model
   identity; no validity/holdout/significance/protocol gates. Fail-closed now.
4. Runner metadata lied: spec claimed hermes/opencode-go while trials may run
   on any backend; per-trial provenance discarded.
5. Seed stored but unused.

## Lifecycle vocabulary (evidence)
PROPOSED PREREGISTERED RUNNING PROVISIONAL CONFIRMED REPLICATED
FAILED_REPLICATION INVALIDATED STALE
INVALIDATED = machinery defect (retain forever, never delete).
FAILED_REPLICATION = valid protocol, effect didn't replicate. Different things.

## Execution order
1. Invalidate H-CANARY-001 (preserve record, cite offending commit, affected runs)
2. Automated tests (pytest): canonical_hash determinism, choice parser,
   validator rejection cases, Wilson CI bounds, promotion gates
3. validate_experiment(spec) gate before any run
4. CanarySpec rewrite: immutable tool_ids, unique names v1 (same-name ambiguity
   deferred to instance-ID protocol), structured selection, UNPARSEABLE ≠ wrong,
   correct job passing (keyword-only args)
5. Trial-level runtime provenance: provider, model_id, temperature, max_tokens,
   prompt_hash, response_hash, spec_hash, runner_commit, timestamps, ordering
6. Statistics: Wilson score CI (2-candidate); cluster-aware bootstrap later;
   real BT deferred until multi-candidate tournaments exist
7. Promotion gates: CONFIRMED = preregistered-valid + n≥30 + Wilson CI excludes
   0.5; REPLICATED = independent rerun, different model family, same direction,
   CI excludes 0.5. No manual upgrades.
8. Rerun canary (fixed) on ≥2 genuine model families
9. Cross-family replication check
10. Execution-grounded MCP sandbox (selection→params→invoke→verify) next wave

## Later phases (do NOT start before 7)
Factorial MCP field mutations · WebMCP adversarial lab · A2A Agent Card lab ·
AgentSearchBench adapter · L0-L4 evidence ladder · evolution campaign · Cogym bridge.

## Hygiene
Git holds code/schemas/specs/fixtures only. Raw runs → artifacts/ (gitignored,
content-addressed filenames). lab.db, logs/, __pycache__/ gitignored.
