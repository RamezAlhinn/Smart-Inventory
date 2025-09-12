import streamlit as st
import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from packages.core.forecasting.prophet_model import forecast_prophet
from packages.core.inventory.reorder import suggest_order

# Title of the web app
st.title("📊 Smart Inventory — Demo")

# File uploaders → allow user to upload sales + stock CSVs
sales_file = st.file_uploader("Upload sales.csv", type=["csv"])
stock_file = st.file_uploader("Upload stock.csv", type=["csv"])

# Only run logic if both files are uploaded
if sales_file and stock_file:
    # Load uploaded CSVs into pandas DataFrames
    sales = pd.read_csv(sales_file, parse_dates=["date"])
    stock = pd.read_csv(stock_file, parse_dates=["date"])
    
    # --- Dropdowns for SKU and Store ---
    available_stores = sales["store_id"].unique().tolist()
    available_skus = sales["sku"].unique().tolist()
    
    store = st.selectbox("Select Store", available_stores, index=0)
    sku = st.selectbox("Select Product (SKU)", available_skus, index=0)

    # Lead time and MOQ inputs
    lead = st.number_input("Lead time (days)", 1, 30, 5)
    moq = st.number_input("Minimum Order Quantity", 1, 1000, 1)

    # Forecast model choice
    model_choice = st.selectbox("Forecast model", ["Moving Average", "Prophet"])

    # Filter sales for the selected SKU & store
    s_df = sales[(sales["sku"]==sku) & (sales["store_id"]==store)][["date","qty_sold"]]
    
    if s_df.empty:
        st.warning("⚠️ No sales data found for this product in this store.")
    else:
        # Convert sales into daily time series (fills missing days with 0s)
        series = to_daily(s_df)

        # Plot sales history
        st.subheader("📈 Sales History")
        st.line_chart(series)

        # --- Forecasting ---
        if model_choice == "Moving Average":
            # Simple baseline forecast
            fcst = moving_avg_forecast(series, window=7, horizon=7)
            st.subheader("🔮 Forecast (Moving Average)")
            st.line_chart(fcst.set_index("date")["yhat"].rename("Expected Demand"))
            d_daily = fcst["yhat"].mean()

        elif model_choice == "Prophet":
            # AI forecast using Prophet
            df = s_df.rename(columns={"date": "ds", "qty_sold": "y"})
            fcst = forecast_prophet(df, horizon=14)
            # Rename columns for user-friendly labels
            fcst = fcst.rename(columns={
                "yhat": "Expected Demand",
                "yhat_lower": "Lower Range",
                "yhat_upper": "Upper Range"
            })
            st.subheader("🤖 Forecast (Prophet)")
            st.line_chart(fcst.set_index("ds")[["Expected Demand", "Lower Range", "Upper Range"]])
            d_daily = fcst.tail(14)["Expected Demand"].mean()

        # --- Inventory Logic ---
        sigma = series.tail(28).std() if len(series)>=2 else 0.0

        # Get current stock from stock.csv
        on_hand_row = stock[(stock["sku"]==sku) & (stock["store_id"]==store)]
        on_hand = int(on_hand_row["on_hand"].iloc[0]) if not on_hand_row.empty else 0

        # Run reorder calculation
        qty, rop, ss = suggest_order(d_daily, sigma, lead, on_hand, moq)

        # Create purchase order DataFrame
        po = pd.DataFrame([{
            "Product (SKU)": sku,
            "Store": store,
            "On Hand": on_hand,
            "Avg Next Days": round(d_daily,2),
            "Reorder Point": round(rop,1),
            "Suggested Order Qty": qty
        }])

        # Show results in app
        st.subheader("📦 Suggested Purchase Order")
        st.dataframe(po)

        # Download button → let user export the PO as CSV
        st.download_button("⬇️ Download PO CSV", po.to_csv(index=False), "suggested_po.csv")