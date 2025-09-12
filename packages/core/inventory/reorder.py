import math

# Suggest how much to order (based on forecast, stock, and supplier rules).
# Inputs:
# - d_daily: average daily demand
# - sigma: demand variability (standard deviation)
# - lead_time_days: how many days supplier takes to deliver
# - on_hand: current stock
# - moq: minimum order quantity
# - z: service level factor (1.64 ≈ 95% confidence)
def suggest_order(d_daily: float, sigma: float, lead_time_days: int, on_hand: int, moq: int = 1, z: float = 1.64):
     # Safety stock = buffer to handle uncertainty
    ss = z * sigma * math.sqrt(max(lead_time_days,1))
     # Reorder point = demand during lead time + safety stock
    rop = d_daily * lead_time_days + ss
    # Suggested qty = how much stock is missing to reach ROP
    qty = max(0, int(round(rop - on_hand)))
    # Adjust to MOQ (round up to multiples of MOQ)
    if moq > 1 and qty % moq != 0:
        qty = ((qty + moq - 1)//moq)*moq
    return qty, rop, ss