# Runner
Backends read keys from `runner/.env` (gitignored — copy from `.env.template`) or process env:
`CF_ACCOUNT_ID`, `CF_TOKEN`, `OPENROUTER_API_KEY`, `OPENCODE_GO_API_KEY`.

## Sentinel suite (`sentinel_suite_v1`)

Fixed-trial drift replay of accepted experiments, fired on model/version change
(abuse.md item 10; validity-sprint A7: INVALIDATED findings are never baselines).

- Spec: `runner/sentinel_suite_v1.spec.json` — 2 cases:
  `pairwise_cancelme_evidence_vs_process` (H-0001 baseline p=1.0, n=22;
  5 pairs x AB/BA = fixed 10 trials) and `canary_domain_verify_v2`
  (H-CANARY-002 candidate; 6 decoy classes x 2 = 12 balanced trials).
- Run manually: `python3 -m runner.sentinel --force`
- Scheduled: hourly probe job `agentseolab-watch` (builder cron `572032c82616`)
  runs `~/.hermes/profiles/builder/scripts/sentinel_tick.sh`, which invokes
  `python3 -m runner.sentinel`; the runner fires the full replay only on
  model/version change vs `runs/sentinel_state.json`, else weekly fallback.
- Verdicts per case: OK / WARN (>0.08 abs) / DRIFT (>=0.15 abs) /
  UNKNOWN (n<6 or NO_VALID_BASELINE). Cross-model deltas are labeled
  CROSS_MODEL_COMPARISON (non-transfer signal), never auto-staled.
- Adopting a canary baseline after a clean run:
  `python3 -c "import sys; sys.path.insert(0,'runner'); import sentinel; print(sentinel.adopt_baseline(report_path='runs/<report>.json'))"`
  (moves the case off NO_VALID_BASELINE; changes the manifest hash by design).
