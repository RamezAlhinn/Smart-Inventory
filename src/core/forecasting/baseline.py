"""
baseline.py (Core Forecasting)

Purpose:
--------
Provides simple, lightweight baseline forecasting methods 
that are **domain-agnostic** and require minimal data. 
These models are used as fallbacks or benchmarks against 
more advanced approaches (e.g., Prophet, Croston, TSB).

Contents:
- to_daily(): Convert raw sales data into a continuous daily series.
- moving_avg_forecast(): Weighted moving average forecast with horizon.

These methods ensure the system always has a stable forecast, 
even with sparse or noisy data.
"""

import pandas as pd
import numpy as np


def to_daily(series_df: pd.DataFrame) -> pd.Series:
    """
    Convert transactional sales data to daily demand series.
    
    - Groups by date and sums quantities.
    - Reindexes to daily frequency, filling missing days with 0.
    - Ensures a non-empty series (returns 7 days of zeros if empty).
    """
    if series_df.empty:
        # Create a 7-day empty series to avoid crashes
        idx = pd.date_range(
            pd.Timestamp.today().normalize() - pd.Timedelta(days=6),
            periods=7,
            freq="D"
        )
        return pd.Series(0.0, index=idx)

    df = series_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    grouped = df.groupby("date", as_index=False)["qty_sold"].sum()
    s = (
        grouped.set_index("date")["qty_sold"]
        .astype(float)
        .asfreq("D", fill_value=0.0)
    )
    return s.clip(lower=0.0)


def moving_avg_forecast(series: pd.Series, window: int = 7, horizon: int = 7) -> pd.DataFrame:
    """
    Weighted moving average forecast.

    - Uses the last `window` days, with linearly increasing weights.
    - Produces a constant forecast for the next `horizon` days.
    - Enforces a minimum avg (0.1) to avoid total zero forecasts.

    Returns:
        DataFrame with ["date", "yhat"] for forecasted horizon.
    """
    series = series.astype(float).clip(lower=0.0)
    if len(series) == 0:
        avg = 0.1
    else:
        recent = series.tail(window).to_numpy()
        weights = np.arange(1, len(recent) + 1)
        avg = float(np.dot(recent, weights) / weights.sum())
        avg = max(round(avg, 2), 0.1)  # keep decimals, avoid zero

    future = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    return pd.DataFrame({"date": future, "yhat": [avg] * horizon})