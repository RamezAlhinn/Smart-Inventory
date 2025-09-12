import math

def suggest_order(d_daily: float, sigma: float, lead_time_days: int, on_hand: int, moq: int = 1, z: float = 1.64):
    ss = z * sigma * math.sqrt(max(lead_time_days,1))
    rop = d_daily * lead_time_days + ss
    qty = max(0, int(round(rop - on_hand)))
    if moq > 1 and qty % moq != 0:
        qty = ((qty + moq - 1)//moq)*moq
    return qty, rop, ss