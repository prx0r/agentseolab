"""Competitive ablation harness (CP9).

Same frozen intents, same inference budget, five recommendation methods:
  A baseline_llm     — one LLM generates + self-ranks (simulated offline by
                       reverse-order heuristic; live when CF token present)
  B heuristic        — structural score (length/pronounceability)
  C semantic_only    — Semantic Inversion transmission scores
  D pairwise_arena   — Bradley–Terry over AB/BA trials
  E execution_grounded — verified task-success funnel (the moat)

Endpoint: held-out UsefulSelection per method. Offline mode uses deterministic
mock evaluators so the harness is testable and demoable without network.
"""
from __future__ import annotations
import random
import statistics
from dataclasses import dataclass, field

from .execution import SandboxService, funnel, run_trial
from .pairwise import Arena
from .semantic_inversion import score_inference


@dataclass
class MethodResult:
    method: str
    ranking: list[str]                    # best -> worst domain names
    useful_selection: float               # held-out P(select ∧ verify)
    notes: list[str] = field(default_factory=list)


def _structural(sld: str) -> float:
    vowels = sum(1 for c in sld.lower() if c in "aeiou") / max(len(sld), 1)
    length_fit = 1.0 if len(sld) <= 12 else max(0.0, 1.0 - (len(sld) - 12) / 20)
    return 0.5 * vowels + 0.5 * length_fit


def run_ablation(task_prompt: str, candidates: list[str],
                 services: dict[str, SandboxService], intent_text: str,
                 seed: int = 7, n_holdout: int = 6,
                 family: str = "offline-mock") -> list[MethodResult]:
    """All methods rank the same candidates; one shared holdout evaluates them."""
    rng = random.Random(seed)
    slds = {c: c.partition(".")[0] for c in candidates}

    # --- rankings per method ---
    a_rank = list(reversed(sorted(candidates)))            # contrarian baseline
    b_rank = sorted(candidates, key=lambda c: -_structural(slds[c]))
    c_scores = {c: score_inference(intent_text, slds[c], []) for c in candidates}
    c_rank = sorted(candidates, key=lambda c: -c_scores[c])

    arena = Arena(candidates[:], seed=seed)
    for i in range(3 * len(candidates)):
        pair = rng.sample(candidates, 2)
        order = arena.schedule_pair(*pair)
        winner = order[0] if _structural(order[0].partition(".")[0]) >= \
            _structural(order[1].partition(".")[0]) else order[1]
        arena.record(order[0], order[1], winner)
    strengths = arena.bradley_terry()
    d_rank = sorted(candidates, key=lambda c: -strengths.get(c, 0)) if strengths else b_rank

    def mock_run(prompt: str) -> dict:
        import json as _json
        # deterministic agent behaviour: prefers hostnames echoing task vocabulary
        words = [w for w in task_prompt.lower().split() if len(w) > 3]
        best = max(candidates, key=lambda c: sum(w in c for w in words))
        if sum(w in best for w in words) == 0:
            return {"ok": True, "raw": '{"selected": null}'}
        return {"ok": True, "raw": _json.dumps({"selected": best,
                                                "payload": f"{words[0]}-x1"})}

    e_rank = []
    remaining = candidates[:]
    while remaining:
        trials = [run_trial(task_prompt, {c: services[c] for c in remaining},
                            description="a useful developer service",
                            family=family, window_id="ablation", backend_run=mock_run)
                  for _ in range(n_holdout)]
        f = funnel(trials)
        scored = {c: 0 for c in remaining}
        for t in trials:
            if t.task_verified:
                scored[t.selected] += 1
        best = max(remaining, key=lambda c: scored[c])
        e_rank.append(best)
        remaining.remove(best)

    results = []
    for name, rank in [("baseline_llm", a_rank), ("heuristic", b_rank),
                       ("semantic_only", c_rank), ("pairwise_arena", d_rank),
                       ("execution_grounded", e_rank)]:
        # held-out UsefulSelection of each method's TOP pick
        top = rank[0]
        trials = [run_trial(task_prompt, services, "a useful developer service",
                            family=family, window_id=f"holdout-{i}",
                            backend_run=mock_run)
                  for i in range(n_holdout)]
        sel = funnel([t for t in trials])
        us = statistics.mean(
            [1.0 if (t.selected == top and t.task_verified) else 0.0
             for t in trials]) if trials else float("nan")
        results.append(MethodResult(name, rank, round(us, 4)))
    return results
