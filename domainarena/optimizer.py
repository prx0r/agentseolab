"""Audience-conditioned policy + Pareto selection over feasible candidates."""
from __future__ import annotations
from dataclasses import dataclass

from .models import Candidate, EvidenceVector

PRESETS = {
    "agent_api": {
        "semantic_transmission": 0.25,
        "task_success": 0.25,
        "pairwise_strength": 0.15,
        "model_stability": 0.20,
        "brand_elasticity": 0.05,
        "human_recall": 0.00,
        "worst_family": 0.10,
    },
    "developer": {
        "semantic_transmission": 0.22,
        "task_success": 0.18,
        "pairwise_strength": 0.14,
        "model_stability": 0.16,
        "brand_elasticity": 0.10,
        "human_recall": 0.10,
        "worst_family": 0.10,
    },
    "consumer": {
        "semantic_transmission": 0.15,
        "task_success": 0.05,
        "pairwise_strength": 0.10,
        "model_stability": 0.10,
        "brand_elasticity": 0.20,
        "human_recall": 0.30,
        "worst_family": 0.10,
    },
}


def _vec(ev: EvidenceVector) -> dict[str, float]:
    return {k: (getattr(ev, k) if getattr(ev, k) is not None else 0.0)
            for k in PRESETS["agent_api"]}


def _preset_for(audience: str) -> str:
    return "agent_api" if audience == "ai_agent" else audience


def weighted_score(ev: EvidenceVector, audience: str) -> float:
    weights = PRESETS[_preset_for(audience)]
    v = _vec(ev)
    total_w = sum(weights.values())
    return sum(v[k] * w for k, w in weights.items()) / total_w


def _dims(cand: Candidate, ev: EvidenceVector) -> dict[str, float]:
    return {
        **_vec(ev),
        "economics": -(cand.inventory.purchase_price or 0.0),
        "renewal_economics": -(cand.inventory.renewal_price or 0.0),
    }


def pareto_front(candidates: list[tuple[Candidate, EvidenceVector]]) -> list[str]:
    """Pareto over evidence dims + economics (price = minimize)."""
    ds = {c.candidate_id: _dims(c, ev) for c, ev in candidates}
    front: list[str] = []
    for cand, _ in candidates:
        a = ds[cand.candidate_id]
        dominated = False
        for other, _ in candidates:
            if other.candidate_id == cand.candidate_id:
                continue
            b = ds[other.candidate_id]
            if all(b[k] >= a[k] for k in a) and any(b[k] > a[k] for k in a):
                dominated = True
                break
        if not dominated:
            front.append(cand.candidate_id)
    return front


@dataclass
class Recommendation:
    candidate_id: str
    domain_name: str
    audience: str
    score: float
    on_pareto: bool
    explanation: list[str]


def recommend(
    candidates: list[tuple[Candidate, EvidenceVector]],
    audience: str,
) -> Recommendation:
    """Choose among Pareto candidates via the audience preset; explain why."""
    front = set(pareto_front(candidates))
    best: tuple[float, Candidate, EvidenceVector] | None = None
    for cand, ev in candidates:
        s = weighted_score(ev, audience)
        if best is None or s > best[0]:
            best = (s, cand, ev)
    assert best is not None, "no candidates"
    s, cand, ev = best
    weights = PRESETS[_preset_for(audience)]
    v = _vec(ev)
    top_dims = sorted(weights, key=lambda k: -weights[k] * (v[k]))[:3]
    explanation = [
        f"audience preset '{audience}' weights {top_dims[0]}, {top_dims[1]}, {top_dims[2]} most heavily",
    ]
    if ev.worst_family is not None and ev.model_stability is not None:
        explanation.append(
            f"robust across families (mean {ev.model_stability:.2f}, "
            f"worst family {ev.worst_family:.2f})")
    if cand.inventory.purchase_price is not None:
        explanation.append(f"first-year ${cand.inventory.purchase_price:.2f}, "
                           f"renewal ${cand.inventory.renewal_price or 0:.2f} within hard budget")
    return Recommendation(
        candidate_id=cand.candidate_id,
        domain_name=cand.domain_name,
        audience=audience,
        score=s,
        on_pareto=cand.candidate_id in front,
        explanation=explanation,
    )
