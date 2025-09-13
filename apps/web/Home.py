import sys, os
# Fix path so Streamlit Cloud can find packages/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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
products_file = st.file_uploader("Upload products.csv (optional)", type=["csv"])

if sales_file and stock_file:
    sales = pd.read_csv(sales_file, parse_dates=["date"])
    stock = pd.read_csv(stock_file, parse_dates=["date"])
    products = pd.read_csv(products_file) if products_file else None

    # --- Filters ---
    available_stores = sales["store_id"].unique().tolist()
    available_categories = sales["category"].unique().tolist() if "category" in sales.columns else []

    store = st.selectbox("Select Store", ["All"] + available_stores)
    categories = st.multiselect("Select Categories", available_categories, default=available_categories)

    # Forecast model choice
    model_choice = st.selectbox(
        "Forecast Model",
        ["Moving Average (fast)", "Prophet (slower)"]
    )

    # Horizon slider (shorter for Prophet)
    if model_choice == "Prophet (slower)":
        horizon = st.slider("Forecast Horizon (days)", 7, 14, 7)
    else:
        horizon = st.slider("Forecast Horizon (days)", 7, 30, 14)

    lead = st.number_input("Lead Time (days)", 1, 30, 5)
    moq = st.number_input("Minimum Order Quantity", 1, 1000, 1)

    # --- Filter data ---
    sales_filtered = sales.copy()
    if store != "All":
        sales_filtered = sales_filtered[sales_filtered["store_id"] == store]
    if categories:
        sales_filtered = sales_filtered[sales_filtered["category"].isin(categories)]

    # --- Process each SKU --
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

        # Reorder
        qty, rop, ss = suggest_order(d_daily, sigma, lead, on_hand, moq)

        # Product info (if provided)
        prod_name = (
            products.loc[products["sku"] == sku, "name"].values[0]
            if products is not None and sku in products["sku"].values
            else sku
        )
        prod_cat = (
            products.loc[products["sku"] == sku, "category"].values[0]
            if products is not None and sku in products["sku"].values
            else (sales_filtered[sales_filtered["sku"] == sku]["category"].iloc[0]
                  if "category" in sales_filtered.columns else "")
        )
        supplier = (
            products.loc[products["sku"] == sku, "supplier"].values[0]
            if products is not None and sku in products["sku"].values
            else "Unknown"
        )
        unit_cost = (
            float(products.loc[products["sku"] == sku, "unit_cost"].values[0])
            if products is not None and sku in products["sku"].values
            else 1.0
        )

        # Expiry risk
        expiry_flag = "⚠️ Expiry Risk" if prod_cat in ["Dairy", "Bakery", "Produce"] else "OK"

        # Cost estimation
        order_cost = qty * unit_cost

        # Status
        if on_hand < d_daily:
            status = "🟥 Critical"
        elif on_hand < rop:
            status = "🟨 Warning"
        else:
            status = "🟩 Safe"

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

    # --- Results table ---
    if results:
        df_results = pd.DataFrame(results)

        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🛒 Total Products", len(df_results))
        col2.metric("🚨 Critical", (df_results["Status"] == "🟥 Critical").sum())
        col3.metric("⚠️ Warnings", (df_results["Status"] == "🟨 Warning").sum())
        col4.metric("💰 Total Order Cost", f"{df_results['Order Cost (JOD)'].sum()} JOD")

        # Sort table: Critical > Warning > Safe
        status_order = {"🟥 Critical": 0, "🟨 Warning": 1, "🟩 Safe": 2}
        df_results["status_sort"] = df_results["Status"].map(status_order)
        df_results = df_results.sort_values(by="status_sort").drop(columns=["status_sort"])

        # Show results
        st.subheader("📦 Suggested Orders for All Products")
        st.dataframe(df_results)

        # Download all products
        st.download_button("⬇️ Download Full Purchase Order CSV",
                           df_results.to_csv(index=False),
                           "purchase_order.csv")

        # Group by Supplier (with expanders)
        if "supplier" in df_results.columns:
            st.subheader("📑 Purchase Orders by Supplier")
            grouped = df_results.groupby("supplier")
            for supplier, df_group in grouped:
                with st.expander(f"🏢 {supplier} — {len(df_group)} products", expanded=False):
                    st.dataframe(df_group[[
                        "Product", "SKU", "Category", "Store",
                        "On Hand", "Avg Daily Demand", "Reorder Point",
                        "Suggested Order Qty", "Unit Cost (JOD)", "Order Cost (JOD)",
                        "Expiry Risk", "Status"
                    ]])
                    st.download_button(
                        f"⬇️ Download PO for {supplier}",
                        df_group.to_csv(index=False),
                        f"PO_{supplier.replace(' ', '_')}.csv"
                    )

    else:
        st.info("No products found with current filters.")