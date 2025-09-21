"""
policies.py (Pharmacy domain)
"""

from src.core.reorder import suggest_order


def get_policy_for(sku: str, category: str = None) -> dict:
    """Return pharmacy policy dict for a given SKU/category."""
    if category in ["Opioids", "Narcotics"]:
        return {"service_level": 0.99, "moq": 1, "max_order_qty": 50}
    elif category in ["Antibiotics", "Vaccines"]:
        return {"service_level": 0.98, "moq": 5}
    else:
        return {"service_level": 0.95, "moq": 1}


def get_reorder_qty(sku, d_daily, sigma, lead, on_hand, moq, category=None):
    """
    Compute reorder qty using core logic, then apply pharmacy policy.
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

    # Enforce MOQ
    moq_policy = policy.get("moq", moq)
    if result["qty"] < moq_policy:
        result["qty"] = moq_policy

    # Enforce max cap (controlled substances)
    max_cap = policy.get("max_order_qty")
    if max_cap and result["qty"] > max_cap:
        result["qty"] = max_cap

    return result