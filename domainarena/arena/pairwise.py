"""AB/BA pairwise arena with Bradley–Terry aggregation.

Position bias controls: every pair runs in both orders; order is randomized
per seed; "neither" is a valid abstention and never counted as a selection.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field


@dataclass
class PairTrial:
    domain_a: str
    domain_b: str
    winner: str | None  # domain name or None for abstention
    first_shown: str    # position control record


@dataclass
class Arena:
    domains: list[str]
    seed: int = 42
    trials: list[PairTrial] = field(default_factory=list)

    def _rng(self) -> random.Random:
        return random.Random(self.seed + len(self.trials))

    def schedule_pair(self, a: str, b: str) -> tuple[str, str]:
        """Randomized AB/BA: returns presentation order."""
        rng = self._rng()
        pair = [a, b]
        rng.shuffle(pair)
        return pair[0], pair[1]

    def record(self, shown_first: str, shown_second: str, winner: str | None):
        assert {shown_first, shown_second} <= set(self.domains)
        if winner is not None:
            assert winner in (shown_first, shown_second)
        self.trials.append(PairTrial(shown_first, shown_second, winner,
                                     first_shown=shown_first))

    # ---- statistics ----

    def decided(self) -> list[PairTrial]:
        return [t for t in self.trials if t.winner is not None]

    def bradley_terry(self, iters: int = 200, lr: float = 0.5) -> dict[str, float]:
        """MM-style iterative BT fit. Returns normalized strengths (sum=1)."""
        wins: dict[tuple[str, str], int] = {}
        for t in self.decided():
            loser = t.domain_b if t.winner == t.domain_a else t.domain_a
            key = (t.winner, loser)
            wins[key] = wins.get(key, 0) + 1
        players = sorted({p for k in wins for p in k})
        if len(players) < 2:
            return {}
        strength = {p: 1.0 for p in players}
        for _ in range(iters):
            new = dict(strength)
            for i in players:
                wi = sum(c for (w, l), c in wins.items() if w == i)
                li = sum(c for (w, l), c in wins.items() if l == i)
                denom = sum(
                    strength[i] + strength[j]
                    for j in players if j != i
                    for _c in [wins.get((i, j), 0) + wins.get((j, i), 0)]
                    if _c > 0
                ) or None
                if denom:
                    new[i] = max(1e-6, wi / denom * strength[i])
                elif li == 0:
                    new[i] = strength[i]  # no games involving i as recorded
            s = sum(new.values())
            strength = {p: v / s for p, v in new.items()}
        return strength

    def position_bias(self) -> float:
        """Fraction of decided trials won by the slot shown first (≈0.5 is healthy)."""
        d = self.decided()
        if not d:
            return float("nan")
        first_wins = sum(1 for t in d if t.winner == t.first_shown)
        return first_wins / len(d)

    def wilson_ci(self, wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
        if n == 0:
            return (float("nan"), float("nan"))
        p = wins / n
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
        return (max(0.0, center - margin), min(1.0, center + margin))
