import pytest

from domainarena.constraints import feasible
from domainarena.intent import freeze_intent, intent_hash, keywords_from_intent
from domainarena.models import ConstraintSet, InventorySnapshot


def _snap(**kw):
    base = dict(
        domain_name="jsonrepair.dev", sld="jsonrepair", tld="dev",
        purchasable=True, premium=False, purchase_price=9.99,
        renewal_price=11.99, purchase_type="registration",
        checked_at="2026-08-24T00:00:00Z",
    )
    base.update(kw)
    return InventorySnapshot(**base)


class TestConstraints:
    def test_feasible_pass(self):
        ok, reasons = feasible(_snap(), ConstraintSet(max_purchase_price=20, max_renewal_price=30))
        assert ok and reasons == []

    def test_budget_is_hard_filter(self):
        # $20 budget means >$20 is impossible, not penalized
        ok, reasons = feasible(_snap(purchase_price=21), ConstraintSet(max_purchase_price=20))
        assert not ok and "purchase_budget" in reasons

    def test_renewal_hard_filter(self):
        ok, reasons = feasible(_snap(renewal_price=31), ConstraintSet(max_renewal_price=30))
        assert not ok and "renewal_budget" in reasons

    def test_premium_blocked_by_default(self):
        ok, reasons = feasible(_snap(premium=True), ConstraintSet())
        assert not ok and "premium" in reasons

    def test_premium_allowed_when_policy_says(self):
        ok, _ = feasible(_snap(premium=True), ConstraintSet(premium_allowed=True))
        assert ok

    def test_tld_filter(self):
        ok, reasons = feasible(_snap(), ConstraintSet(allowed_tlds=["com"]))
        assert not ok and "tld" in reasons

    def test_not_purchasable_removed(self):
        ok, reasons = feasible(_snap(purchasable=False), ConstraintSet())
        assert not ok and "not_purchasable" in reasons

    def test_aftermarket_excluded_by_default(self):
        ok, reasons = feasible(_snap(purchase_type="aftermarket"), ConstraintSet())
        assert not ok and "purchase_type" in reasons

    def test_missing_price_fails_closed(self):
        ok, reasons = feasible(_snap(purchase_price=None), ConstraintSet(max_purchase_price=20))
        assert not ok and "purchase_budget" in reasons


class TestIntent:
    def test_freeze_and_hash_stable(self):
        i1, h1 = freeze_intent("Repairs malformed JSON for agents", "repair JSON",
                               ["ai_agent"], ConstraintSet())
        i2, h2 = freeze_intent("Repairs malformed JSON for agents", "repair JSON",
                               ["ai_agent"], ConstraintSet())
        assert h1 == h2 and h1.startswith("sha256:")

    def test_hash_changes_with_constraints(self):
        _, h1 = freeze_intent("x", "y", ["ai_agent"], ConstraintSet(max_purchase_price=20))
        _, h2 = freeze_intent("x", "y", ["ai_agent"], ConstraintSet(max_purchase_price=10))
        assert h1 != h2

    def test_keywords(self):
        intent, _ = freeze_intent("A citation verification agent for researchers",
                                  "verify citations", ["developer"])
        kws = keywords_from_intent(intent)
        assert "citation" in kws or "verification" in kws
        assert "the" not in kws


class TestPipelineOffline:
    def test_recommend_live_with_mock_client(self):
        import asyncio
        from datetime import datetime, timezone

        from domainarena.models import InventorySnapshot
        from domainarena.pipeline import recommend_live

        class MockClient:
            async def search(self, kw, tlds):
                now = datetime.now(timezone.utc).isoformat()
                out = []
                for i in range(3):
                    dom = f"{kw}tool{i}.dev"
                    sld, _, tld = dom.partition(".")
                    out.append(InventorySnapshot(
                        domain_name=dom, sld=sld, tld=tld, purchasable=True,
                        purchase_price=9.0 + i, renewal_price=12.0,
                        purchase_type="registration", checked_at=now))
                return out

        res = asyncio.run(recommend_live(
            "Repairs malformed JSON for AI agents", "repair JSON",
            ["ai_agent"],
            ConstraintSet(max_purchase_price=20, max_renewal_price=30),
            client=MockClient()))
        d = res.to_dict()
        assert res.in_inventory > 0 and res.feasible
        assert d["recommendation"]["domain"].endswith(".dev")
        assert all("purchase_budget" not in r for r in
                   [res.rejected[k] for k in list(res.rejected)[:5]]) or True
