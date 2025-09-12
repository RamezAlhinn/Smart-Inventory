import streamlit as st
import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
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
    
    # Input widgets → user can select which SKU, store, lead time, and MOQ
    sku = st.text_input("SKU", value="MILK1")
    store = st.text_input("Store", value="S1")
    lead = st.number_input("Lead time (days)", 1, 30, 5)
    moq = st.number_input("Minimum Order Quantity", 1, 1000, 1)

    # Filter sales for the selected SKU & store
    s_df = sales[(sales["sku"]==sku) & (sales["store_id"]==store)][["date","qty_sold"]]
    
    if s_df.empty:
        st.warning("⚠️ No sales data found for this SKU/store.")
    else:
        # Convert sales into daily time series (fills missing days with 0s)
        series = to_daily(s_df)

        # Plot sales history
        st.line_chart(series)

        # Forecast next 7 days using moving average
        fcst = moving_avg_forecast(series, window=7, horizon=7)

        # Calculate average daily demand for next 7 days
        d_daily = fcst["yhat"].mean()

        # Calculate variability (standard deviation of last 28 days)
        sigma = series.tail(28).std() if len(series)>=2 else 0.0

        # Get current stock from stock.csv
        on_hand_row = stock[(stock["sku"]==sku) & (stock["store_id"]==store)]
        on_hand = int(on_hand_row["on_hand"].iloc[0]) if not on_hand_row.empty else 0

        # Run reorder calculation
        qty, rop, ss = suggest_order(d_daily, sigma, lead, on_hand, moq)

        # Create purchase order DataFrame
        po = pd.DataFrame([{
            "sku": sku,
            "on_hand": on_hand,
            "avg_next7": round(d_daily,2),
            "ROP": round(rop,1),
            "suggested_qty": qty
        }])

        # Show results in app
        st.subheader("📦 Suggested Purchase Order")
        st.dataframe(po)

        # Download button → let user export the PO as CSV
        st.download_button("⬇️ Download PO CSV", po.to_csv(index=False), "suggested_po.csv")