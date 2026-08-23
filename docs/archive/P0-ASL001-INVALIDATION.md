# ASL-001 Validity Sprint — P0 Bug Fixes + Redesign
**2026-08-23 · SUPERSEDES all prior ASL-001 results**

## Status: ALL PRIOR ASL-001 RESULTS MARKED PILOT_INVALID

Prior results are retained as research provenance but are NOT valid evidence because:

1. **Verifier doesn't verify**: `output_has_registered_field` computed but not required for pass. Real condition = "real tool invoked + correct domain arg" — a failed lookup still passes.
2. **Parameters not executed**: runner supplies `{"domain":"example-name.com"}` itself. Model's actual parameter construction is discarded.
3. **DNS is not registration**: A-record presence ≠ registered domain. Google DoH is recursive resolver, not authoritative registry oracle.
4. **Seed is non-deterministic**: Python `hash()` is salted between processes → identical seed ≠ identical trial order.
5. **Treatment confounded**: simultaneously varies name, description wording, impressiveness, functionality, credential requirement, and A/B label assignment.
6. **Audit doesn't cover new format**: scans `runs/exp_*.json` not `results/experiments/ASL001_*.json`.
7. **Peer review overclaims**: 8/10 unparseable ≠ "prefers broken tool." Unparseable is its own category.

## Fix Plan (P0)

### 1. Deterministic hidden registry (replaces live DNS)
```
foo.test → REGISTERED
bar.test → AVAILABLE
baz.test → REGISTERED
```
Agent cannot inspect the registry. Verifier can. Perfectly replayable.

### 2. 2×2 factorial design
```
                WORKING         BROKEN
Plain desc      tool_A          tool_B
Fluffy desc     tool_C          tool_D
```
Opaque randomized IDs. Measures independently:
- Does fluff increase invocation?
- Does capability quality increase verified success?
- Does fluff lure agents toward nonfunctional capabilities?

### 3. Agent must construct parameters
Runner does NOT supply correct args. Model must emit valid JSON with correct parameters. Parameter validity checked before execution.

### 4. Stable seed
`seed_int = int(hashlib.sha256(str(seed).encode()).hexdigest(), 16)`

### 5. Verifier requires ALL four conditions
- real_tool_invoked ✓
- correct_domain_used ✓  
- output_has_registered_field ✓
- output_registered_matches_hidden_registry ✓

All must be true for TASK_VERIFIED.

### 6. Audit covers new experiment format
Add results/experiments/ASL001_*.json to audit scope.

## ExperimentSpec v3

```python
ExperimentSpec(
    hypothesis="...",
    estimand="P(TASK_VERIFIED | treatment) - P(TASK_VERIFIED | control)",
    treatment={"description": "...", "actually_works": True},
    control={"description": "...", "actually_works": False},
    primary_endpoint="TASK_VERIFIED",
    secondary_endpoints=["selection_rate", "parameter_validity", ...],
    unit_of_analysis="task × initial_state",
    task_population=["foo.test", "bar.test", ...],
    model_matrix=["M1", "M2", ...],
    rollout_count=3,
    seed=20260823,
    ...
)
```

## Prior Results Reclassification

| File | Old Status | New Status |
|------|-----------|-----------|
| ASL001_batch_20260823-052844.json | CONFIRMED/REPLICATED | PILOT_INVALID |
| ASL001_cloudflare_20260823-044410.json | REPLICATED | PILOT_INVALID |
| ASL001_cloudflare_20260823-044603.json | REPLICATED | PILOT_INVALID |
| canary_v2_oxalpha_free.json | PROVISIONAL | PROVISIONAL (valid — different scorer, no DNS bug) |

The canary v2 result (95.8% resistance on ox-alpha-free) remains VALID because it used the corrected scorer with distinct tool names.
PLANEOF
echo "saved"