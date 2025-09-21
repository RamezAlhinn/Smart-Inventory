"""
test_reorder.py

Purpose:
--------
Unit tests for core reorder logic (suggest_order).
Validates that reorder calculations behave correctly under
different scenarios (no need, MOQ rounding, high variability, etc.).
"""

import pytest
from src.core.reorder import suggest_order


def test_suggest_order_no_need():
    result = suggest_order(daily_demand=5, sigma=1, lead=2, on_hand=20, moq=1)
    assert result["qty"] == 0  # enough stock
    assert result["rop"] > 0


def test_suggest_order_needs_order():
    result = suggest_order(daily_demand=10, sigma=2, lead=3, on_hand=5, moq=1)
    assert result["qty"] > 0
    assert result["qty"] % 1 == 0


def test_suggest_order_respects_moq():
    # MOQ=5, should round up
    result = suggest_order(daily_demand=10, sigma=1, lead=2, on_hand=0, moq=5)
    assert result["qty"] % 5 == 0


def test_suggest_order_high_variability():
    # large sigma increases reorder point
    low_var = suggest_order(10, sigma=1, lead=2, on_hand=0, moq=1)
    high_var = suggest_order(10, sigma=20, lead=2, on_hand=0, moq=1)

    assert high_var["rop"] > low_var["rop"]
    assert high_var["qty"] >= low_var["qty"]


def test_suggest_order_negative_demand():
    # negative demand should be clipped to 0
    result = suggest_order(daily_demand=-5, sigma=1, lead=2, on_hand=0, moq=1)
    assert result["qty"] == 0
    assert result["rop"] >= 0
    assert result["daily_demand"] == 0.0