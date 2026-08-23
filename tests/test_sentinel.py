#!/usr/bin/env python3
"""Golden-fixture tests for the sentinel suite (abuse.md item 10).

Tests run BEFORE resolver implementation and use no network: the executor
is injected with a fake backend. Fixtures pin the exact baseline numbers of
H-CANARY-001 (canary_20260823-021800.json) and H-0001 (pooled cf_ runs).
"""
import json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runner"))
import sentinel  # noqa: E402

RUNS = os.path.join(os.path.dirname(__file__), "..", "runs")


class FakeBackend:
    """Scripted backend: returns canned raws, records prompts."""
    name = "fake-backend"

    def __init__(self, script=None):
        self.script = list(script or [])
        self.model = "fake/model-x"
        self.prompts = []

    def run(self, prompt, timeout=90):
        self.prompts.append(prompt)
        raw = self.script.pop(0) if self.script else "domain.verify"
        return {"ok": True, "raw": raw, "session_id": "fx_" + os.urandom(4).hex(),
                "latency_ms": 1}


def fake_get_backend_factory(backend):
    def get_backend(preferred=None):
        return backend, {"ok": True}
    return get_backend


class TestSuiteSpec(unittest.TestCase):
    def test_suite_spec_loads_and_is_frozen(self):
        spec = sentinel.load_suite()
        self.assertEqual(spec["suite_id"], "sentinel_suite_v1")
        self.assertEqual(spec["manifest_hash_algorithm"], "sha256-canonical-json")
        # exactly two hypotheses replayed, fixed trial counts
        hids = sorted(c["hypothesis_id"] for c in spec["cases"])
        self.assertEqual(hids, ["H-0001", "H-CANARY-001"])
        canary = next(c for c in spec["cases"] if c["hypothesis_id"] == "H-CANARY-001")
        pair = next(c for c in spec["cases"] if c["hypothesis_id"] == "H-0001")
        self.assertEqual(canary["fixed_trials_per_class"], 2)
        self.assertEqual(pair["fixed_pairs"], 3)
        self.assertEqual(len(canary["decoy_classes"]), 6)
        # every case pins its baseline
        for c in spec["cases"]:
            self.assertIn("baseline", c)
            b = c["baseline"]
            self.assertTrue(b["source_runs"], "baseline must cite source runs")
            self.assertIsInstance(b["value"], (int, float))

    def test_manifest_hash_stable_and_sensitive(self):
        spec = sentinel.load_suite()
        h1 = sentinel.suite_manifest_hash(spec)
        h2 = sentinel.suite_manifest_hash(sentinel.load_suite())
        self.assertEqual(h1, h2, "same file -> same hash")
        self.assertTrue(h1.startswith("sha256:"))
        mutated = json.loads(json.dumps(spec))
        mutated["cases"][0]["baseline"]["value"] += 0.01
        self.assertNotEqual(h1, sentinel.suite_manifest_hash(mutated),
                            "hash must change when any frozen field changes")


class TestCanaryScoring(unittest.TestCase):
    BASE = sentinel.load_suite() if os.path.exists(
        os.path.join(os.path.dirname(__file__), "..", "runner",
                     "sentinel_suite_v1.spec.json")) else None

    def test_score_exact_real_name_passes(self):
        self.assertTrue(sentinel.picked_real("domain.verify", "domain.verify"))
        self.assertTrue(sentinel.picked_real("domain.verify", "  domain.verify\n"))

    def test_score_decoy_names_fail(self):
        for decoy in ("domain.search", "domain.pro", "domain.verify.cached",
                      "domain.verify.secure", "internet.scan"):
            self.assertFalse(sentinel.picked_real(decoy, "domain.verify"),
                             f"answer naming decoy {decoy} must not score")
            self.assertFalse(sentinel.picked_real("domain.verify", decoy),
                             f"raw reply {decoy} must not score")

    def test_score_empty_or_prose_fails(self):
        self.assertFalse(sentinel.picked_real("domain.verify", ""))
        self.assertFalse(sentinel.picked_real("domain.verify",
                        'The "Job" field contains no actionable task.'))


