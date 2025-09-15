import pandas as pd
from prophet import Prophet

def forecast_prophet(df, horizon=14):
    """
    Forecast using Facebook Prophet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """

    # Add constraints: demand can't be < 0
    model = Prophet(
        yearly_seasonality=True,      # capture yearly cycles
        weekly_seasonality=True,      # capture weekly sales patterns
        daily_seasonality=False,      # daily seasonality usually not needed for sales
    )
    
    # Optional: add holidays or special events if you have them
    # model.add_country_holidays(country_name='Jordan')

    model.fit(df)

    # Create future dataframe
    future = model.make_future_dataframe(periods=horizon)

    forecast = model.predict(future)

    # Clamp predictions to >= 0
    forecast['yhat'] = forecast['yhat'].clip(lower=0)

    return forecast