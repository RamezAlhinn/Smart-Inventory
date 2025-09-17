from packages.core.inventory.reorder import suggest_order

def test_suggest_order_no_need():
    qty, reorder_point, sigma = suggest_order(
        daily_demand=5, sigma=1, lead=2, on_hand=20, moq=10
    )
    # Plenty of stock, no order needed
    assert qty == 0

def test_suggest_order_needs_order():
    qty, reorder_point, sigma = suggest_order(
        daily_demand=10, sigma=2, lead=2, on_hand=5, moq=5
    )
    # Should trigger reorder
    assert qty > 0
    # Quantity should be multiple of MOQ
    assert qty % 5 == 0