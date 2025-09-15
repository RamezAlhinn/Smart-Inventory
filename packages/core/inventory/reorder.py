import math

def suggest_order(daily_demand: float, sigma: float, lead: int, on_hand: float, moq: int, z: float = 1.65):
    """
    Stable reorder rule:
    - ROP = demand during lead + safety stock
    - Order ceil(ROP - on_hand) (rounded up), then round to MOQ.
    - Guard against zeros everywhere.
    """
    daily_demand = max(float(daily_demand), 0.1)
    sigma = max(float(sigma or 0.0), 0.0)
    lead = max(int(lead), 1)
    moq = max(int(moq), 1)

    demand_lead = daily_demand * lead
    safety_stock = z * sigma * (lead ** 0.5)
    rop = max(demand_lead + safety_stock, 0.0)

    raw_qty = rop - float(on_hand)
    qty = math.ceil(raw_qty) if raw_qty > 0 else 0
    if qty > 0:
        qty = ((qty + moq - 1) // moq) * moq  # round up to MOQ

    return int(qty), float(rop), float(safety_stock)