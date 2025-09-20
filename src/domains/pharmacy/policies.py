from src.core.reorder import suggest_order


def get_policy_for(sku: str, category: str = None) -> dict:
    """
    Return pharmacy policy dict for a given SKU/category.
    Example: {"service_level": 0.99, "moq": 1, "max_order_qty": 100}
    """
    if category in ["Opioids", "Narcotics"]:
        return {"service_level": 0.99, "moq": 1, "max_order_qty": 50}
    elif category in ["Antibiotics", "Vaccines"]:
        return {"service_level": 0.98, "moq": 5}
    else:
        return {"service_level": 0.95, "moq": 1}


def get_reorder_qty(sku, d_daily, sigma, lead, on_hand, moq, category=None):
    """
    Compute reorder quantity using core logic, then apply pharmacy policy.
    """
    policy = get_policy_for(sku, category)
    base_qty, rop, ss = suggest_order(
        d_daily, sigma, lead, on_hand, moq
    )

    # Enforce MOQ
    moq_policy = policy.get("moq", moq)
    if base_qty < moq_policy:
        base_qty = moq_policy

    # Enforce max cap (controlled substances)
    max_cap = policy.get("max_order_qty")
    if max_cap and base_qty > max_cap:
        base_qty = max_cap

    return base_qty, rop, ss