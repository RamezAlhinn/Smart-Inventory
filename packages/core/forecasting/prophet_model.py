import pandas as pd
from prophet import Prophet

def forecast_prophet(df, horizon=14):
    """
    Forecast using Facebook Prophet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """
    model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    model.fit(df)

    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)

    # Clip negative predictions to 0
    forecast["yhat"] = forecast["yhat"].clip(lower=0)

    return forecast