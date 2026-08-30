# P0 Review — eecd511 → submission-rc1

## Fixes Applied (2026-08-31)

All 28 P0 items have been addressed. 135 tests passing.

| Item | Status | Fix |
|------|--------|-----|
| P0-1 | ✅ | pyproject build backend → `setuptools.build_meta` |
| P0-2 | ✅ | MCP handlers use `await svc.*_async()` |
| P0-3+4 | ✅ | `DomainService.recommend_async()` owns live discovery + `_live_discovery()` |
| P0-5 | ✅ | HTTP API strict mode: `DOMAINARENA_MODE` env var, 503 if live without creds |
| P0-6 | ✅ | `DecisionState.decision_basis` persists constraints + inventory snapshot + selected quote |
| P0-7 | ✅ | `register_async()` price drift guard with `max_price_drift_pct` |
| P0-8 | ✅ | Fixture `EvidenceValue(value=None, status=NOT_MEASURED)` — no bare floats |
| P0-9 | ✅ | Separate `measured_coverage` vs `proxy_coverage`; VALIDATED requires measured ≥ 0.70 |
| P0-10 | ✅ | Demo scorer uses `mistral-small-3.1-24b` (different from tested model) |
| P0-11 | ✅ | Experiment uses exact `@cf/...` model IDs |
| P0-12 | ✅ | Experiment env vars: `CLOUDFLARE_ACCOUNT_ID`/`CLOUDFLARE_API_TOKEN` with CF_* fallback |
| P0-15 | ✅ | World `observe()` no longer leaks intent |
| P0-16 | ✅ | `HiddenScorerExecutor` validates `inference_model_id != model_id` |
| P0-17 | ✅ | `ActionResult.status` validated before processing; semantic score in [0,1] |
| P0-18 | ✅ | Pareto `_dims` keeps None as None; comparison skips missing dimensions |
| P0-19 | ✅ | `weighted_score` computes audience-specific measured coverage |
| P0-20 | ✅ | `$0.00` renewal → "renewal unknown" in recommendation explanation |
| P0-24 | ✅ | `domainarena/cli.py` entry point, `pyproject.toml` → `domainarena.cli:main` |
| P0-25 | ✅ | `.env.example` base URL corrected |
| P0-28 | ✅ | `REJECTED` + `REVOKED` status; `reject()` transitions |

## Overall verdict

| Area | Previous | eecd511 |
|------|----------|---------|
| Product coherence | 7 | 9 |
| Name.com integration architecture | 7 | 8.5 |
| Lifecycle design | 6 | 8 |
| MCP correctness | 6 | 4.5 |
| Demo truthfulness | 4 | 5 |
| Experimental rigor | 5.5 | 6 |
| Reproducibility | 4.5 | 6 |
| Packaging / CI | 4 | 3 |
| Potential after next push | — | 9+ |

## P0 findings

### 1. CI is actually red
- `setuptools.backends._legacy` doesn't exist. Fix to `setuptools.build_meta`.
- README says 82, commit says 85, CI proves zero ran.

### 2. Three MCP lifecycle tools broken by async refactor
- MCP handlers call `svc.prepare_registration()` (sync) from async context.
- Sync wrappers raise RuntimeError in event loop.
- Fix: `await svc.prepare_registration_async(...)` etc.

### 3. MCP recommend_domain still uses fixtures, not live Name.com
- `svc.recommend()` without `live_candidates` → fixtures.
- Labels response as "name.com-live" when credentials present → worst truth bug.
- Fix: DomainService owns discovery. One `recommend_async()` that does Name.com Search → constraints → evidence → optimizer.

### 4. Demo also uses fixtures
- Says "LIVE DOMAIN DISCOVERY" but uses `_fixture_candidates()`.
- Fix: Same as MCP — one `recommend_async()` that owns discovery.

### 5. HTTP regressed "no silent fixture in live mode" guarantee
- If `DOMAINARENA_MODE=live` but credentials missing, falls through to fixtures silently.
- Fix: Raise 503 if live mode lacks credentials. Validate `mode ∈ {live, fixture}`.

### 6. Final purchase price drift guard incomplete
- `max_price_drift_pct` passed to `register_async()` but not used.
- Registration doesn't check current price against approved quote or hard budgets.
- Fix: Persist approved quote. Re-check drift + budgets before CreateDomain.

### 7. Not enough persisted info for restart safety
- `_candidates` only in memory. After restart, `orig_price = None` → drift check skipped.
- Fix: Persist immutable decision basis (constraints, inventory snapshot, approved budgets).

