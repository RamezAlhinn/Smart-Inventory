"""
run_demo.py

Purpose:
--------
Headless demo script for Smart-Inventory.
Runs the core pipeline (sales → forecast → reorder → purchase order CSV) 
without Streamlit, for quick smoke tests or CI/CD verification.

Usage:
    python scripts/run_demo.py

Output:
    - data/suggested_po.csv
"""

import pandas as pd
from src.core.forecasting.baseline import to_daily, moving_avg_forecast
from src.core.forecasting.prophet_model import forecast_prophet
from src.core.reorder import suggest_order

# Config (demo SKU + lead time)
SKU = "MILK1"
STORE = "S1"
LEAD_TIME = 5
MOQ = 1

# --- Load sales + stock data ---
sales = pd.read_csv("data/sales.csv")
stock = pd.read_csv("data/stock.csv")

s_df = sales[(sales["sku"] == SKU) & (sales["store_id"] == STORE)][["date", "qty_sold"]]

# --- Convert to daily demand series ---
series = to_daily(s_df)

# --- Prepare Prophet input ---
df_prophet = series.reset_index().rename(columns={"date": "ds", "qty_sold": "y"})

# --- Forecast demand ---
try:
    fcst = forecast_prophet(df_prophet, horizon=7)
    fcst["yhat"] = fcst["yhat"].clip(lower=0)
    d_daily = fcst["yhat"].mean()
except Exception:
    fcst = moving_avg_forecast(series, window=7, horizon=7)
    d_daily = fcst["yhat"].mean()

# --- Variability ---
sigma = max(series.tail(28).std(), 0.1)

# --- Current stock ---
on_hand = int(stock[(stock["sku"] == SKU) & (stock["store_id"] == STORE)]["on_hand"].iloc[0])

# --- Reorder calculation ---
result = suggest_order(
    daily_demand=d_daily,
    sigma=sigma,
    lead=LEAD_TIME,
    on_hand=on_hand,
    moq=MOQ,
)

# --- Build purchase order ---
po = pd.DataFrame([{
    "sku": SKU,
    "store": STORE,
    "on_hand": on_hand,
    "avg_next7": round(d_daily, 2),
    "ROP": round(result["rop"], 1),
    "safety_stock": round(result["safety_stock"], 1),
    "suggested_qty": result["qty"],
}])

po.to_csv("data/suggested_po.csv", index=False)
print("✅ Purchase order written to data/suggested_po.csv")