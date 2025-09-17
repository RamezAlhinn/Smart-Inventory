import pandas as pd
from packages.core.forecasting.baseline import moving_avg_forecast, to_daily

def test_to_daily():
    df = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02", "2025-01-02"],
        "qty_sold": [10, 5, 7]
    })
    s = to_daily(df)
    # Expect 10 on first day, 12 on second
    assert s.loc["2025-01-01"] == 10
    assert s.loc["2025-01-02"] == 12

def test_moving_avg_forecast():
    s = pd.Series([10, 20, 30], index=pd.date_range("2025-01-01", periods=3))
    forecast = moving_avg_forecast(s, window=3, horizon=3)
    # Weighted average = (10*1 + 20*2 + 30*3) / (1+2+3) = 23.33
    assert all(forecast["yhat"] == 23.33)
    assert len(forecast) == 3