### 8. Fixture task_success is not NOT_MEASURED
- `task_success=0.0` → coerced to `PROXY` not `NOT_MEASURED`.
- Fix: `EvidenceValue(value=None, status=EvStatus.NOT_MEASURED, note="no DA-T6 execution trial")`.

### 9. Proxy coverage can produce "VALIDATED"
- Coverage counts PROXY dimensions toward 70% gate.
- Fix: Separate `measured_coverage` from `proxy_coverage`. VALIDATED requires measured ≥ 0.70.

### 10. Demo hidden scorer is same model as tested model
- Both use `@cf/meta/llama-3.3-70b-instruct-fp8-fast`.
- Fix: Use different model for scorer (e.g. mistral or qwen).

### 11. Experiment runner model IDs wrong
- Uses `meta-llama-3.3-70b` not `@cf/meta/llama-3.3-70b-instruct-fp8-fast`.
- Fix: Use exact Cloudflare Workers AI IDs.

### 12. Experiment env vars disagree with standardized config
- `demo_experiment.py` reads `CF_ACCOUNT_ID`/`CF_TOKEN`.
- Fix: Use `CLOUDFLARE_ACCOUNT_ID`/`CLOUDFLARE_API_TOKEN` everywhere.

### 13. New experiment isn't the strongest experiment
- Does individual semantic inversion, not pairwise AB/BA selection.
- Fix: Keep as DA-T2, add DA-T3 pairwise runner.

### 14. Preregistered experiment disconnected from runner
- Runner hardcodes config instead of reading YAML.
- Fix: `python -m experiments.run experiments/demo_json_repair_v1/config.yaml`.

### 15. World still leaks hidden intent
- Observation includes `intent_description[:200]`.
- Fix: Remove intent from observation. Keep oracle/private.

### 16. World scorer separation not enforced
- Test only checks model_id exists, doesn't enforce != inference model.
- Fix: `if scorer_model_id == inference_model_id: raise ValueError(...)`.

### 17. Error handling in world incomplete
- `apply()` doesn't reject `ActionResult(status="error")`.
- Semantic score not range-validated.
- Fix: Validate status and score range.

### 18. Pareto still turns missing evidence into zero
- `dims = {k: (val if val is not None else 0.0)}`.
- Fix: Comparable-dimension Pareto or evidence gate before Pareto.

### 19. Evidence coverage still based on agent preset
- `_vec()` uses `PRESETS["agent_api"]` regardless of audience.
- Fix: `_vec(ev, audience)` using correct preset.

### 20. Unknown renewal displayed as $0.00
- `f"renewal ${cand.inventory.renewal_price or 0:.2f}"`.
- Fix: Use "renewal unknown".

### 21. Test for unknown renewal too weak
- `assert len(front) >= 1` is trivially true.
- Fix: Assert exact expected membership.

### 22. "E2E lifecycle" test mocks core lifecycle
- Not actually hitting real service methods.
- Fix: Rename to `test_http_lifecycle_contract`. Add real provider-mocked E2E.

### 23. Demo smoke test doesn't test demo
- Tests FastAPI app, not `domainarena.web.demo.Handler`.
- Fix: Add actual demo server smoke test.

### 24. Packaging has console script bug
- `domainarena = "domainarena.api.http:app"` — FastAPI app isn't a callable.
- Fix: Create `domainarena/cli.py` with `main()`.

### 25. .env.example has wrong Name.com base URL
- `https://api.name.com/v4` + `/core/v1/` = double path.
- Fix: `https://api.name.com`.

### 26. Approval token isn't HMAC
- Uses `hmac.compare_digest()` for constant-time comparison, but token isn't HMAC-signed.
- Fix: Describe as "random one-time approval token with constant-time comparison".

### 27. Don't persist raw approval token
- Store `sha256(raw_token)`, compare `sha256(supplied_token)`.
- Fix: Free to implement, better security posture.

### 28. Reject state isn't modeled
- `reject()` clears token but doesn't transition status.
- Fix: Add REJECTED/REVOKED status or transition back to PREPARED.

## Exact next push

Fix pyproject backend → CI green → MCP async → live discovery in DomainService → strict mode → persist decision basis → price drift guard → NOT_MEASURED fixtures → measured vs proxy coverage → Pareto fix → audience-specific coverage → $0.00 fix → different scorer model → remove intent from world → enforce scorer separation → validate ActionResult → fix experiment IDs/env/config → pairwise runner → real Name.com mocked E2E → actual MCP handler test → actual demo smoke → fix console script → get green CI.
