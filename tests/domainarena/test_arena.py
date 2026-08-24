import math

import pytest

from domainarena.arena.pairwise import Arena
from domainarena.arena.semantic_inversion import (
    aggregate,
    run_semantic_inversion,
    score_inference,
)
from domainarena.models import Candidate, InventorySnapshot


def _cand(dom):
    sld, _, tld = dom.partition(".")
    return Candidate(candidate_id=dom, domain_name=dom, generator="test",
                     inventory=InventorySnapshot(
                         domain_name=dom, sld=sld, tld=tld, purchasable=True,
                         checked_at="2026-08-24T00:00:00Z"))


class TestSemanticInversion:
    def test_score_inference_overlap(self):
        assert score_inference("repair malformed JSON", "repair broken JSON", ["json"]) > 0.5
        assert score_inference("repair malformed JSON", "sell shoes online", []) == 0.0

    def test_offline_fallback_runs(self):
        res = run_semantic_inversion([_cand("jsonrepair.dev")], "repair malformed JSON")
        assert len(res) == 1
        assert res[0].parse_ok
        assert res[0].score >= 0

    def test_aggregate_means(self):
        from domainarena.arena.semantic_inversion import InversionResult
        rs = [
            InversionResult("a", "a.dev", "f1", "x", None, score=1.0),
            InversionResult("a", "a.dev", "f2", "", None, score=0.0, parse_ok=False),
        ]
        assert aggregate(rs)["a.dev"] == 0.5


class TestPairwiseArena:
    def test_abba_position_control_recorded(self):
        arena = Arena(["a.dev", "b.dev"], seed=7)
        first, second = arena.schedule_pair("a.dev", "b.dev")
        assert {first, second} == {"a.dev", "b.dev"}
        arena.record(first, second, winner=first)
        assert arena.trials[0].first_shown in ("a.dev", "b.dev")

    def test_abstention_not_counted(self):
        arena = Arena(["a.dev", "b.dev"])
        arena.record("a.dev", "b.dev", None)
        assert arena.decided() == []

    def test_invalid_winner_rejected(self):
        arena = Arena(["a.dev", "b.dev"])
        with pytest.raises(AssertionError):
            arena.record("a.dev", "b.dev", "c.dev")

    def test_bt_prefers_dominant_candidate(self):
        arena = Arena(["strong.dev", "weak.dev"])
        for i in range(20):
            order = arena.schedule_pair("strong.dev", "weak.dev")
            winner = "strong.dev"
            arena.record(order[0], order[1], winner)
        strengths = arena.bradley_terry()
        assert strengths["strong.dev"] > strengths["weak.dev"]

    def test_wilson_ci(self):
        lo, hi = Arena(["a", "b"]).wilson_ci(9, 10)
        assert lo > 0.5 and hi <= 1.0
        lo, hi = Arena(["a", "b"]).wilson_ci(5, 10)
        assert lo <= 0.5 <= hi

    def test_position_bias_healthy_range(self):
        arena = Arena(["a.dev", "b.dev"], seed=3)
        rng_order = [(arena.schedule_pair("a.dev", "b.dev"), "a.dev" if i % 2 else "b.dev")
                     for i in range(40)]
        for (first, second), w in rng_order:
            arena.record(first, second, w)
        bias = arena.position_bias()
        assert not math.isnan(bias) and 0.2 < bias < 0.8
