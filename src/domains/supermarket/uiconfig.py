# src/domains/supermarket/uiconfig.py
import streamlit as st
import pandas as pd


def render_filters(sales_df: pd.DataFrame):
    """Render store and category filters for supermarkets."""
    available_stores = sales_df["store_id"].unique().tolist()
    available_categories = (
        sales_df["category"].unique().tolist()
        if "category" in sales_df.columns else []
    )

    store = st.selectbox("Select Store", ["All"] + available_stores)
    categories = st.multiselect("Select Categories", available_categories, default=available_categories)
    return store, categories


def resolve_product_info(sku, products_df, sales_df):
    """Get product name, category, supplier, and cost (with fallbacks)."""
    if products_df is not None:
        prod_row = products_df.loc[products_df["sku"] == sku]
        if not prod_row.empty:
            prod_name = prod_row["name"].values[0]
            prod_cat = prod_row["category"].values[0] if "category" in prod_row else ""
            supplier = prod_row["supplier"].values[0] if "supplier" in prod_row else "Unknown"
            unit_cost = float(prod_row["unit_cost"].values[0]) if "unit_cost" in prod_row else 1.0
            return prod_name, prod_cat, supplier, unit_cost

    # Fallbacks if no product file or missing fields
    prod_name = sku
    prod_cat = (
        sales_df[sales_df["sku"] == sku]["category"].iloc[0]
        if "category" in sales_df.columns else ""
    )
    supplier = "Unknown"
    unit_cost = 1.0
    return prod_name, prod_cat, supplier, unit_cost


def check_expiry_risk(category, sku, products_df):
    """Flag expiry-sensitive categories (hardcoded for supermarkets)."""
    if category in ["Dairy", "Bakery", "Produce"]:
        return "⚠️ Expiry Risk"
    return "OK"


def evaluate_status(on_hand, avg_daily_demand, reorder_point):
    """Return traffic-light stock status."""
    if on_hand < avg_daily_demand:
        return "🟥 Critical"
    elif on_hand < reorder_point:
        return "🟨 Warning"
    else:
        return "🟩 Safe"


def render_results(results: list[dict]):
    """Render KPIs and tables for supermarket results."""
    df_results = pd.DataFrame(results)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🛒 Total Products", len(df_results))
    col2.metric("🚨 Critical", (df_results["Status"] == "🟥 Critical").sum())
    col3.metric("⚠️ Warnings", (df_results["Status"] == "🟨 Warning").sum())
    col4.metric("💰 Total Order Cost", f"{df_results['Order Cost (JOD)'].sum()} JOD")

    # Sort: Critical > Warning > Safe
    status_order = {"🟥 Critical": 0, "🟨 Warning": 1, "🟩 Safe": 2}
    df_results["status_sort"] = df_results["Status"].map(status_order)
    df_results = df_results.sort_values(by="status_sort").drop(columns=["status_sort"])

    # Results table
    st.subheader("📦 Suggested Orders for All Products")
    st.dataframe(df_results)

    # Download all products
    st.download_button("⬇️ Download Full Purchase Order CSV",
                       df_results.to_csv(index=False),
                       "purchase_order.csv")

    # Grouped by supplier
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