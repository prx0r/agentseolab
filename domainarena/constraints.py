from .models import ConstraintSet, InventorySnapshot


def feasible(inv: InventorySnapshot, c: ConstraintSet) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not inv.purchasable:
        reasons.append("not_purchasable")
    if inv.purchase_type not in c.purchase_types:
        reasons.append("purchase_type")
    if inv.tld not in {t.lower().lstrip('.') for t in c.allowed_tlds}:
        reasons.append("tld")
    if inv.premium and not c.premium_allowed:
        reasons.append("premium")
    if c.max_purchase_price is not None:
        if inv.purchase_price is None or inv.purchase_price > c.max_purchase_price:
            reasons.append("purchase_budget")
    if c.max_renewal_price is not None:
        if inv.renewal_price is None or inv.renewal_price > c.max_renewal_price:
            reasons.append("renewal_budget")
    return (not reasons, reasons)
