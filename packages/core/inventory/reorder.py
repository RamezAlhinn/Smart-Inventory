import math

# Suggest how much to order (based on forecast, stock, and supplier rules).
# Inputs:
# - d_daily: average daily demand
# - sigma: demand variability (standard deviation)
# - lead_time_days: how many days supplier takes to deliver
# - on_hand: current stock
# - moq: minimum order quantity
# - z: service level factor (1.64 ≈ 95% confidence)
def suggest_order(daily_demand, sigma, lead, on_hand, moq):
    daily_demand = max(daily_demand, 0)
    reorder_point = max(daily_demand * lead + 1.65 * sigma, 0)
    qty = max(reorder_point - on_hand, 0)
    # round to MOQ
    qty = ((qty + moq - 1) // moq) * moq if qty > 0 else 0
    return int(qty), reorder_point, sigma