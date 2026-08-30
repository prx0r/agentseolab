"""Tests for the pairwise selection experiment runner."""
import pytest
from experiments.pairwise_selection import extract_choice, wilson_lower, pairwise_prompt


def test_extract_choice_prefers_a():
    assert extract_choice("I choose jsonrepair.dev", "jsonrepair.dev", "fixjson.com") == "jsonrepair.dev"


def test_extract_choice_prefers_b():
    assert extract_choice("fixjson.com is better", "jsonrepair.dev", "fixjson.com") == "fixjson.com"


def test_extract_choice_ambiguous():
    assert extract_choice("both are good jsonrepair.dev fixjson.com", "jsonrepair.dev", "fixjson.com") is None


def test_extract_choice_unparseable():
    assert extract_choice("I'm not sure", "jsonrepair.dev", "fixjson.com") is None


def test_wilson_lower_all_wins():
    ci = wilson_lower(20, 20)
    assert ci > 0.5


def test_wilson_lower_half_wins():
    ci = wilson_lower(10, 20)
    assert 0.25 < ci < 0.6


def test_wilson_lower_zero():
    ci = wilson_lower(0, 20)
    assert ci < 0.01  # close to zero, may have tiny floating point error


def test_wilson_lower_zero_n():
    assert wilson_lower(0, 0) == 0.0


def test_pairwise_prompt_ab_order():
    prompt = pairwise_prompt("a.dev", "b.com", "test intent", "AB")
    assert "a.dev" in prompt
    assert "b.com" in prompt
    # In AB order, a.dev should appear first
    assert prompt.index("a.dev") < prompt.index("b.com")


def test_pairwise_prompt_ba_order():
    prompt = pairwise_prompt("a.dev", "b.com", "test intent", "BA")
    # In BA order, b.com should appear first
    assert prompt.index("b.com") < prompt.index("a.dev")
