import streamlit as st
import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from packages.core.forecasting.prophet_model import forecast_prophet
from packages.core.inventory.reorder import suggest_order

# --- Page setup ---
st.set_page_config(page_title="Smart Inventory Dashboard", layout="wide")
st.title("📊 Smart Inventory — Demo Dashboard")

# --- File upload ---
sales_file = st.file_uploader("Upload sales.csv", type=["csv"])
stock_file = st.file_uploader("Upload stock.csv", type=["csv"])

if sales_file and stock_file:
    sales = pd.read_csv(sales_file, parse_dates=["date"])
    stock = pd.read_csv(stock_file, parse_dates=["date"])
    
    # --- Filters ---
    available_stores = sales["store_id"].unique().tolist()
    available_categories = sales["category"].unique().tolist() if "category" in sales.columns else []

    store = st.selectbox("Select Store", ["All"] + available_stores)
    category = st.selectbox("Select Category", ["All"] + available_categories) if available_categories else "All"
    model_choice = st.selectbox("Forecast Model", ["Moving Average", "Prophet"])
    lead = st.number_input("Lead Time (days)", 1, 30, 5)
    moq = st.number_input("Minimum Order Quantity", 1, 1000, 1)

    # --- Filter data by store/category ---
    sales_filtered = sales.copy()
    if store != "All":
        sales_filtered = sales_filtered[sales_filtered["store_id"] == store]
    if category != "All" and "category" in sales_filtered.columns:
        sales_filtered = sales_filtered[sales_filtered["category"] == category]

    # --- Process each SKU ---
    results = []
    for sku in sales_filtered["sku"].unique():
        s_df = sales_filtered[sales_filtered["sku"] == sku][["date", "qty_sold"]]
        if s_df.empty:
            continue

        series = to_daily(s_df)

        # Forecast
        if model_choice == "Moving Average":
            fcst = moving_avg_forecast(series, window=7, horizon=7)
            d_daily = fcst["yhat"].mean()
        else:  # Prophet
            df = s_df.rename(columns={"date": "ds", "qty_sold": "y"})
            fcst = forecast_prophet(df, horizon=14)
            d_daily = fcst.tail(14)["yhat"].mean()

        # Variability
        sigma = series.tail(28).std() if len(series) >= 2 else 0.0

        # Current stock
        on_hand_row = stock[(stock["sku"] == sku) & (stock["store_id"].isin([store] if store != "All" else stock["store_id"].unique()))]
        on_hand = int(on_hand_row["on_hand"].iloc[0]) if not on_hand_row.empty else 0

        # Reorder calculation
        qty, rop, ss = suggest_order(d_daily, sigma, lead, on_hand, moq)

        results.append({
            "Product (SKU)": sku,
            "Store": store if store != "All" else "All Stores",
            "On Hand": on_hand,
            "Avg Daily Demand": round(d_daily, 0),
            "Reorder Point": round(rop, 0),
            "Suggested Order Qty": qty,
            "Status": "Critical" if on_hand < d_daily else ("Warning" if on_hand < rop else "Safe")
        })

    # --- Results table ---
    if results:
        df_results = pd.DataFrame(results)

        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("🛒 Total Products", len(df_results))
        col2.metric("🚨 Critical Stockouts", (df_results["Status"] == "Critical").sum())
        col3.metric("⚠️ Warnings", (df_results["Status"] == "Warning").sum())

        # Color-coding table
        def highlight_status(val):
            if val == "Critical":
                return "background-color: #ff4d4d; color: white"
            elif val == "Warning":
                return "background-color: #ffd633"
            else:
                return "background-color: #b3ffb3"

        st.subheader("📦 Suggested Orders for All Products")
        st.dataframe(df_results.style.applymap(highlight_status, subset=["Status"]))

        # Download button
        st.download_button("⬇️ Download Full Purchase Order CSV",
                           df_results.to_csv(index=False),
                           "purchase_order.csv")
    else:
        st.info("No products found with current filters.")