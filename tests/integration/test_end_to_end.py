import pandas as pd
from packages.core.forecasting.baseline import to_daily, moving_avg_forecast
from src.core.reorder.reorder import suggest_order

def test_end_to_end_pipeline():
    # 1. Fake sales data
    sales = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=5),
        "qty_sold": [10, 15, 20, 25, 30],
    })

    # 2. Convert to daily
    daily_series = to_daily(sales)
    assert not daily_series.empty
    assert all(daily_series >= 0)

    # 3. Forecast demand
    forecast = moving_avg_forecast(daily_series, window=3, horizon=3)
    assert "yhat" in forecast.columns
    assert all(forecast["yhat"] >= 0)

    # 4. Reorder suggestion
    avg_demand = forecast["yhat"].mean()
    qty, rop, ss = suggest_order(
        daily_demand=avg_demand,
        sigma=2,
        lead=3,
        on_hand=10,
        moq=5
    )

    # 5. Integration checks
    assert isinstance(qty, int)
    assert qty % 5 == 0  # respects MOQ
    assert rop > 0

def test_integration_with_csvs():
    sales = pd.read_csv("data/sales_demo.csv")
    stock = pd.read_csv("data/stock_demo.csv")

    # Pick one SKU
    sku_sales = sales[sales["sku"] == "MILK1"]

    # Run pipeline
    daily_series = to_daily(sku_sales)
    forecast = moving_avg_forecast(daily_series, window=7, horizon=7)

    avg_demand = forecast["yhat"].mean()
    stock_on_hand = stock.loc[stock["sku"] == "MILK1", "on_hand"].iloc[0]

    qty, rop, ss = suggest_order(
        daily_demand=avg_demand,
        sigma=2,
        lead=3,
        on_hand=stock_on_hand,
        moq=5
    )

    # Assertions
    assert isinstance(qty, int)
    assert qty >= 0
    assert rop > 0