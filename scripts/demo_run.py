#!/usr/bin/env python3
"""DomainArena demo — runs the full lifecycle end-to-end.

Usage:
    # Fixture mode (no API keys)
    python scripts/demo_run.py

    # Live mode (requires NAMECOM credentials)
    DOMAINARENA_MODE=live python scripts/demo_run.py
"""
import json
import os
import sys
import time

# Ensure domainarena is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    from domainarena.service import get_service, DecisionStatus
    from domainarena.models import ConstraintSet

    mode = os.environ.get("DOMAINARENA_MODE", "fixture")
    print(f"\n{'='*60}")
    print(f"DomainArena Demo — mode={mode}")
    print(f"{'='*60}\n")

    svc = get_service()

    # Step 1: Intent
    print("[1/6] Intent")
    desc = "A JSON repair tool for fixing malformed JSON"
    print(f"  Description: {desc}")
    print(f"  Budget: $25 max purchase, $15 max renewal\n")

    constraints = ConstraintSet(max_purchase_price=25.0, max_renewal_price=15.0)

    # Step 2: Recommend
    print("[2/6] Recommendation (name.com search + evidence + Pareto)")
    import asyncio
    ds, cands = asyncio.run(svc.recommend_async(
        description=desc, primary_job=desc,
        audience="ai_agent", constraints=constraints, mode=mode))

    print(f"  Recommended: {ds.recommended_domain}")
    print(f"  Decision ID: {ds.decision_id}")
    print(f"  Status: {ds.status.value}")
    print(f"  Candidates: {len(cands)}")
    for c, ev in cands:
        sem = ev.semantic_transmission
        note = f"sem={sem.value}" if sem.value else "sem=N/A"
        print(f"    {c.domain_name:25s} ${c.inventory.purchase_price:6.2f}  {note}")
    print()

    # Step 3: Prepare
    print("[3/6] Prepare registration (fresh availability + pricing)")
    if mode == "live":
        prep = asyncio.run(svc.prepare_registration_async(ds.decision_id))
        print(f"  Status: {prep.get('status')}")
        print(f"  Price: ${prep.get('purchase_price', 'N/A')}")
        print(f"  Drift: {prep.get('price_drift_pct', 'N/A')}%")
    else:
        # Fixture: manually set preparation
        ds.preparation = {"approval_valid": True, "purchasable": True,
                          "purchase_price": 9.99}
        ds.transition(DecisionStatus.PREPARED)
        svc._persist(ds)
        print(f"  Status: PREPARED (fixture)")
    print()

    # Step 4: Approve
    print("[4/6] Approve")
    result = svc.approve(ds.decision_id)
    token = result["approval_token"]
    print(f"  Approved: {result['approved']}")
    print(f"  Token: {token[:8]}...{token[-8:]}")
    print()

    # Step 5: Register (sandbox only)
    print("[5/6] Register (sandbox mode)")
    if mode == "live" and os.environ.get("NAMECOM_MODE") == "sandbox":
        reg = asyncio.run(svc.register_async(ds.decision_id, token))
        print(f"  Status: {reg.get('status')}")
        print(f"  Domain: {reg.get('domain')}")
    else:
        print(f"  Skipped (mode={mode}, requires sandbox)")
    print()

    # Step 6: DNS receipt
    print("[6/6] DNS receipt")
    if mode == "live" and os.environ.get("NAMECOM_MODE") == "sandbox":
        dns = asyncio.run(svc.configure_dns_async(ds.decision_id))
        print(f"  Receipt: {dns.get('receipt_hash')}")
        print(f"  Verified: {dns.get('dns_receipt_verified')}")
    else:
        print(f"  Skipped (mode={mode}, requires sandbox)")
    print()

    # Summary
    print(f"{'='*60}")
    print(f"Demo complete!")
    print(f"  Domain: {ds.recommended_domain}")
    print(f"  Decision: {ds.decision_id}")
    print(f"  Mode: {mode}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
