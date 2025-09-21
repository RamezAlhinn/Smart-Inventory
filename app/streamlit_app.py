import sys, os
import streamlit as st
import pandas as pd

# --- Path setup (ensure src/ is visible) ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.forecasting.baseline import to_daily, moving_avg_forecast
from src.core.forecasting.prophet_model import forecast_prophet
from src.core.reorder import suggest_order
from src.domains import get_domain_module

# --- Load domain-specific plugin ---
uiconfig = get_domain_module("uiconfig")
policies = get_domain_module("policies")

# --- Page setup ---
st.set_page_config(page_title="Smart Inventory Dashboard", layout="wide")
st.title("📊 Smart Inventory — Demo Dashboard")

# --- File upload ---
sales_file = st.file_uploader("Upload sales.csv", type=["csv"])
stock_file = st.file_uploader("Upload stock.csv", type=["csv"])
products_file = st.file_uploader("Upload products.csv (optional)", type=["csv"])

if sales_file and stock_file:
    sales = pd.read_csv(sales_file, parse_dates=["date"])
    stock = pd.read_csv(stock_file, parse_dates=["date"])
    products = pd.read_csv(products_file) if products_file else None

    # --- Filters (delegated to domain UI if needed) ---
    store, categories = uiconfig.render_filters(sales)

    # Forecast model choice
    model_choice = st.selectbox(
        "Forecast Model",
        ["Moving Average (fast)", "AI Powered"]
    )

    # Horizon slider
    horizon = st.slider(
        "Forecast Horizon (days)",
        7,
        30,
        7 if model_choice == "AI Powered" else 14
    )

    lead = st.number_input("Lead Time (days)", 1, 30, 5)
    moq = st.number_input("Minimum Order Quantity", 1, 1000, 1)

    # --- Filter data ---
    sales_filtered = sales.copy()
    if store != "All":
        sales_filtered = sales_filtered[sales_filtered["store_id"] == store]
    if categories:
        sales_filtered = sales_filtered[sales_filtered["category"].isin(categories)]

    # --- Process each SKU ---
    results = []
    for sku in sales_filtered["sku"].unique():
        s_df = sales_filtered[sales_filtered["sku"] == sku][["date", "qty_sold"]]
        if s_df.empty:
            continue

        series = to_daily(s_df)

        # Forecast
        if model_choice == "Moving Average (fast)":
            fcst = moving_avg_forecast(series, window=7, horizon=horizon)
            d_daily = max(fcst["yhat"].mean(), 0)
        else:  # Prophet
            df = s_df.rename(columns={"date": "ds", "qty_sold": "y"})
            fcst = forecast_prophet(df, horizon=horizon)
            d_daily = fcst.tail(horizon)["yhat"].mean()

        # Variability
        sigma = series.tail(28).std() if len(series) >= 2 else 0.0

        # Stock
        on_hand_row = stock[
            (stock["sku"] == sku) &
            (stock["store_id"].isin([store] if store != "All" else stock["store_id"].unique()))
        ]
        on_hand = int(on_hand_row["on_hand"].iloc[0]) if not on_hand_row.empty else 0

        # 1. Resolve product info first
        prod_name, prod_cat, supplier, unit_cost = uiconfig.resolve_product_info(
            sku, products, sales_filtered
        )

        # Reorder (domain policy may override core suggest_order)
        result = policies.get_reorder_qty(
            sku=sku,
            d_daily=d_daily,
            sigma=sigma,
            lead=lead,
            on_hand=on_hand,
            moq=moq,
            category=prod_cat
        )

        qty = result["qty"]
        rop = result["rop"]
        ss = result["safety_stock"]

        # Product info (if provided)
        prod_name, prod_cat, supplier, unit_cost = uiconfig.resolve_product_info(sku, products, sales_filtered)

        # Expiry risk check (delegated to plugin)
        expiry_flag = uiconfig.check_expiry_risk(prod_cat, sku, products)

        # Cost estimation
        order_cost = qty * unit_cost

        # Status (critical, warning, safe)
        status = uiconfig.evaluate_status(on_hand, d_daily, rop)

        results.append({
            "Product": prod_name,
            "SKU": sku,
            "Category": prod_cat,
            "Store": store if store != "All" else "All Stores",
            "On Hand": int(on_hand),
            "Avg Daily Demand": round(d_daily, 0),
            "Reorder Point": round(rop, 0),
            "Suggested Order Qty": int(qty),
            "Unit Cost (JOD)": unit_cost,
            "Order Cost (JOD)": round(order_cost, 2),
            "Expiry Risk": expiry_flag,
            "Status": status,
            "supplier": supplier
        })

    # --- Results ---
    if results:
        uiconfig.render_results(results)
    else:
        st.info("No products found with current filters.")