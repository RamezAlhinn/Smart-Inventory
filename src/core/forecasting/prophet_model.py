import pandas as pd
from prophet import Prophet

def forecast_prophet(df, horizon=14):
    """
    Forecast daily demand using Prophet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """
    # Ensure no negatives in input
    df["y"] = df["y"].clip(lower=0)

    # Configure Prophet with useful seasonality
    model = Prophet(
        yearly_seasonality=True,   # yearly trend (safe to keep)
        weekly_seasonality=True,   # weekly demand cycles
        daily_seasonality=False,   # daily not needed for sales
        seasonality_mode="multiplicative"  # reacts better to growth/decline
    )
    
    # Add monthly seasonality manually
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    # Fit
    model.fit(df)

    # Forecast horizon
    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future)

    # Clip negatives
    forecast["yhat"] = forecast["yhat"].clip(lower=0)

    return forecast