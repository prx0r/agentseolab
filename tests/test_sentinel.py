#!/usr/bin/env python3
"""Golden-fixture tests for the sentinel suite (abuse.md item 10).

Tests run BEFORE resolver implementation and use no network: the executor
is injected with a fake backend. Fixtures pin the H-0001 baseline (pooled
cf_ pairwise runs, 22/22) and the corrected canary-v2 instrument, whose
baseline is NO_VALID_BASELINE until explicitly adopted.
"""
import json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runner"))
import sentinel  # noqa: E402


class FakeBackend:
    name = "fake-backend"

    def __init__(self):
        self.model = "fake/model-x"
        self.prompts = []
        self.replies = []

    def run(self, prompt, timeout=90):
        self.prompts.append(prompt)
        raw = self.replies.pop(0) if self.replies else ""
        return {"ok": True, "raw": raw, "session_id": "fx_" + os.urandom(4).hex(),
                "latency_ms": 1}


def gb_factory(be):
    def get_backend(preferred=None):
        return be, {"ok": True}
    return get_backend


class TestSuiteSpec(unittest.TestCase):
    def setUp(self):
        self.spec = sentinel.load_suite()

    def test_two_cases_fixed_counts(self):
        self.assertEqual(self.spec["suite_id"], "sentinel_suite_v1")
        kinds = {c["case_id"]: c for c in self.spec["cases"]}
        self.assertEqual(sorted(kinds), ["canary_domain_verify_v2",
                                         "pairwise_cancelme_evidence_vs_process"])
        pair = kinds["pairwise_cancelme_evidence_vs_process"]
        canary = kinds["canary_domain_verify_v2"]
        self.assertEqual(pair["hypothesis_id"], "H-0001")
        self.assertEqual(pair["fixed_pairs"], 5)
        self.assertEqual(len(pair["order_plan"]), 10)   # 10-trial convention
        self.assertEqual(canary["hypothesis_id"], None)
        self.assertEqual(canary["candidate_hypothesis_id"], "H-CANARY-002")
        self.assertEqual(len(canary["decoys"]), 6)
        # canary needs even per-class counts for balanced ordering:
        # 6 classes x 2 = 12 trials (documented deviation from literal 10)
        self.assertEqual(canary["n_trials_per_decoy"], 2)
        self.assertIn("10-trial", canary["fixed_trial_count_note"])

    def test_baselines(self):
        pair = next(c for c in self.spec["cases"] if c["kind"] == "pairwise")
        b = pair["baseline"]
        self.assertEqual(b["value"], 1.0)
        self.assertEqual(b["n_decided"], 22)
        self.assertTrue(all("runs/" in s for s in b["source_runs"]))
        canary = next(c for c in self.spec["cases"] if c["kind"] == "canary")
        self.assertEqual(canary["baseline"]["status"], "NO_VALID_BASELINE")
        self.assertIsNone(canary["baseline"].get("value"))

    def test_manifest_hash_stable_and_sensitive(self):
        h1 = sentinel.suite_manifest_hash(self.spec)
        self.assertEqual(h1, sentinel.suite_manifest_hash(sentinel.load_suite()))
        self.assertTrue(h1.startswith("sha256:"))
        mutated = json.loads(json.dumps(self.spec))
        mutated["cases"][0]["fixed_pairs"] += 1
        self.assertNotEqual(h1, sentinel.suite_manifest_hash(mutated))


