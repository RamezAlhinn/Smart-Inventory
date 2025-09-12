import pandas as pd
from neuralprophet import NeuralProphet

def forecast_prophet(df, horizon=14):
    """
    Forecast using NeuralProphet.
    df: must have columns ["ds", "y"]
    horizon: number of future days to forecast
    """
    model = NeuralProphet()
    model.fit(df, freq="D")
    
    future = model.make_future_dataframe(df, periods=horizon)
    forecast = model.predict(future)
    return forecast