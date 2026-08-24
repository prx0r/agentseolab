#!/usr/bin/env python3
"""test_arena_pairwise.py — CP-C validation suite (peer review §4).

Covers: exact AB/BA balancing · BT closed-form 2-player · synthetic 3-player
strength recovery · disconnected graph handling · permutation invariance ·
position-bias statistic. Run: python3 -m pytest tests/test_arena_pairwise.py -q
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domainarena.arena.pairwise import (
    Arena, schedule_blocks, BalancedBlockRunner,
)

def test_schedule_exact_balance_even():
    for n in (2, 10, 51*2):
        seq = schedule_blocks("A", "B", n, seed=7)
        first_a = sum(1 for x in seq if x[0] == "A")
        assert len(seq) == n
        assert abs(first_a - (n - first_a)) <= 1

def test_schedule_odd_allows_single_excess():
    seq = schedule_blocks("A", "B", 7, seed=3)
    fa = sum(1 for x in seq if x[0] == "A")
    fb = sum(1 for x in seq if x[0] == "B")
    assert abs(fa - fb) == 1 and len(seq) == 7

def test_runner_alternates_without_repeat_skew():
    r = BalancedBlockRunner("A", "B", 8, seed=11)
    orders = [r.next_order() for _ in range(8)]
    a_first = sum(1 for o in orders if o[0] == "A")
    assert a_first == 4

def _mk_arena(trials):
    a = Arena(domains=sorted({d for t in trials for d in (t[0], t[1])}))
    for f, s, w in trials:
        a.record(f, s, w)
    return a

def test_bt_two_player_closed_form():
    # A beat B 3/4 → strengths proportional to wins (closed form for 2 players)
    trials = [("A","B","A")]*3 + [("A","B","B")]
    arena = _mk_arena(trials)
    st = arena.bradley_terry()
    assert abs(st["A"]/st["B"] - 3.0) < 1e-6

def test_bt_three_player_synthetic_recovery():
    """Generate outcomes from known strengths [3,2,1] via BT probabilities;
    recovered ranking must match and top/bottom ratio within tolerance."""
    import math
    true = {"A": 3.0, "B": 2.0, "C": 1.0}
    rng = random.Random(5)
    trials = []
    for _ in range(400):
        (i, j) = rng.sample(sorted(true), 2)
        p_i = true[i]/(true[i]+true[j])
        win, lose = (i, j) if rng.random() < p_i else (j, i)
        trials.append((win, lose, win))
    arena = _mk_arena(trials)
    st = arena.bradley_terry()
    order = sorted(st, key=st.get, reverse=True)
    assert order[0] == "A" and order[-1] == "C"
    assert st["A"]/st["C"] > 2.0   # strong separation preserved directionally

def test_bt_disconnected_graph_does_not_crash():
    trials = [("A","B","A")]*5 + [("C","D","D")]*5
    arena = _mk_arena(trials)
    st = arena.bradley_terry()
    assert set(st) == {"A","B","C","D"}
    assert arena.bt_connected() is False

def test_bt_permutation_invariance():
    trials = ([("A","B","A")]*7 + [("A","B","B")]*3 +
              [("B","C","B")]*6 + [("C","B","C")]*4)
    base = _mk_arena(list(trials)).bradley_terry()
    shuffled = list(trials); rng = random.Random(9); rng.shuffle(shuffled)
    alt = _mk_arena(list(shuffled)).bradley_terry()
    for p in ("A","B","C"):
        assert abs(base[p]-alt[p]) < 1e-9

def test_abstentions_excluded_from_ranking_but_counted_positionally():
    from domainarena.arena.pairwise import PairTrial
    a = Arena(domains=["A","B"])
    a.record("A","B","A"); a.record("A","B",None)
    assert len(a.trials) == 2 and len(a.decided()) == 1
    pb = a.position_bias()
    assert pb == 1.0

def test_arena_balanced_block_integration():
    a = Arena(domains=["X","Y"], seed=99)
    def judge(f, s):  # Y always wins regardless of slot
        return "Y"
    made = a.run_balanced_block("X","Y", judge, 20)
    fx = sum(1 for t in made if t.first_shown=="X")
    fy = sum(1 for t in made if t.first_shown=="Y")
    assert fx == fy == 10          # exact balance guaranteed
    assert sum(1 for t in made if t.winner=="Y") == len(made)

import random
