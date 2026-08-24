"""AB/BA pairwise arena with reference-grade Bradley–Terry aggregation.

Peer-review CP-C fixes (2026-08-24):
  1. Exact AB/BA balancing: schedules PAIRED BLOCKS [(A,B),(B,A)] with
     block order randomized — first-position counts are guaranteed equal,
     not left to chance.
  2. Bradley–Terry via the standard MM fixed point (Hunter 2004), with
     disconnected-graph tolerance, permutation invariance, convergence.
"""
from __future__ import annotations
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field


def schedule_blocks(a: str, b: str, n_trials: int, seed: int = 42
                    ) -> list[tuple[str, str]]:
    """Exact AB/BA schedule: floor(n/2) blocks of both orders + at most one
    extra randomized order if n is odd. Block order shuffled by seed."""
    rng = random.Random(seed)
    half = n_trials // 2
    seq = [(a, b)] * half + [(b, a)] * half
    if n_trials % 2:
        seq.append((a, b) if rng.random() < 0.5 else (b, a))
    rng.shuffle(seq)
    return seq


@dataclass
class BalancedBlockRunner:
    a: str
    b: str
    n_trials: int
    seed: int = 42
    _seq: list = field(default_factory=list)
    _i: int = 0

    def __post_init__(self):
        self._seq = schedule_blocks(self.a, self.b, self.n_trials, self.seed)

    def next_order(self) -> tuple[str, str]:
        o = self._seq[self._i % len(self._seq)]
        self._i += 1
        return o


@dataclass
class PairTrial:
    domain_a: str
    domain_b: str
    winner: str | None
    first_shown: str


@dataclass
class Arena:
    domains: list[str]
    seed: int = 42
    trials: list[PairTrial] = field(default_factory=list)

    def schedule_pair(self, a: str, b: str, *, balanced: bool = True
                      ) -> tuple[str, str]:
        """Legacy single-order call; consecutive same-pair calls alternate
        orders deterministically (exact AB/BA across repeats)."""
        if not balanced:
            rng = self._rng(); pair = [a, b]; rng.shuffle(pair)
            return pair[0], pair[1]
        flips = sum(1 for t in self.trials
                    if {t.domain_a, t.domain_b} == {a, b})
        pair = [a, b] if flips % 2 == 0 else [b, a]
        return pair[0], pair[1]

    def record(self, shown_first: str, shown_second: str,
               winner: str | None):
        assert {shown_first, shown_second} <= set(self.domains)
        if winner is not None:
            assert winner in (shown_first, shown_second)
        self.trials.append(PairTrial(shown_first, shown_second, winner,
                                     first_shown=shown_first))

    def run_balanced_block(self, a: str, b: str, judge, n_trials: int) -> list:
        made = []
        for first, second in schedule_blocks(a, b, n_trials,
                                             self.seed + len(self.trials)):
            self.record(first, second, judge(first, second))
            made.append(self.trials[-1])
        return made

    def decided(self) -> list[PairTrial]:
        return [t for t in self.trials if t.winner is not None]

    def bradley_terry(self, iters: int = 500, tol: float = 1e-10
                      ) -> dict[str, float]:
        """Standard BT MM fixed point. Ties excluded (winner=None filtered).
        Disconnected components identified only within; normalized globally."""
        W: dict[str, float] = defaultdict(float)
        N: dict[tuple[str, str], float] = defaultdict(float)
        players = set()
        for t in self.decided():
            a, b = t.domain_a, t.domain_b
            players.update((a, b))
            N[(min(a, b), max(a, b))] += 1
            if t.winner == a: W[a] += 1
            elif t.winner == b: W[b] += 1
        if len(players) < 2:
            return {}
        eps = 1e-9
        strength = {p: 1.0 for p in players}
        for _ in range(iters):
            new = dict(strength)
            delta = 0.0
            for i in players:
                denom = sum(
                    N[(min(i, j), max(i, j))] / (strength[i] + strength[j])
                    for j in players if j != i
                    and N[(min(i, j), max(i, j))] > 0)
                if denom > 0:
                    new[i] = max(W[i] / denom, eps)
                    delta = max(delta, abs(new[i] - strength[i]))
            ssum = sum(new.values())
            strength = {p: v / ssum for p, v in new.items()}
            if delta < tol:
                break
        return strength

    def bt_connected(self) -> bool:
        d = self.decided()
        if not d:
            return False
        adj: dict[str, set] = defaultdict(set)
        for t in d:
            adj[t.domain_a].add(t.domain_b)
            adj[t.domain_b].add(t.domain_a)
        seen, stack = set(), [next(iter(adj))]
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); stack.extend(adj[x] - seen)
        return len(seen) == len(adj)

    def position_bias(self) -> float:
        d = self.decided()
        if not d:
            return float("nan")
        return sum(1 for t in d if t.winner == t.first_shown) / len(d)

    def wilson_ci(self, wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
        if n == 0:
            return (float("nan"), float("nan"))
        p = wins / n
        denom = 1 + z**2 / n
        center = (p + z**2 / (2*n)) / denom
        margin = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
        return (max(0.0, center - margin), min(1.0, center + margin))
