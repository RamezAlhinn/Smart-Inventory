import pandas as pd
from prophet import Prophet

def forecast_prophet(df, horizon=14):
    """
    Forecast using Facebook Prophet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """
    # Ensure df is valid
    df = df.dropna().copy()
    if df["y"].nunique() <= 1:
        raise ValueError("Not enough variation in data for forecasting")

    model = Prophet(
        daily_seasonality=True,
        yearly_seasonality=False,
        weekly_seasonality=True,
    )

    # More stable optimization
    try:
        model.fit(df)
    except RuntimeError:
        # Retry with smaller iterations
        model = Prophet(daily_seasonality=True, weekly_seasonality=True)
        model.fit(df, iter=2000)

    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    return forecast