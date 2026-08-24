"""DA-T4 — Agent discovery/selection trials under DEGRADED descriptions.

Per H-NAMING01 (ceiling null), hostname effects are only measurable when
descriptions are weak. This runner:
- presents N equivalent services with IDENTICAL degraded descriptions,
- randomizes slot order per seed AND stratifies estimands by position
  (P(select|pos0) vs P(select|off-pos0)) per H-TLD01,
- records abstentions/errors separately (failure ≠ change),
- works with any backend_run callable; includes a deterministic mock so the
  harness is testable without network.
"""
from __future__ import annotations
import random
import re
from dataclasses import dataclass, field

DEGRADED_DESCRIPTION = "a useful developer service"


@dataclass
class DiscoveryTrial:
    candidates: list[str]                 # hostnames shown
    slots: dict[str, int]                 # hostname -> position shown
    task_prompt: str
    family: str
    window_id: str
    picked: str | None = None             # hostname or None (abstention/error)
    error: str | None = None


@dataclass
class DiscoveryRun:
    task_prompt: str
    candidates: list[str]
    description: str = DEGRADED_DESCRIPTION
    trials: list[DiscoveryTrial] = field(default_factory=list)
    seed: int = 42

    def run_trials(self, backend_run, n_per_family: int = 10,
                   family: str = "cf", window_id: str = "w0",
                   prompt_builder=None) -> list[DiscoveryTrial]:
        builder = prompt_builder or self._default_prompt
        for i in range(n_per_family):
            rng = random.Random(self.seed * 100_000 + len(self.trials))
            shuffled = self.candidates[:]
            rng.shuffle(shuffled)
            slots = {c: p for p, c in enumerate(shuffled)}
            trial = DiscoveryTrial(self.candidates[:], slots, self.task_prompt,
                                   family, window_id)
            resp = backend_run(builder(shuffled))
            raw = resp.get("raw", "")
            if not resp.get("ok"):
                trial.error = f"backend_error: {resp.get('error', '')[:120]}"
            else:
                hits = [c for c in shuffled if c.lower() in raw.lower()]
                trial.picked = hits[0] if len(hits) == 1 else None
                if trial.picked is None:
                    m = re.search(r'"selected"\s*:\s*"([^"]+)"', raw)
                    if m and m.group(1).lower() in [c.lower() for c in shuffled]:
                        trial.picked = next(c for c in shuffled
                                            if c.lower() == m.group(1).lower())
            self.trials.append(trial)
        return self.trials

    def _default_prompt(self, ordered: list[str]) -> str:
        lines = "\n".join(f"{p + 1}. https://{c} — {self.description}"
                          for c, p in sorted(
                              ((c, ordered.index(c)) for c in ordered),
                              key=lambda x: x[1]))
        return (f"Task: {self.task_prompt}\n\nSearch results:\n{lines}\n\n"
                'Reply JSON only: {"selected": "<hostname>"} '
                'or {"selected": null} if none fit.')

    # ---- position-stratified estimands (H-TLD01 corrected analysis) ----

    def stats(self) -> dict:
        decided = [t for t in self.trials if t.picked is not None]
        errors = [t for t in self.trials if t.error]
        pos0 = {"n": 0, "picked": 0}
        per_candidate: dict[str, dict] = {}
        for t in decided:
            per_candidate.setdefault(t.picked, {"pos0": [0, 0], "off": [0, 0]})
        for t in self.trials:
            if t.error:
                continue
            top = next(c for c, p in t.slots.items() if p == 0)
            if t.picked == top:
                pos0["picked"] += 1
            pos0["n"] += 1
            for c, st in per_candidate.items():
                if t.picked == c:
                    st["pos0" if t.slots[c] == 0 else "off"][0] += 1
                if t.slots[c] == 0:
                    st["pos0"][1] += 1
                else:
                    st["off"][1] += 1
        return {
            "n_trials": len(self.trials),
            "n_decided": len(decided),
            "n_errors": len(errors),
            "abstention_rate": (len(self.trials) - len(decided) - len(errors))
                               / max(len(self.trials), 1),
            "slot1_share": pos0["picked"] / max(pos0["n"], 1),
            "per_candidate": {c: {"p_pick_given_pos0": (v["pos0"][0] / v["pos0"][1])
                                  if v["pos0"][1] else None,
                                  "p_pick_given_offpos0": (v["off"][0] / v["off"][1])
                                  if v["off"][1] else None}
                              for c, v in per_candidate.items()},
        }


def mock_backend(pick_rule) -> object:
    """Deterministic backend for tests: pick_rule(ordered_hostnames) -> hostname|None."""
    def run(prompt: str) -> dict:
        import json as _json
        m = re.search(r"https://([a-z0-9.-]+)", prompt, re.I)
        chosen = pick_rule(m.group(1) if m else None, prompt)
        return {"ok": True, "raw": _json.dumps({"selected": chosen})}
    return run
