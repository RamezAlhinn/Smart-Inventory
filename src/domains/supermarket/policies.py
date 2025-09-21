"""
policies.py (Supermarket domain)
"""

from src.core.reorder import suggest_order


def get_policy_for(sku: str, category: str = None) -> dict:
    """Return supermarket policy for a given SKU/category."""
    if category in ["Dairy", "Bakery", "Produce"]:
        return {"service_level": 0.97, "moq": 5}
    return {"service_level": 0.90, "moq": 1}


def get_reorder_qty(sku, d_daily, sigma, lead, on_hand, moq, category=None):
    """
    Compute reorder qty using core logic, then apply supermarket policy.
    Returns a dict with qty, rop, safety_stock, etc.
    """
    policy = get_policy_for(sku, category)
    result = suggest_order(
        daily_demand=d_daily,
        sigma=sigma,
        lead=lead,
        on_hand=on_hand,
        moq=moq,
    )

    # Enforce MOQ from policy
    moq_policy = policy.get("moq", moq)
    if result["qty"] < moq_policy:
        result["qty"] = moq_policy

    return result