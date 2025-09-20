# Streamlit config for pharmacy
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def render_filters(sales_df: pd.DataFrame):
    """Render pharmacy-specific filters (e.g., category = therapeutic class)."""
    available_categories = (
        sales_df["category"].unique().tolist()
        if "category" in sales_df.columns else []
    )

    categories = st.multiselect(
        "Select Therapeutic Classes",
        available_categories,
        default=available_categories
    )
    return "All", categories  # placeholder store handling (pharmacies often single location)


def resolve_product_info(sku, products_df, sales_df):
    """Get drug name, therapeutic class, supplier, and cost (with fallbacks)."""
    if products_df is not None:
        prod_row = products_df.loc[products_df["sku"] == sku]
        if not prod_row.empty:
            prod_name = prod_row["name"].values[0]
            prod_class = prod_row["category"].values[0] if "category" in prod_row else ""
            supplier = prod_row["supplier"].values[0] if "supplier" in prod_row else "Unknown"
            unit_cost = float(prod_row["unit_cost"].values[0]) if "unit_cost" in prod_row else 1.0
            return prod_name, prod_class, supplier, unit_cost

    # Fallbacks
    prod_name = sku
    prod_class = (
        sales_df[sales_df["sku"] == sku]["category"].iloc[0]
        if "category" in sales_df.columns else ""
    )
    supplier = "Unknown"
    unit_cost = 1.0
    return prod_name, prod_class, supplier, unit_cost


def check_expiry_risk(category, sku, products_df):
    """
    Pharmacy expiry risk check.
    - If products_df contains an expiry column, flag soon-to-expire lots.
    - Otherwise fall back to category-based heuristic.
    """
    if products_df is not None and "expiry" in products_df.columns:
        row = products_df.loc[products_df["sku"] == sku]
        if not row.empty:
            expiry = pd.to_datetime(row["expiry"].values[0])
            days_left = (expiry - datetime.today()).days
            if days_left < 30:
                return f"⚠️ Expiry in {days_left} days"
    # Fallback
    if category in ["Antibiotics", "Vaccines"]:
        return "⚠️ Expiry Sensitive"
    return "OK"


def evaluate_status(on_hand, avg_daily_demand, reorder_point):
    """
    Pharmacy stock status evaluation.
    - Stricter thresholds than supermarket (low stock-out tolerance).
    """
    if on_hand < avg_daily_demand:
        return "🟥 Critical"
    elif on_hand < reorder_point * 1.2:  # stricter buffer
        return "🟨 Warning"
    else:
        return "🟩 Safe"


def render_results(results: list[dict]):
    """Render KPIs and tables for pharmacy results with compliance info."""
    df_results = pd.DataFrame(results)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💊 Total SKUs", len(df_results))
    col2.metric("🚨 Critical", (df_results["Status"] == "🟥 Critical").sum())
    col3.metric("⚠️ Warnings", (df_results["Status"] == "🟨 Warning").sum())
    col4.metric("💰 Total Order Cost", f"{df_results['Order Cost (JOD)'].sum()} JOD")

    # Sort: Critical > Warning > Safe
    status_order = {"🟥 Critical": 0, "🟨 Warning": 1, "🟩 Safe": 2}
    df_results["status_sort"] = df_results["Status"].map(status_order)
    df_results = df_results.sort_values(by="status_sort").drop(columns=["status_sort"])

    # Compliance annotations
    if "Category" in df_results.columns:
        df_results["Compliance Flag"] = df_results["Category"].apply(
            lambda c: "Controlled Drug" if c in ["Opioids", "Narcotics"] else "Standard"
        )

    # Results table
    st.subheader("📦 Suggested Orders for Pharmacy SKUs")
    st.dataframe(df_results)

    # Download full PO
    st.download_button("⬇️ Download Full Purchase Order CSV",
                       df_results.to_csv(index=False),
                       "purchase_order.csv")

    # Group by Supplier
    if "supplier" in df_results.columns:
        st.subheader("📑 Purchase Orders by Supplier")
        grouped = df_results.groupby("supplier")
        for supplier, df_group in grouped:
            with st.expander(f"🏢 {supplier} — {len(df_group)} SKUs", expanded=False):
                st.dataframe(df_group[[
                    "Product", "SKU", "Category", "Store",
                    "On Hand", "Avg Daily Demand", "Reorder Point",
                    "Suggested Order Qty", "Unit Cost (JOD)", "Order Cost (JOD)",
                    "Expiry Risk", "Status", "Compliance Flag"
                ]])
                st.download_button(
                    f"⬇️ Download PO for {supplier}",
                    df_group.to_csv(index=False),
                    f"PO_{supplier.replace(' ', '_')}.csv"
                )