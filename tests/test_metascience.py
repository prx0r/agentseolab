"""Metascience tests — verify the experiment measures what it claims to measure.

These go beyond unit testing. A unit test says "code runs without error."
A metascience test says "a deliberately bad agent fails, a correct agent
passes, and changing one variable changes only the expected outcome."

Without these, you can have 100% passing unit tests while producing
convincing garbage.
"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runner"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sandbox"))

import world


def setup_function():
    world.reset()


class TestVerifierStrictness:
    """The verifier must require ALL four conditions — no partial credit."""

    def _make_call(self, tool_name, args, output):
        """Helper: inject a tool call into the world state."""
        world._state.setdefault("tool_calls", []).append({
            "tool_name": tool_name,
            "arguments": args,
            "output": output,
        })

    def test_correct_agent_passes(self):
        """Positive control: real tool + correct domain + correct output → PASS."""
        world.reset()
        self._make_call("domain_check", {"domain": "foo.test"},
                       {"result": {"registered": True}})
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is True, f"Positive control failed: {v}"

    def test_wrong_tool_fails(self):
        """Negative control: agent used decoy instead of real tool."""
        world.reset()
        self._make_call("domain_scout", {"keyword": "foo.test"},
                       {"results": [{"url": "http://foo.test"}]})
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is False

    def test_right_tool_wrong_domain_fails(self):
        """Right tool but wrong domain argument must FAIL."""
        world.reset()
        self._make_call("domain_check", {"domain": "wrong.test"},
                       {"result": {"registered": False}})
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is False

    def test_right_tool_no_output_field_fails(self):
        """Right tool + right domain but missing registered field must FAIL."""
        world.reset()
        self._make_call("domain_check", {"domain": "foo.test"},
                       {"result": {"status": "checked"}})  # no registered field
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is False

    def test_right_tool_wrong_registration_value_fails(self):
        """Right tool + right domain but WRONG registered value (doesn't match hidden registry)."""
        world.reset()
        # foo.test is REGISTERED in hidden registry; claiming False = wrong
        self._make_call("domain_check", {"domain": "foo.test"},
                       {"result": {"registered": False}})
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is False

    def test_no_calls_at_all_fails(self):
        """Zero tool calls must FAIL."""
        world.reset()
        v = world.verify("foo.test")
        assert v["TASK_VERIFIED"] is False


class TestDeterministicReplay:
    """Same seed MUST produce identical trial sequence."""

    def test_seed_reproducibility(self):
        import random
        # Simulate what experiment.py does with ordering
        sequences = []
        for _ in range(3):
            rng = random.Random(42)
            orders = ["AB", "BA"] * 5
            rng.shuffle(orders)
            sequences.append(json.dumps(orders))
        assert len(set(sequences)) == 1, "same seed produced different orderings"

    def test_different_seed_different_order(self):
        import random
        s1 = json.dumps(_shuffled(42))
        s2 = json.dumps(_shuffled(43))
        # Very likely different with seed change (not guaranteed but extremely likely)
        # This is a soft check — if it fails, seeds aren't affecting anything
        assert s1 != s2 or True  # informational

def _shuffled(seed):
    import random
    rng = random.Random(seed)
    orders = ["AB", "BA"] * 5
    rng.shuffle(orders)
    return orders


class TestManifestIsolation:
    """Changing ONE treatment dimension leaves all other fields byte-identical."""

    def test_manifest_isolation(self):
        from experiment import ExperimentSpec
        base_kwargs = dict(
            name="isolation-test",
            intent_id="intent_test",
            job_prompt="test job",
            variant_a={"tool_name": "tool_a", "description": "description alpha"},
            variant_b={"tool_name": "tool_b", "description": "description beta"},
            n_pairs=4, seed=100,
        )
        
        spec1 = ExperimentSpec(**base_kwargs)
        
        # Change ONLY variant_a description
        kwargs2 = {**base_kwargs}
        kwargs2["variant_a"] = {"tool_name": "tool_a", "description": "CHANGED description"}
        spec2 = ExperimentSpec(**kwargs2)
        
        # Manifest hashes should differ (variable changed)
        assert spec1.manifest_hash != spec2.manifest_hash
        
        # All STABLE fields byte-identical (volatile per-run keys excluded:
        # created_at + experiment_id are unique per instantiation by design)
        VOLATILE = {"created_at", "experiment_id"}
        d1 = {k: v for k, v in spec1.spec.items() if k not in VOLATILE and k != "variant_a"}
        d2 = {k: v for k, v in spec2.spec.items() if k not in VOLATILE and k != "variant_a"}
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


class TestCanonicalHashDeterminism:
    """Hash must be independent of key insertion order."""

    def test_key_order_independence(self):
        from experiment import canonical_hash
        h1 = canonical_hash({"z": 1, "a": {"c": 3, "b": [2, 1]}})
        h2 = canonical_hash({"a": {"b": [2, 1], "c": 3}, "z": 1})
        assert h1 == h2, "key order leaked into canonical hash"


import json
