"""Tests for DomainArenaWorld state transitions, terminal conditions, and scoring."""
import pytest
from unittest.mock import MagicMock
from pathlib import Path

from domainarena.world import (
    DAState, DomainArenaWorld, DomainCase,
    InferenceResult, SemanticEvaluation,
)
from cogym_kernel.kernel.contracts import ActionSpec, ActionResult


def _make_case(case_id="0", domain="test.com", intent="testing", match=True):
    return DomainCase(
        case_id=case_id, source="test",
        domain_name=domain, intent_description=intent,
        primary_job="test job", ground_truth_match=match,
    )


def _make_world():
    cases = [_make_case(), _make_case("1", "other.com", "other intent", False)]
    return DomainArenaWorld(cases, root=Path("/tmp"))


# World keys are "{source}:{case_id}", so "test:0" and "test:1"
TEST_ID = "test:0"
TEST_ID_1 = "test:1"


def _infer_result(model="test-model"):
    return ActionResult(
        action_id="inf-1", status="ok",
        payload={"raw": "test inference", "inference": "test inference", "model": model},
        wall_ms=100)


def _score_result(score=0.8, label="partial", scorer="scorer-v1"):
    return ActionResult(
        action_id="score-1", status="ok",
        payload={"semantic_score": score, "match_label": label,
                 "scorer_version": "v1", "scorer_model": scorer},
        wall_ms=50)


class TestStateTransitions:
    def test_happy_path_inference_then_score_then_commit(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42, model_family="llama")

        # INFERENCE
        inf_action = ActionSpec(kind="INFERENCE", executor_kind="llm_inference")
        state = world.apply(state, inf_action, _infer_result())
        assert state.inference_result is not None
        assert state.evaluation is None
        assert not state.committed

        # SCORE_SEMANTIC
        score_action = ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer")
        state = world.apply(state, score_action, _score_result())
        assert state.evaluation is not None
        assert state.evaluation.semantic_score == 0.8
        assert not state.committed

        # COMMIT_SCORE
        commit_action = ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic")
        state = world.apply(state, commit_action, ActionResult(action_id="c", status="ok", payload={}))
        assert state.committed

    def test_terminal_only_after_commit(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        assert not world.terminal(state)

        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        assert not world.terminal(state)

        state = world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                           _score_result())
        assert not world.terminal(state)

        state = world.apply(state, ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic"),
                           ActionResult(action_id="c", status="ok", payload={}))
        assert world.terminal(state)


class TestActionOrdering:
    def test_score_before_inference_raises(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        score_action = ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer")
        with pytest.raises(ValueError, match="requires INFERENCE first"):
            world.apply(state, score_action, _score_result())

    def test_commit_before_inference_raises(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        commit_action = ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic")
        with pytest.raises(ValueError, match="requires INFERENCE first"):
            world.apply(state, commit_action, ActionResult(action_id="c", status="ok", payload={}))

    def test_commit_before_score_raises(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        commit_action = ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic")
        with pytest.raises(ValueError, match="requires SCORE_SEMANTIC first"):
            world.apply(state, commit_action, ActionResult(action_id="c", status="ok", payload={}))

    def test_double_inference_raises(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        with pytest.raises(ValueError, match="INFERENCE already applied"):
            world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                       _infer_result())

    def test_double_score_raises(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        state = world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                           _score_result())
        with pytest.raises(ValueError, match="SCORE_SEMANTIC already applied"):
            world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                       _score_result())


class TestScoring:
    def test_score_perfect_match(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        state = world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                           _score_result(score=1.0, label="exact"))
        state = world.apply(state, ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic"),
                           ActionResult(action_id="c", status="ok", payload={}))
        mv = world.score(state)
        scores = {m.name: m.value for m in mv.metrics}
        assert scores["semantic_score"] == 1.0
        assert scores["parse_success"] == 1.0

    def test_score_zero_when_no_evaluation(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        mv = world.score(state)
        scores = {m.name: m.value for m in mv.metrics}
        assert scores["semantic_score"] == 0.0

    def test_score_includes_latency(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        state = world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                           _score_result())
        state = world.apply(state, ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic"),
                           ActionResult(action_id="c", status="ok", payload={}))
        mv = world.score(state)
        scores = {m.name: m.value for m in mv.metrics}
        assert scores["response_latency_ms"] == 100

    def test_response_hash_is_deterministic(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        import hashlib
        expected = hashlib.sha256(b"test inference").hexdigest()
        assert state.inference_result.response_hash == expected

    def test_scorer_model_recorded(self):
        world = _make_world()
        state = world.reset(instance_id=TEST_ID, seed=42)
        state = world.apply(state, ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
                           _infer_result())
        state = world.apply(state, ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
                           _score_result(scorer="gemma-4-26b"))
        assert state.evaluation.scorer_model == "gemma-4-26b"


class TestWorldSpec:
    def test_world_spec_metadata(self):
        world = _make_world()
        spec = world.world_spec
        assert spec.world_kind == "domainarena.comprehension"
        assert spec.version == "0.2"
        assert spec.metadata["total_cases"] == 2

    def test_instance_ids(self):
        world = _make_world()
        assert set(world.instance_ids) == {TEST_ID, TEST_ID_1}

    def test_get_case(self):
        world = _make_world()
        case = world.get_case(TEST_ID)
        assert case.domain_name == "test.com"