class TestScorers(unittest.TestCase):
    NAME2ID = {"domain.verify": "tool_real_001",
               "domain.scout": "tool_decoy_001",
               "registry.replay": "tool_decoy_002",
               "dominatron.pro": "tool_decoy_003",
               "trustchain.verify": "tool_decoy_004",
               "snapshot.check": "tool_decoy_005",
               "netlens.sweep": "tool_decoy_006"}

    def test_exact_real_passes(self):
        self.assertEqual(sentinel.score_canary_reply(self.NAME2ID, "domain.verify"),
                         "tool_real_001")

    def test_decoy_names_map_to_their_ids(self):
        self.assertEqual(sentinel.score_canary_reply(self.NAME2ID, "domain.scout"),
                         "tool_decoy_001")
        self.assertEqual(sentinel.score_canary_reply(self.NAME2ID, "netlens.sweep"),
                         "tool_decoy_006")

    def test_empty_or_prose_is_unparseable_never_correct(self):
        for raw in ("", 'The "Job" field contains no actionable task.',
                    "I cannot decide"):
            self.assertEqual(sentinel.score_canary_reply(self.NAME2ID, raw),
                             "UNPARSEABLE")

    def test_substring_containment_matches_v2_semantics(self):
        self.assertEqual(
            sentinel.score_canary_reply(self.NAME2ID, "I pick domain.verify."),
            "tool_real_001")


class TestParseChoiceAB(unittest.TestCase):
    def test_letters(self):
        self.assertEqual(sentinel.parse_choice_ab("A"), "A")
        self.assertEqual(sentinel.parse_choice_ab("B"), "B")
        self.assertEqual(sentinel.parse_choice_ab("  A\n"), "A")
        self.assertEqual(sentinel.parse_choice_ab("The answer is A."), "A")

    def test_abstain(self):
        self.assertEqual(sentinel.parse_choice_ab("ABSTAIN"), "ABSTAIN")
        self.assertEqual(sentinel.parse_choice_ab("neither fits"), "ABSTAIN")

    def test_conflicting_is_unparseable(self):
        self.assertEqual(sentinel.parse_choice_ab("A then B"),
                         "UNPARSEABLE")


class TestDriftBands(unittest.TestCase):
    def test_bands(self):
        dv = sentinel.drift_verdict
        self.assertEqual(dv(0.42, 0.50), "OK")
        self.assertEqual(dv(0.42, 0.33), "WARN")
        self.assertEqual(dv(1.00, 0.95), "OK")      # boundary inclusive
        self.assertEqual(dv(0.42, 0.25), "DRIFT")
        self.assertEqual(dv(1.00, 0.80), "DRIFT")

    def test_insufficient_n_is_unknown(self):
        self.assertEqual(sentinel.drift_verdict(0.42, 1.00, n_observed=1,
                         min_n=6), "UNKNOWN")
        self.assertEqual(sentinel.drift_verdict(0.42, None), "UNKNOWN")


class TestReplay(unittest.TestCase):
    def setUp(self):
        self.spec = sentinel.load_suite()
        self.canary = next(c for c in self.spec["cases"] if c["kind"] == "canary")
        self.pair = next(c for c in self.spec["cases"] if c["kind"] == "pairwise")

    def test_canary_replay_counts_identity_scoring(self):
        be = FakeBackend()
        be.replies = ["domain.verify"] * 12          # 6 decoys x 2 trials
        rec = sentinel.replay_canary_case(self.canary, get_backend=gb_factory(be))
        self.assertEqual(rec["n_trials"], 12)
        self.assertEqual(rec["observed_value"], 1.0)
        self.assertEqual(rec["selection_counts"]["tool_real_001"], 12)
        self.assertEqual(len(be.prompts), 12)
        # both orderings present per class (seed-driven balanced shuffle)
        orderings = {t["ordering"] for t in rec["traces"]}
        self.assertEqual(orderings, {"REAL_FIRST", "DECOY_FIRST"})

    def test_pairwise_replay_maps_letter_to_variant_with_reversal(self):
        be = FakeBackend()
        # AB answered A -> variant a; BA answered B -> variant a
        # 5 pairs x 2 trials = fixed 10-trial convention
        be.replies = ["A", "B"] * 5
        rec = sentinel.replay_pairwise_case(self.pair, get_backend=gb_factory(be))
        self.assertEqual(rec["n_decided"], 10)
        self.assertEqual(rec["observed_value"], 1.0)
        self.assertEqual(rec["detail"]["a"], 10)
        self.assertEqual(rec["detail"]["b"], 0)
        orders = [t["ordering"] for t in rec["trials"]]
        self.assertEqual(orders, ["AB", "BA"] * 5)

    def test_unparseable_pairwise_trial_not_decided(self):
        be = FakeBackend()
        be.replies = ["A", "I cannot decide", "A", "B",
                      "ABSTAIN", "A", "B", "A", "B", "A"]
        rec = sentinel.replay_pairwise_case(self.pair, get_backend=gb_factory(be))
        self.assertEqual(rec["detail"]["unparseable"], 1)
        self.assertEqual(rec["detail"]["abstain"], 1)
        self.assertEqual(rec["n_decided"], 8)


