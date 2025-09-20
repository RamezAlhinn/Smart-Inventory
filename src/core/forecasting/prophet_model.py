"""
prophet_model.py (Core Forecasting)

Purpose:
--------
Provides a Prophet-based forecasting model for demand prediction. 
This is a more advanced alternative to the baseline moving-average 
approach, capturing seasonality and trend patterns.

Contents:
- forecast_prophet(): Fit and forecast daily demand using Prophet.

Usage:
- Input DataFrame must have columns ["ds", "y"] where:
  - "ds" = date (datetime)
  - "y" = demand (numeric, non-negative)
- Returns a full Prophet forecast DataFrame with columns including 
  ["ds", "yhat", "yhat_lower", "yhat_upper"].
"""

import pandas as pd
from prophet import Prophet


def forecast_prophet(df: pd.DataFrame, horizon: int = 14) -> pd.DataFrame:
    """
    Forecast daily demand using Prophet.

    Args:
        df: DataFrame with columns ["ds", "y"].
            - "ds" must be datetime-like.
            - "y" is demand (non-negative).
        horizon: Number of future days to forecast.

    Returns:
        Prophet forecast DataFrame with at least ["ds", "yhat"].
    """
    # Ensure no negatives in input
    df = df.copy()
    df["y"] = df["y"].clip(lower=0)

    # Configure Prophet with relevant seasonalities
    model = Prophet(
        yearly_seasonality=True,     # yearly trend (safe to keep)
        weekly_seasonality=True,     # weekly demand cycles
        daily_seasonality=False,     # daily not needed for sales
        seasonality_mode="multiplicative",  # handles growth/decline better
    )

    # Add monthly seasonality manually (approx 30.5 days)
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    # Fit model
    model.fit(df)

    # Forecast horizon
    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future)

    # Ensure non-negative predictions
    forecast["yhat"] = forecast["yhat"].clip(lower=0)

    return forecast