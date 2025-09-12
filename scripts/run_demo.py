import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from packages.core.inventory.reorder import suggest_order

# Load sales + stock data from CSVs
sales = pd.read_csv("data/sales.csv")
stock = pd.read_csv("data/stock.csv")

sku = "MILK1"  # test SKU
# Get sales for this SKU
s_df = sales[(sales["sku"]==sku) & (sales["store_id"]=="S1")][["date","qty_sold"]]

# Convert to daily series (fills gaps with 0)
series = to_daily(s_df)

# Forecast next 7 days using moving average
fcst = moving_avg_forecast(series, window=7, horizon=7)

# Average forecasted demand (daily)
d_daily = fcst["yhat"].mean()

# Demand variability (last 28 days)
sigma = series.tail(28).std() if len(series)>=2 else 0.0

# Get current stock
on_hand = int(stock[(stock["sku"]==sku) & (stock["store_id"]=="S1")]["on_hand"].iloc[0])

# Run reorder calculation
qty, rop, ss = suggest_order(d_daily, sigma, lead_time_days=5, on_hand=on_hand, moq=1)

# Build purchase order row
po = pd.DataFrame([{
    "sku": sku,
    "on_hand": on_hand,
    "avg_next7": round(d_daily,2),
    "ROP": round(rop,1),
    "suggested_qty": qty
}])

# Save to CSV
po.to_csv("data/suggested_po.csv", index=False)
print("OK -> data/suggested_po.csv")