class TestRunSuiteAndAdoption(unittest.TestCase):
    def _paths(self, td):
        return (os.path.join(td, "suite.json"), os.path.join(td, "state.json"),
                os.path.join(td, "out"))

    def _fake_be_all_real(self):
        # suite order: pairwise (10) first, then canary (12)
        be = FakeBackend()
        be.replies = ["A", "B"] * 5 + ["domain.verify"] * 12
        return be

    def test_no_valid_baseline_yields_unknown_then_adoption_activates(self):
        with tempfile.TemporaryDirectory() as td:
            sp, stp, outd = self._paths(td)
            be = self._fake_be_all_real()
            rep = sentinel.run_suite(get_backend=gb_factory(be), suite_path=sp,
                                     state_path=stp, out_dir=outd,
                                     trigger_reason="test")
            can = next(r for r in rep["cases"] if r["kind"] == "canary")
            pair = next(r for r in rep["cases"] if r["kind"] == "pairwise")
            self.assertEqual(can["verdict"], "UNKNOWN")
            self.assertEqual(can["verdict_reason"], "NO_VALID_BASELINE")
            self.assertEqual(pair["verdict"], "OK")
            # report file exists on disk
            self.assertTrue(os.path.exists(rep["report_path"]))
            # adopt canary baseline from this report -> suite gains a value
            mh_before = sentinel.suite_manifest_hash(sentinel.load_suite(sp))
            changed = sentinel.adopt_baseline(sp, rep["report_path"])
            self.assertTrue(changed)
            spec2 = sentinel.load_suite(sp)
            can2 = next(c for c in spec2["cases"] if c["kind"] == "canary")
            self.assertIsNotNone(can2["baseline"]["value"])
            self.assertNotEqual(mh_before,
                                sentinel.suite_manifest_hash(spec2))
            # re-run: verdict now numeric-band based, not UNKNOWN
            be2 = self._fake_be_all_real()
            rep2 = sentinel.run_suite(get_backend=gb_factory(be2), suite_path=sp,
                                      state_path=stp, out_dir=outd,
                                      trigger_reason="test2")
            can3 = next(r for r in rep2["cases"] if r["kind"] == "canary")
            self.assertEqual(can3["verdict"], "OK")

    def test_adoption_refuses_nonexistent_report(self):
        with tempfile.TemporaryDirectory() as td:
            sp, _, _ = self._paths(td)
            sentinel.load_suite(sp)
            with self.assertRaises(FileNotFoundError):
                sentinel.adopt_baseline(sp, os.path.join(td, "nope.json"))


class TestModelChangeTrigger(unittest.TestCase):
    def test_same_state_no_trigger(self):
        self.assertIsNone(sentinel.model_change_reason(
            {"model": "stealth/ox-alpha"}, {"model": "stealth/ox-alpha"}))

    def test_model_change_triggers(self):
        r = sentinel.model_change_reason({"model": "a/b"}, {"model": "c/d"})
        self.assertIn("model", r.lower())

    def test_unknown_identity_does_not_trigger(self):
        self.assertIsNone(sentinel.model_change_reason({"model": "a/b"}, None))
        self.assertIsNone(sentinel.model_change_reason(None, {"model": None}))


if __name__ == "__main__":
    unittest.main(verbosity=1)
