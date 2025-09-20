from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from src.core.forecasting.prophet_model import forecast_prophet
from src.core.reorder.reorder import suggest_order

# Load sales + stock data
sales = pd.read_csv("data/sales.csv")
stock = pd.read_csv("data/stock.csv")

sku = "MILK1"
s_df = sales[(sales["sku"]==sku) & (sales["store_id"]=="S1")][["date","qty_sold"]]

# Convert to daily series
series = to_daily(s_df)

# Prepare Prophet input
df_prophet = series.reset_index().rename(columns={"date": "ds", "qty_sold": "y"})

# Forecast demand
try:
    fcst = forecast_prophet(df_prophet, horizon=7)
    fcst["yhat"] = fcst["yhat"].clip(lower=0)
    d_daily = fcst["yhat"].mean()
except Exception:
    fcst = moving_avg_forecast(series, window=7, horizon=7)
    d_daily = fcst["yhat"].mean()

# Variability
sigma = max(series.tail(28).std(), 0.1)

# Current stock
on_hand = int(stock[(stock["sku"]==sku) & (stock["store_id"]=="S1")]["on_hand"].iloc[0])

# Reorder
qty, rop, ss = suggest_order(d_daily, sigma, lead_time_days=5, on_hand=on_hand, moq=1)

# Build PO
po = pd.DataFrame([{
    "sku": sku,
    "on_hand": on_hand,
    "avg_next7": round(d_daily, 2),
    "ROP": round(rop, 1),
    "suggested_qty": qty
}])

po.to_csv("data/suggested_po.csv", index=False)
print("OK -> data/suggested_po.csv")