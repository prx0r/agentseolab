"""Experiment validator — fail-closed gate before any run (P0 item 3)."""
class ValidationError(Exception): pass

def validate_canary(spec: dict):
    errs = []
    real = spec.get("real_tool") or {}
    decoys = spec.get("decoys") or []
    if not real.get("name"): errs.append("real_tool.name missing")
    if not real.get("description"): errs.append("real_tool.description missing")
    if not real.get("tool_id"): errs.append("real_tool.tool_id missing (immutable identity required)")
    if len(decoys) < 1: errs.append("no decoys")
    names = [real.get("name")] + [d.get("name") for d in decoys]
    ids   = [real.get("tool_id")] + [d.get("tool_id") for d in decoys]
    if len(set(filter(None, names))) != len([n for n in names if n]):
        errs.append("duplicate display names — same-name ambiguity requires instance-ID protocol (not supported v1)")
    if len(set(filter(None, ids))) != len([i for i in ids if i]):
        errs.append("duplicate tool_ids")
    for d in decoys:
        if not d.get("name"): errs.append(f"decoy missing name: {d}")
        if not d.get("tool_id"): errs.append(f"decoy missing tool_id: {d.get('name')}")
        if not d.get("class"): errs.append(f"decoy missing class: {d.get('name')}")
    # impossible-scorer guard: real name must not be substring of any decoy name or vice versa
    rn = (real.get("name") or "").lower()
    for d in decoys:
        dn = (d.get("name") or "").lower()
        if rn and dn and (rn in dn or dn in rn):
            errs.append(f"substring-collision real:{rn} decoy:{dn} — scorer would be ambiguous; rename decoy")
    n = spec.get("n_trials_per_decoy", 0)
    if not isinstance(n, int) or n < 2: errs.append("n_trials_per_decoy must be int >= 2")
    if not spec.get("seed"): errs.append("seed required")
    if not spec.get("job"): errs.append("job required")
    if errs:
        raise ValidationError("; ".join(errs))
    return True

def validate_pairwise(spec: dict):
    errs = []
    va, vb = spec.get("variant_a") or {}, spec.get("variant_b") or {}
    if va == vb: errs.append("variants identical")
    for v, label in ((va,"a"),(vb,"b")):
        if not v.get("description"): errs.append(f"variant_{label}.description missing")
        if not v.get("tool_name"): errs.append(f"variant_{label}.tool_name missing")
    if (va.get("tool_name") or "").lower() == (vb.get("tool_name") or "").lower():
        errs.append("same tool_name across variants breaks attribution")
    if (spec.get("n_pairs") or 0) < 2: errs.append("n_pairs >= 2 required")
    if not spec.get("seed"): errs.append("seed required")
    if not spec.get("intent_id"): errs.append("intent_id required (frozen intent prerequisite)")
    if errs: raise ValidationError("; ".join(errs))
    return True
