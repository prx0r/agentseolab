"""TLD causal experiment, productized on real candidate SLDs.

Canonical fixes from PEER_REVIEW + H-TLD01 corrected analysis:
- identical titles/descriptions/tools; ONLY the TLD differs;
- best-result TLD counterbalanced across trials;
- primary endpoints are POSITION-STRATIFIED: P(pick|pos0) and P(pick|off-pos0);
- raw marginal TLD share is reported as a known-confounded secondary stat.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

TLDS = ["com", "org", "dev", "io", "xyz"]


@dataclass
class TLDTrial:
    sld: str
    slot_assignment: dict[str, int]        # tld -> position 0..4 (seeded shuffle)
    best_tld: str                          # where the genuinely-best result sits
    picked: str | None = None              # TLD the agent picked
    position: int | None = None            # position of the pick


@dataclass
class TLDTrials:
    trials: list[TLDTrial] = field(default_factory=list)
    seed: int = 42

    def new_trial(self, sld: str, best_tld: str) -> TLDTrial:
        rng = random.Random(self.seed * 1000 + len(self.trials))
        order = TLDS[:]
        rng.shuffle(order)
        trial = TLDTrial(
            sld=sld,
            slot_assignment={t: i for i, t in enumerate(order)},
            best_tld=best_tld,
        )
        self.trials.append(trial)
        return trial

    def record_pick_by_position(self, trial: TLDTrial, position: int):
        if not 0 <= position <= 4:
            return  # out-of-range is an error, never a selection
        trial.position = position
        trial.picked = next(t for t, p in trial.slot_assignment.items() if p == position)

    # ---- corrected estimands ----

    def stratified(self) -> dict[str, dict[str, tuple[int, int]]]:
        """Per-TLD P(pick|pos0) and P(pick|off-pos0), plus best-result hit rate."""
        stats: dict[str, dict[str, list[int]]] = {
            t: {"pos0": [0, 0], "off": [0, 0], "best": [0, 0]} for t in TLDS}
        for tr in self.trials:
            if tr.picked is None:
                continue
            for t in TLDS:
                pos = tr.slot_assignment[t]
                if pos == 0:
                    stats[t]["pos0"][1] += 1
                    stats[t]["pos0"][0] += int(tr.picked == t)
                else:
                    stats[t]["off"][1] += 1
                    stats[t]["off"][0] += int(tr.picked == t)
                if tr.best_tld == t:
                    stats[t]["best"][1] += 1
                    stats[t]["best"][0] += int(tr.picked == t)
        return {t: {k: tuple(v) for k, v in d.items()} for t, d in stats.items()}

    def position_primacy(self) -> float:
        decided = [t for t in self.trials if t.position is not None]
        if not decided:
            return float("nan")
        return sum(1 for t in decided if t.position == 0) / len(decided)

    def marginal_share(self) -> dict[str, float]:
        """KNOWN-CONFOUNDED by slot assignment — secondary only."""
        decided = [t for t in self.trials if t.picked]
        n = len(decided) or 1
        shares = {t: 0 for t in TLDS}
        for t in decided:
            shares[t.picked] += 1
        return {t: c / n for t, c in shares.items()}
