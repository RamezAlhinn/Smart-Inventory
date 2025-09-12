import pandas as pd
from prophet import Prophet

def forecast_prophet(df, horizon=14):
    """
    Forecast using Facebook Prophet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    return forecast