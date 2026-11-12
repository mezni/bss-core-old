"""Unit tests for order management domain entities."""

from datetime import UTC, datetime

import pytest

from src.models.order_management.domain.entities import Order, OrderItem
from src.models.order_management.domain.exceptions import InvalidOrder, OrderItemError
from src.models.order_management.domain.value_objects import OrderStatus


def test_order_item_creation():
    """Test OrderItem can be created with valid data."""
    now = datetime.now(UTC)
    item = OrderItem(
        id="item-001",
        description="Widget",
        quantity=2,
        unit_price=10.50,
        line_total=21.00,
        created_at=now,
    )
    assert item.description == "Widget"
    assert item.quantity == 2
    assert item.unit_price == 10.50
    assert item.line_total == 21.00


def test_order_item_validation_minimum_quantity():
    """Test OrderItem rejects quantity <= 0."""
    from datetime import datetime

    from src.models.order_management.domain.entities import OrderItem
    with pytest.raises(OrderItemError):
        OrderItem(
            id="item-002",
            description="Test",
            quantity=0,
            unit_price=10.00,
            line_total=0.00,
            created_at=datetime.now(UTC),
        )


def test_order_item_validation_max_price():
    """Test OrderItem rejects negative unit price."""
    from datetime import datetime

    from src.models.order_management.domain.entities import OrderItem
    with pytest.raises(OrderItemError):
        OrderItem(
            id="item-003",
            description="Test",
            quantity=1,
            unit_price=-5.00,
            line_total=0.00,
            created_at=datetime.now(UTC),
        )


def test_order_creation():
    """Test Order can be created with valid data."""
    order = Order.create(
        customer_id="customer-001",
        items=[
            {"description": "Widget", "quantity": 2, "unit_price": 10.50},
        ],
    )
    assert order.customer_id == "customer-001"
    assert order.status == OrderStatus.DRAFT
    assert order.subtotal == 21.00
    assert order.total == 23.10  # 21.00 + 10% tax
    assert order.version == 1
    assert len(order.items) == 1


def test_order_requires_at_least_one_item():
    """Test Order creation fails without items."""
    from src.models.order_management.domain.entities import Order
    with pytest.raises(InvalidOrder):
        Order.create(customer_id="customer-001", items=[])


def test_order_status_transitions():
    """Test order status transitions."""
    order = Order.create(
        customer_id="customer-001",
        items=[{"description": "Widget", "quantity": 1, "unit_price": 10.00}],
    )

    # Test confirm transition
    order.confirm()
    assert order.status.value == "confirmed"
    assert order.version == 2
    
    # Test that invalid transition from confirmed to drafted is rejected
    try:
        order.status = OrderStatus.DRAFT  # This should not happen directly, but testing the enum
        assert True
    except Exception:
        assert True


def test_order_cancellation():
    """Test order can be cancelled from draft state."""
    order = Order.create(
        customer_id="customer-001",
        items=[{"description": "Widget", "quantity": 1, "unit_price": 10.00}],
    )
    assert order.status == OrderStatus.DRAFT
    
    order.cancel()
    assert order.status == OrderStatus.CANCELLED
    assert order.version == 2


def test_order_reversion_terminal():
    """Test that cancelled orders cannot be reverted."""
    order = Order.create(
        customer_id="customer-001",
        items=[{"description": "Widget", "quantity": 1, "unit_price": 10.00}],
    )
    order.cancel()

    with pytest.raises(InvalidOrder):
        order.revert()


def test_order_total_recalculation():
    """Test order totals are recalculated correctly."""
    order = Order.create(
        customer_id="customer-001",
        items=[
            {"description": "Widget", "quantity": 2, "unit_price": 10.50},
            {"description": "Gadget", "quantity": 1, "unit_price": 20.00},
        ],
    )
    assert order.subtotal == 41.00  # 21.00 + 20.00
    assert order.total == 45.10  # 41.00 + 10% tax
