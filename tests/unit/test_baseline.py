"""
test_baseline.py

Purpose:
--------
Unit tests for baseline forecasting functions:
- to_daily(): ensures daily aggregation and gap filling works.
- moving_avg_forecast(): ensures forecasts behave as expected.

These tests validate correctness, edge cases, and robustness.
"""

import pandas as pd
import numpy as np
import pytest
from src.core.forecasting import to_daily, moving_avg_forecast


# ---------- Tests for to_daily ----------
def test_to_daily_basic():
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "qty_sold": [10, 20]})
    s = to_daily(df)
    assert len(s) == 2
    assert s.iloc[0] == 10
    assert s.iloc[1] == 20


def test_to_daily_fills_missing_days():
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-03"], "qty_sold": [5, 15]})
    s = to_daily(df)
    # Should fill 2025-01-02 with 0
    assert s.loc["2025-01-02"] == 0


def test_to_daily_empty_input():
    df = pd.DataFrame(columns=["date", "qty_sold"])
    s = to_daily(df)
    assert (s == 0).all()
    assert len(s) == 7  # should return a 7-day empty series


def test_to_daily_clips_negatives():
    df = pd.DataFrame({"date": ["2025-01-01"], "qty_sold": [-5]})
    s = to_daily(df)
    assert s.iloc[0] == 0.0  # clipped to zero


# ---------- Tests for moving_avg_forecast ----------
def test_moving_avg_forecast_basic():
    s = pd.Series([10, 20, 30], index=pd.date_range("2025-01-01", periods=3))
    fc = moving_avg_forecast(s, window=2, horizon=3)
    assert len(fc) == 3
    assert all(fc["yhat"] >= 0)
    assert pd.api.types.is_datetime64_dtype(fc["date"])


def test_moving_avg_forecast_short_series():
    s = pd.Series([100], index=pd.date_range("2025-01-01", periods=1))
    fc = moving_avg_forecast(s, window=7, horizon=5)
    # Should still return a constant positive forecast
    assert len(fc) == 5
    assert (fc["yhat"] == fc["yhat"].iloc[0]).all()
    assert fc["yhat"].iloc[0] >= 0.1  # respects minimum floor


def test_moving_avg_forecast_all_zeros():
    s = pd.Series([0, 0, 0], index=pd.date_range("2025-01-01", periods=3))
    fc = moving_avg_forecast(s, window=2, horizon=3)
    assert all(fc["yhat"] == 0.1)  # enforced floor for zeros


def test_moving_avg_forecast_horizon_longer():
    s = pd.Series([5, 10, 15], index=pd.date_range("2025-01-01", periods=3))
    fc = moving_avg_forecast(s, window=2, horizon=10)
    assert len(fc) == 10
    # Dates must be consecutive daily steps
    assert (fc["date"].diff().dropna() == pd.Timedelta(days=1)).all()


# ---------- Property-based tests ----------
def test_forecast_non_negative_and_monotonic_dates():
    s = pd.Series(
        np.random.randint(0, 50, size=30),
        index=pd.date_range("2025-01-01", periods=30),
    )
    fc = moving_avg_forecast(s, window=7, horizon=14)
    assert (fc["yhat"] >= 0).all()
    assert fc["date"].is_monotonic_increasing