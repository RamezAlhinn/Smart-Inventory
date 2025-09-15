import pandas as pd
import numpy as np

def to_daily(series_df: pd.DataFrame) -> pd.Series:
    """Group sales to daily frequency and fill gaps with 0."""
    if series_df.empty:
        # create a 7-day empty series to avoid crashes
        idx = pd.date_range(pd.Timestamp.today().normalize() - pd.Timedelta(days=6), periods=7, freq="D")
        return pd.Series(0.0, index=idx)

    df = series_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    grouped = df.groupby("date", as_index=False)["qty_sold"].sum()
    s = (grouped.set_index("date")["qty_sold"]
         .astype(float)
         .asfreq("D", fill_value=0.0))
    return s.clip(lower=0.0)

def moving_avg_forecast(series: pd.Series, window: int = 7, horizon: int = 7) -> pd.DataFrame:
    """Simple, robust moving-average forecast (weighted, non-zero)."""
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