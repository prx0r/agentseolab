"""Ground-truth-verified statistical + validity gates."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'analysis'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runner'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'archive', 'legacy', 'analysis'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'archive', 'legacy', 'runner'))

def test_wilson_matches_statsmodels():
    from wilson import wilson
    # values cross-checked against statsmodels proportion_confint(method='wilson')
    r = wilson(6, 6)
    assert abs(r["ci95"][0] - 0.610) < 0.005 and r["ci95"][1] == 1.0
    r = wilson(0, 10)
    assert r["ci95"] == [0.0, 0.278]
    r = wilson(16, 16)
    assert abs(r["ci95"][0] - 0.806) < 0.01 and r["excludes_0.5"]

def test_wilson_bounds_never_exceed_unit():
    from wilson import wilson
    for k in range(0, 11):
        for n in (10, 30):
            lo, hi = wilson(k, n)["ci95"]
            assert 0.0 <= lo <= hi <= 1.0

def test_validator_rejects_substring_collision():
    from validator import validate_canary, ValidationError
    spec = {"capability_id":"x","job":"j","seed":1,"n_trials_per_decoy":2,
      "real_tool":{"tool_id":"t1","name":"domain.verify","description":"d"},
      "decoys":[{"tool_id":"t2","class":"parameter_trap","name":"domain.verify.pro","description":"d2"}]}
    try:
        validate_canary(spec); assert False, "should reject substring collision"
    except ValidationError as e:
        assert "substring-collision" in str(e)

def test_validator_rejects_missing_identity():
    from validator import validate_canary, ValidationError
    spec = {"capability_id":"x","job":"j","seed":1,"n_trials_per_decoy":2,
      "real_tool":{"tool_id":"t1","name":"domain.verify","description":"d"},
      "decoys":[{"class":"c","name":"other.tool","description":"d"}]}  # no tool_id
    try:
        validate_canary(spec); assert False
    except ValidationError as e:
        assert "tool_id" in str(e)

def test_validator_accepts_clean_spec():
    from validator import validate_canary
    spec = {"capability_id":"domain_verify","seed":42,
            "job":"check availability of example-name.com",
            "real_tool":{"tool_id":"tool_real_001","name":"domain.verify","description":"RDAP+DNS verification"},
            "decoys":[{"tool_id":"tool_decoy_001","class":"semantic_decoy","name":"domain.scout","description":"web mention search"},
                      {"tool_id":"tool_decoy_002","class":"temporal_decoy","name":"snapshot.check","description":"cached lookups"}],
            "n_trials_per_decoy": 3}
    assert validate_canary(spec) is True

def test_choice_parser_distincts():
    import re as _re
    def parse_choice(raw):
        s = raw.strip()
        low = s.lower()
        if "abstain" in low or "neither" in low:
            return "ABSTAIN"
        for ch in (s[:2], s[-2:]):
            for c in ch:
                if c in "AB":
                    return c
        m = _re.findall(r"\b([AB])\b", s)
        return m[0] if len(set(m)) == 1 else "UNPARSEABLE"
    assert parse_choice("A") == "A"
    assert parse_choice("B") == "B"
    assert parse_choice("ABSTAIN") == "ABSTAIN"
    assert parse_choice("The tool is clearly B for this job.") == "B"
    assert parse_choice("hello world no letters") == "UNPARSEABLE"

def test_canonical_hash_order_independent():
    import json, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runner'))
    from experiment import canonical_hash
    a = canonical_hash({"b": 1, "a": {"y": 2, "x": 3}})
    b = canonical_hash({"a": {"x": 3, "y": 2}, "b": 1})
    assert a == b, "key order leaked into hash"
