import math

def suggest_order(daily_demand: float, sigma: float, lead: int, on_hand: float, moq: int, z: float = 1.65):
    """
    Stable reorder rule:
    - If demand <= 0 → no demand, no safety stock.
    - Otherwise, use standard ROP = demand during lead + safety stock.
    """
    lead = max(int(lead), 1)
    moq = max(int(moq), 1)

    if daily_demand <= 0:
        daily_demand = 0.0
        sigma = 0.0

    demand_lead = daily_demand * lead
    safety_stock = z * sigma * (lead ** 0.5)
    rop = demand_lead + safety_stock

    raw_qty = rop - float(on_hand)
    qty = math.ceil(raw_qty) if raw_qty > 0 else 0

    if qty > 0:
        qty = ((qty + moq - 1) // moq) * moq  # round up to MOQ

    return int(qty), float(rop), float(safety_stock)