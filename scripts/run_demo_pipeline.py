"""Offline end-to-end DomainArena pipeline demo.

Runs the full tier ladder with zero network access (deterministic fixtures +
sandbox execution services). Produces the evidence-shaped output that the live
pipeline produces once name.com credentials are configured.

Usage: python3 scripts/run_demo_pipeline.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domainarena.arena.execution import SandboxService, funnel, run_trial  # noqa: E402
from domainarena.arena.pairwise import Arena  # noqa: E402
from domainarena.arena.semantic_inversion import aggregate, run_semantic_inversion  # noqa: E402
from domainarena.arena.stability import FamilyOutcome, robustness_report  # noqa: E402
from domainarena.constraints import feasible  # noqa: E402
from domainarena.fixtures import DEMO_CANDIDATES, DEMO_INTENTS  # noqa: E402
from domainarena.intent import freeze_intent  # noqa: E402
from domainarena.models import (  # noqa: E402
    Candidate, ConstraintSet, EvidenceVector, InventorySnapshot,
)
from domainarena.optimizer import recommend  # noqa: E402


def _cand(row) -> tuple[Candidate, EvidenceVector]:
    dom, price, renew, sem, stab, worst, task = row
    sld, _, tld = dom.partition(".")
    cand = Candidate(
        candidate_id=dom, domain_name=dom, generator="demo",
        inventory=InventorySnapshot(
            domain_name=dom, sld=sld, tld=tld, purchasable=True,
            purchase_price=price, renewal_price=renew,
            purchase_type="registration", checked_at="2026-08-24T00:00:00Z"),
    )
    ev = EvidenceVector(semantic_transmission=sem, model_stability=stab,
                        worst_family=worst, task_success=task)
    return cand, ev


def main() -> dict:
    report: dict[str, dict] = {}
    for spec in DEMO_INTENTS:
        intent, ihash = freeze_intent(
            spec["description"], spec["primary_job"], [spec["audience"]],
            ConstraintSet(max_purchase_price=spec["max_purchase_price"],
                          max_renewal_price=spec.get("max_renewal_price", 30)))
        cands = [_cand(r) for r in DEMO_CANDIDATES]
        cands = [(c, ev) for c, ev in cands
                 if feasible(c.inventory, intent.constraints)[0]]

        rec = recommend(cands, spec["audience"])

        # Tier 6 demo: execution-grounded trials on the winner vs a rival
        rival = next(c.domain_name for c, _ in cands if c.domain_name != rec.domain_name)
        services = {
            rec.domain_name: SandboxService(rec.domain_name),
            rival: SandboxService(rival, works=False),
        }

        def fake_backend(prompt: str) -> dict:
            # deterministic stand-in for a fresh agent session: prefers the
            # service whose hostname echoes the task vocabulary.
            task_word = spec["primary_job"].split()[0].lower()
            match = next((d for d in sorted(services)
                          if task_word in d or task_word[:4] in d), None)
            if match is None:
                return {"ok": True, "raw": '{"selected": null}'}
            return {"ok": True,
                    "raw": json.dumps({"selected": match,
                                       "payload": f"{task_word}-request-001"})}

        trials = [
            run_trial(spec["primary_task"] if "primary_task" in spec else spec["primary_job"],
                      {k: services[k] for k in order}, description="a useful developer service",
                      family="demo-fixture", window_id=f"w{i % 2}", backend_run=fake_backend)
            for i, order in enumerate([sorted(services), list(reversed(sorted(services)))] * 3)
        ]

        outcomes = [
            FamilyOutcome("demo-fixture", "w0", 0.82, 30),
            FamilyOutcome("demo-fixture", "w1", 0.79, 30),
            FamilyOutcome("rival-family", "w0", 0.44, 30),
        ]

        report[spec["primary_job"]] = {
            "intent_hash": ihash,
            "audience": spec["audience"],
            "recommended": rec.domain_name,
            "score": round(rec.score, 4),
            "explanation": rec.explanation,
            "execution_funnel": funnel(trials),
            "robustness": robustness_report(outcomes)["worst_family"],
        }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
