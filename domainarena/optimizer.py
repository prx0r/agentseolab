"""Audience-conditioned policy + Pareto selection over feasible candidates."""
from __future__ import annotations
from dataclasses import dataclass

from .models import Candidate, EvidenceVector

PRESETS = {
    "agent_api": {
        "semantic_transmission": 0.25,
        "task_success": 0.25,
        "pairwise_strength": 0.15,
        "structural_fluency_proxy": 0.08,
        "brand_elasticity": 0.05,
        "human_recall": 0.00,
        "worst_family": 0.10,
    },
    "developer": {
        "semantic_transmission": 0.22,
        "task_success": 0.18,
        "pairwise_strength": 0.14,
        "structural_fluency_proxy": 0.06,
        "brand_elasticity": 0.10,
        "human_recall": 0.10,
        "worst_family": 0.10,
    },
    "consumer": {
        "semantic_transmission": 0.15,
        "task_success": 0.05,
        "pairwise_strength": 0.10,
        "structural_fluency_proxy": 0.05,
        "brand_elasticity": 0.20,
        "human_recall": 0.30,
        "worst_family": 0.10,
    },
}


PROXY_DISCOUNT = 0.5   # proxies contribute half-weight value (peer review §3.1)

def _vec(ev: EvidenceVector) -> tuple[dict[str, float | None], float]:
    """Returns (values-with-None-for-unmeasured, coverage).
    Coverage = measured weight / requested weight (review §3.2)."""
    vals: dict[str, float | None] = {}
    num = den = 0.0
    for k in PRESETS["agent_api"]:
        evd = getattr(ev, k, None)
        w = PRESETS["agent_api"][k]
        den += w
        v = getattr(evd, "value", evd) if not isinstance(evd, (int, float)) else evd
        st = getattr(evd, "status", None)
        if isinstance(evd, dict):
            v = evd.get("value"); st = evd.get("status")
        if v is None or st == "NOT_MEASURED":
            vals[k] = None
        elif st == "PROXY":
            vals[k] = float(v) * PROXY_DISCOUNT
            num += w * vals[k]; den += w
        else:
            vals[k] = float(v); num += w * vals[k]
    measured_w = sum(
        PRESETS["agent_api"][k] for k in PRESETS["agent_api"]
        if vals.get(k) is not None) or 1.0
    coverage = round(sum(PRESETS["agent_api"][k]
                         for k in PRESETS["agent_api"]
                         if vals.get(k) is not None) / sum(PRESETS["agent_api"].values()), 4)
    return vals, coverage


def _preset_for(audience: str) -> str:
    return "agent_api" if audience == "ai_agent" else audience


def weighted_score(ev: EvidenceVector, audience: str) -> tuple[float, float]:
    """(score, coverage). Score renormalized over MEASURED dimensions —
    missing evidence never masquerades as failure (peer review §3.2)."""
    weights = PRESETS[_preset_for(audience)]
    v, coverage = _vec(ev)
    num = den = 0.0
    for k, w in weights.items():
        if v.get(k) is None:
            continue
        num += v[k] * w
        den += w
    score = num / den if den > 0 else 0.0
    return score, coverage


def _dims(cand: Candidate, ev: EvidenceVector,
          max_purchase: float | None = None,
          max_renewal: float | None = None) -> dict[str, float]:
    v, _cov = _vec(ev)
    dims = {k: (val if val is not None else 0.0) for k, val in v.items()}
    # peer review §3.4: null price = unknown, never free.
    # Penalize with the worst allowed price (constraint ceiling) when set;
    # otherwise a large sentinel so unknown never wins economics.
    p = cand.inventory.purchase_price
    r = cand.inventory.renewal_price
    dims["economics"] = -(p if p is not None
                          else (max_purchase if max_purchase is not None else 10**6))
    dims["renewal_economics"] = -(r if r is not None
                                  else (max_renewal if max_renewal is not None else 10**6))
    return dims


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
    recommendation_status: str = "PROVISIONAL"
    evidence_coverage: float = 0.0


def recommend(
    candidates: list[tuple[Candidate, EvidenceVector]],
    audience: str,
) -> Recommendation:
    """Peer review §3.3: hard feasibility -> evidence sufficiency ->
    Pareto-front restriction -> policy tie-breaker. Selection restricted to
    the Pareto front; coverage <0.70 flagged INSUFFICIENT_EVIDENCE."""
    front = set(pareto_front(candidates))
    pool = [(c, ev) for c, ev in candidates if c.candidate_id in front] or candidates
    best: tuple[float, Candidate, EvidenceVector, float] | None = None
    for cand, ev in pool:
        s, cov = weighted_score(ev, audience)
        if best is None or s > best[0]:
            best = (s, cand, ev, cov)
    assert best is not None, "no candidates"
    s, cand, ev, cov = best
    weights = PRESETS[_preset_for(audience)]
    v, _cov = _vec(ev)
    top_dims = sorted(weights, key=lambda k: -weights[k])[:3]
    explanation = [
        f"audience preset '{audience}' weights {top_dims[0]}, {top_dims[1]}, {top_dims[2]} most heavily",
    ]
    if getattr(ev, "structural_fluency_proxy", None) is not None and \
       getattr(ev.structural_fluency_proxy, "value", None) is not None:
        explanation.append(
            "structural fluency PROXY included at half weight "
            "(not model stability; DA-T4/T6 trials pending)")
    if cand.inventory.purchase_price is not None:
        explanation.append(f"first-year ${cand.inventory.purchase_price:.2f}, "
                           f"renewal ${cand.inventory.renewal_price or 0:.2f} within hard budget")

    # evidence-sufficiency gate (peer review §3.2)
    rec_status = "VALIDATED" if cov >= 0.70 else "INSUFFICIENT_EVIDENCE"
    if cov < 0.70:
        explanation.append(
            f"INSUFFICIENT_EVIDENCE: coverage {cov:.0%} — provisional recommendation only")
    return Recommendation(
        candidate_id=cand.candidate_id,
        domain_name=cand.domain_name,
        audience=audience,
        score=s,
        recommendation_status=rec_status,
        evidence_coverage=cov,
        on_pareto=cand.candidate_id in front,
        explanation=explanation,
    )
