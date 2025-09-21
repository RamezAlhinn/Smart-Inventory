"""
test_end_to_end.py

Purpose:
--------
End-to-end integration tests for Smart-Inventory.
Covers both Supermarket and Pharmacy domains by running the pipeline:
    sales.csv → forecast → reorder → policy → results

Uses demo CSVs stored in data/Supermarket and data/Pharmacy.
"""

import pandas as pd
import pytest
from src.core.forecasting import to_daily, moving_avg_forecast
from src.domains import get_domain_module


# ------------------------------
# Parametrized Integration Tests
# ------------------------------
@pytest.mark.parametrize(
    "domain, sales_file, stock_file, products_file, sku",
    [
        (
            "supermarket",
            "data/Supermarket/sales_demo.csv",
            "data/Supermarket/stock_demo.csv",
            "data/Supermarket/products_demo.csv",
            "MILK1",
        ),
        (
            "pharmacy",
            "data/Pharmacy/sales_pharmacy.csv",
            "data/Pharmacy/stock_pharmacy.csv",
            "data/Pharmacy/products_pharmacy.csv",
            "INSULIN1",
        ),
    ],
)
def test_end_to_end_pipeline(monkeypatch, domain, sales_file, stock_file, products_file, sku):
    """
    Run a full forecast + reorder pipeline for both supermarket and pharmacy.
    Ensures results are valid and respect domain-specific policies.
    """
    # Force correct domain
    monkeypatch.setenv("DOMAIN", domain)

    # Load domain-specific policies
    policies = get_domain_module("policies")

    # Load CSVs
    sales = pd.read_csv(sales_file)
    stock = pd.read_csv(stock_file)
    products = pd.read_csv(products_file)

    # Pick one SKU
    sku_sales = sales[sales["sku"] == sku]
    assert not sku_sales.empty, f"No sales data for {sku} in {domain}"

    # 1. Convert to daily demand series
    daily_series = to_daily(sku_sales)
    assert not daily_series.empty

    # 2. Forecast demand
    forecast = moving_avg_forecast(daily_series, window=7, horizon=7)
    assert "yhat" in forecast.columns
    assert all(forecast["yhat"] >= 0)

    avg_demand = forecast["yhat"].mean()

    # 3. Get stock on hand + category
    stock_on_hand = stock.loc[stock["sku"] == sku, "on_hand"].iloc[0]
    category = products.loc[products["sku"] == sku, "category"].iloc[0]

    # 4. Run reorder with domain policies
    result = policies.get_reorder_qty(
        sku=sku,
        d_daily=avg_demand,
        sigma=2,
        lead=3,
        on_hand=stock_on_hand,
        moq=5,
        category=category,
    )

    # 5. Assertions
    assert isinstance(result, dict)
    assert result["qty"] >= 0
    assert result["rop"] > 0
    assert "safety_stock" in result

    # Extra pharmacy-specific assertion
    if domain == "pharmacy" and category == "Insulin":
        # Insulin should almost never have qty=0 in reorder suggestions
        assert result["qty"] > 0