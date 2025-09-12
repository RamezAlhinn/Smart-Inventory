import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from packages.core.inventory.reorder import suggest_order


sales = pd.read_csv("data/sales.csv")
stock = pd.read_csv("data/stock.csv")

sku = "MILK1"
s_df = sales[(sales["sku"]==sku) & (sales["store_id"]=="S1")][["date","qty_sold"]]
series = to_daily(s_df)
fcst = moving_avg_forecast(series, window=7, horizon=7)

d_daily = fcst["yhat"].mean()                      # avg next 7 days
sigma = series.tail(28).std() if len(series)>=2 else 0.0
on_hand = int(stock[(stock["sku"]==sku) & (stock["store_id"]=="S1")]["on_hand"].iloc[0])

qty, rop, ss = suggest_order(d_daily, sigma, lead_time_days=5, on_hand=on_hand, moq=1)
po = pd.DataFrame([{"sku": sku, "on_hand": on_hand, "avg_next7": round(d_daily,2), "ROP": round(rop,1), "suggested_qty": qty}])
po.to_csv("data/suggested_po.csv", index=False)
print("OK -> data/suggested_po.csv")