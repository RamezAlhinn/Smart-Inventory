import pytest
from packages.core.inventory.reorder import suggest_order

def test_suggest_order_no_need():
    qty, rop, sigma = suggest_order(daily_demand=5, sigma=1, lead=2, on_hand=20, moq=1)
    assert qty == 0  # enough stock
    assert rop > 0

def test_suggest_order_needs_order():
    qty, rop, sigma = suggest_order(daily_demand=10, sigma=2, lead=3, on_hand=5, moq=1)
    assert qty > 0
    assert qty % 1 == 0

def test_suggest_order_respects_moq():
    # MOQ=5, should round up
    qty, rop, sigma = suggest_order(daily_demand=10, sigma=1, lead=2, on_hand=0, moq=5)
    assert qty % 5 == 0

def test_suggest_order_high_variability():
    # large sigma increases reorder point
    qty_low_var, rop_low, _ = suggest_order(10, sigma=1, lead=2, on_hand=0, moq=1)
    qty_high_var, rop_high, _ = suggest_order(10, sigma=20, lead=2, on_hand=0, moq=1)
    assert rop_high > rop_low
    assert qty_high_var >= qty_low_var

def test_suggest_order_negative_demand():
    # negative demand should be clipped to 0
    qty, rop, sigma = suggest_order(daily_demand=-5, sigma=1, lead=2, on_hand=0, moq=1)
    assert qty == 0
    assert rop >= 0