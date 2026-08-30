"""Live recommendation pipeline: frozen intent → generators ∩ name.com Search →
feasibility → semantic proxy → audience-conditioned Pareto recommendation.

Read-only against production; registration stays gated upstream.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass

from .arena.semantic_inversion import aggregate, run_semantic_inversion
from .constraints import feasible
from .generators import generate_candidates, intersect_inventory
from .intent import freeze_intent, keywords_from_intent
from .models import (
    Audience, Candidate, ConstraintSet, DomainIntent, EvidenceVector, EvidenceValue,
    InventorySnapshot,
)
from .optimizer import Recommendation, recommend
from .providers.namecom import NameComClient, client_from_env


@dataclass
class LiveResult:
    intent: DomainIntent
    intent_hash: str
    raw_candidates: int
    in_inventory: int
    feasible: list[Candidate]
    rejected: dict[str, list[str]]
    evidence: dict[str, EvidenceVector]
    recommendation: Recommendation | None

    def to_dict(self) -> dict:
        return {
            "intent_hash": self.intent_hash,
            "raw_candidates": self.raw_candidates,
            "in_inventory": self.in_inventory,
            "feasible": [c.domain_name for c in self.feasible],
            "rejected": self.rejected,
            "recommendation": None if self.recommendation is None else {
                "domain": self.recommendation.domain_name,
                "score": round(self.recommendation.score, 4),
                "on_pareto_front": self.recommendation.on_pareto,
                "explanation": self.recommendation.explanation,
            },
        }


def _evidence_from_inventory(cands: list[Candidate],
                             sem_scores: dict[str, float]) -> dict[str, EvidenceVector]:
    ev = {}
    for c in cands:
        sld = c.inventory.sld
        # PROXY: structural fluency heuristic — labeled as such, never as
        # model stability (peer review §3.1). Real dims arrive from DA-T3/T6.
        pronounceable = sum(1 for ch in sld.lower() if ch in "aeiou") / max(len(sld), 1)
        length_fit = 1.0 if len(sld) <= 12 else max(0.0, 1.0 - (len(sld) - 12) / 20)
        struct = round(0.5 * pronounceable + 0.5 * length_fit, 3)

        sem = sem_scores.get(c.domain_name)
        sem_status = ("PROXY" if isinstance(sem, (int, float)) and sem is not None
                      else "NOT_MEASURED")

        def _ev(status, value=None, note=None):
            return {"value": value, "status": status,
                    "protocol": None, "n": None, "note": note}

        ev[c.domain_name] = EvidenceVector(
            semantic_transmission=EvidenceValue(
                **_ev(sem_status, float(sem) if sem is not None else None)),
            pairwise_strength=EvidenceValue(
                **_ev("NOT_MEASURED", None, "requires DA-T3 arena run")),
            structural_fluency_proxy=EvidenceValue(
                **_ev("PROXY", struct,
                      "vowel-ratio x length-fit heuristic; NOT model stability")),
            worst_family=EvidenceValue(
                **_ev("NOT_MEASURED", None, "requires multi-family arena")),
            task_success=EvidenceValue(
                **_ev("NOT_MEASURED", None, "requires DA-T6 execution run")),
        )
    return ev


async def recommend_live(
    description: str,
    primary_job: str,
    audiences: list[Audience],
    constraints: ConstraintSet,
    client: NameComClient | None = None,
    max_search_keywords: int = 4,
) -> LiveResult:
    own_client = client is None
    client = client or client_from_env()
    try:
        intent, ihash = freeze_intent(description, primary_job, audiences, constraints)
        kws = keywords_from_intent(intent)[:max_search_keywords] or [primary_job.split()[0].lower()]

        raw = generate_candidates(intent)

        # name.com Search itself is a generator: query real inventory per keyword
        snaps: list[InventorySnapshot] = []
        seen_names: set[str] = set()
        tasks = [client.search(kw, constraints.allowed_tlds[:8]) for kw in kws]
        for batch in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(batch, Exception):
                continue
            for s in batch:
                if s.domain_name not in seen_names:
                    seen_names.add(s.domain_name)
                    snaps.append(s)

        matched = intersect_inventory(raw + [
            Candidate(candidate_id=f"inv_{i}", domain_name=s.domain_name,
                      generator="namecom_search", inventory=s)
            for i, s in enumerate(snaps)], snaps)

        keep = []
        rejected: dict[str, list[str]] = {}
        for c in matched:
            ok, reasons = feasible(c.inventory, constraints)
            (keep.append(c) if ok else rejected.setdefault(c.domain_name, reasons))

        inv_results = run_semantic_inversion(keep[:20], f"{description} {primary_job}")
        sem_scores = aggregate(inv_results)
        evidence = _evidence_from_inventory(keep, sem_scores)

        pairs = [(c, evidence[c.domain_name]) for c in keep]
        rec = recommend(pairs, audiences[0]) if pairs else None
        return LiveResult(intent, ihash, len(raw) + len(snaps), len(matched),
                          keep, rejected, evidence, rec)
    finally:
        if own_client:
            await client.close()


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

    res = asyncio.run(recommend_live(
        description="Repairs malformed JSON for AI agents",
        primary_job="repair JSON",
        audiences=["ai_agent"],
        constraints=ConstraintSet(max_purchase_price=20, max_renewal_price=30),
    ))
    print(json.dumps(res.to_dict(), indent=2))
