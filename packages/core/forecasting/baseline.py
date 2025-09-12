import pandas as pd

# Convert sales data into a daily time series (fills missing days with 0).
def to_daily(series_df: pd.DataFrame) -> pd.Series:
    s = (series_df
         .rename(columns={"date":"date","qty_sold":"y"})
         .set_index(pd.to_datetime(series_df["date"]))["y"]
         .asfreq("D", fill_value=0))
    return s

# Forecast using a simple moving average:
# - Look at the last N days (default 7)
# - Predict the same average for the next "horizon" days
def moving_avg_forecast(series: pd.Series, window=7, horizon=7) -> pd.DataFrame:
    last_ma = series.rolling(window=window, min_periods=1).mean().iloc[-1]
    future = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    return pd.DataFrame({"date": future, "yhat": [max(0, round(last_ma))]*horizon})