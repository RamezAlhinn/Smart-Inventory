import pandas as pd
from neuralprophet import NeuralProphet as Prophet

def forecast_prophet(sales_df: pd.DataFrame, horizon=14):
    """
    sales_df: DataFrame with columns ["date", "qty_sold"]
    horizon: days to forecast
    """
    df = sales_df.rename(columns={"date": "ds", "qty_sold": "y"})
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df, freq="D")

    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]