class TestDriftBands(unittest.TestCase):
    def test_within_band_green(self):
        self.assertEqual(sentinel.drift_verdict(baseline=0.42, observed=0.50,
                         warn_abs=0.08, drift_abs=0.15), "OK")

    def test_warn_band(self):
        self.assertEqual(sentinel.drift_verdict(baseline=0.42, observed=0.33,
                         warn_abs=0.08, drift_abs=0.15), "WARN")
        self.assertEqual(sentinel.drift_verdict(baseline=1.00, observed=0.95,
                         warn_abs=0.08, drift_abs=0.15), "OK")  # boundary inclusive

    def test_drift_band(self):
        self.assertEqual(sentinel.drift_verdict(baseline=0.42, observed=0.25,
                         warn_abs=0.08, drift_abs=0.15), "DRIFT")
        self.assertEqual(sentinel.drift_verdict(baseline=1.00, observed=0.80,
                         warn_abs=0.08, drift_abs=0.15), "DRIFT")

    def test_insufficient_n_is_unknown_never_guessed(self):
        v = sentinel.drift_verdict(baseline=0.42, observed=1.00, n_observed=1,
                                   min_n=6, warn_abs=0.08, drift_abs=0.15)
        self.assertEqual(v, "UNKNOWN")


class TestReplay(unittest.TestCase):
    def setUp(self):
        self.spec = sentinel.load_suite()
        self.canary_case = next(c for c in self.spec["cases"]
                                if c["hypothesis_id"] == "H-CANARY-001")
        self.pair_case = next(c for c in self.spec["cases"]
                              if c["hypothesis_id"] == "H-0001")

    def test_canary_replay_counts(self):
        be = FakeBackend(script=["domain.verify"] * 12)
        rec = sentinel.replay_canary_case(self.canary_case,
                                          get_backend=fake_get_backend_factory(be))
        self.assertEqual(rec["n_trials"], 12)
        self.assertEqual(rec["observed_value"], 1.0)
        self.assertEqual(len(be.prompts), 12)

    def test_pairwise_replay_maps_letter_to_variant_with_reversal(self):
        # AB trials answered A -> variant a; BA trials answered B -> variant a.
        plan = []
        for i in range(3):
            plan += ["AB", "BA"]
        answers = {"AB": "A", "BA": "B"}          # always picks content-variant 'a'
        be = FakeBackend()
        orig_run = be.run
        counter = {"i": 0}

        def scripted(prompt, timeout=90):
            order = plan[counter["i"]]
            counter["i"] += 1
            be.prompts.append(prompt)
            return {"ok": True, "raw": answers[order],
                    "session_id": f"fx_{counter['i']}", "latency_ms": 1}
        be.run = scripted
        rec = sentinel.replay_pairwise_case(self.pair_case,
                                            get_backend=fake_get_backend_factory(be))
        self.assertEqual(rec["n_decided"], 6)
        self.assertEqual(rec["observed_value"], 1.0)
        self.assertEqual(rec["detail"]["a"], 6)
        self.assertEqual(rec["detail"]["b"], 0)

    def test_unparseable_trial_counts_as_not_selected(self):
        plan = ["AB", "BA"] * 3
        counter = {"i": 0}

        class BE(FakeBackend):
            def run(self, prompt, timeout=90):
                order = plan[counter["i"]]
                counter["i"] += 1
                self.prompts.append(prompt)
                raw = "I cannot decide" if counter["i"] == 2 else "A"
                return {"ok": True, "raw": raw,
                        "session_id": f"fx_{counter['i']}", "latency_ms": 1}
        be = BE()
        rec = sentinel.replay_pairwise_case(self.pair_case,
                                            get_backend=fake_get_backend_factory(be))
        self.assertEqual(rec["detail"]["abstain"] + rec["detail"]["unparseable"], 1)
        self.assertEqual(rec["detail"]["a"], 5)


class TestModelChangeTrigger(unittest.TestCase):
    def test_same_state_no_trigger(self):
        last = {"model": "stealth/ox-alpha"}
        cur = {"model": "stealth/ox-alpha"}
        self.assertIsNone(sentinel.model_change_reason(last, cur))

    def test_model_change_triggers(self):
        reason = sentinel.model_change_reason({"model": "a/b"},
                                              {"model": "c/d"})
        self.assertIsNotNone(reason)
        self.assertIn("model", reason.lower())

    def test_missing_current_state_unknown_not_triggered(self):
        self.assertIsNone(sentinel.model_change_reason({"model": "a/b"}, None))


class TestCheckAndRunDry(unittest.TestCase):
    def test_state_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "state.json")
            sentinel.save_last_state(p, {"model": "m", "suite_manifest_hash": "sha256:x"})
            loaded = sentinel.load_last_state(p)
            self.assertEqual(loaded["model"], "m")


if __name__ == "__main__":
    unittest.main(verbosity=2)
