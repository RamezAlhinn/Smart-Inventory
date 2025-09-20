"""
forecasting (Core Module)

Purpose:
--------
Provides forecasting models (baseline, Prophet, etc.) 
for demand prediction in Smart-Inventory.
"""

from .baseline import to_daily, moving_avg_forecast
from .prophet_model import forecast_prophet

__all__ = ["to_daily", "moving_avg_forecast", "forecast_prophet"]
