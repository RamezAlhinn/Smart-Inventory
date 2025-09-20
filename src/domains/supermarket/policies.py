from src.core.reorder import suggest_order


def get_policy_for(sku: str, category: str = None) -> dict:
    """
    Return supermarket policy dict for a given SKU/category.
    Example: {"service_level": 0.95, "moq": 1}
    """
    if category in ["Dairy", "Bakery", "Produce"]:
        return {"service_level": 0.97, "moq": 5}
    return {"service_level": 0.90, "moq": 1}


def get_reorder_qty(sku, d_daily, sigma, lead, on_hand, moq, category=None):
    """
    Compute reorder quantity using core logic, then apply supermarket policy.
    """
    policy = get_policy_for(sku, category)
    base_qty, rop, ss = suggest_order(
        d_daily, sigma, lead, on_hand, moq
    )

    # Enforce MOQ from policy if higher
    moq_policy = policy.get("moq", moq)
    if base_qty < moq_policy:
        base_qty = moq_policy

    return base_qty, rop, ss