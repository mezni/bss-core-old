from __future__ import annotations

from decimal import Decimal

from src.domain.models import Order, OrderItem


class OrderItemService:
    """Domain-layer use case: add/modify/remove order items, recalculate order total."""

    def add_item(self, order_id: str, item_data: dict, db_session) -> OrderItem:
        """Add a new item to an order and recalculate total."""
        quantity = item_data.get("quantity", 1)
        unit_price = Decimal(str(item_data.get("unit_price", "0")))
        description = item_data.get("description", "")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1")

        if unit_price < 0:
            raise ValueError("Unit price must be non-negative")

        line_total = quantity * unit_price

        order_item = OrderItem(
            order_id=order_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
        )
        db_session.add(order_item)

        # Recalculate order total
        order = db_session.query(Order).get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Calculate new subtotal from all items
        subtotal = Decimal("0")
        for item in order.items:
            subtotal += item.line_total

        tax = Decimal("0")  # Fixed rate, no jurisdiction-specific logic for S03 MVP
        total = subtotal + tax

        order.subtotal = subtotal
        order.tax_amount = tax
        order.total = total

        db_session.commit()
        db_session.refresh(order)

        return order_item

    def modify_item(
        self, item_id: str, new_quantity: int, new_unit_price: Decimal, db_session
    ) -> Order:
        """Modify an existing order item and recalculate total."""
        if new_quantity < 1:
            raise ValueError("Quantity must be at least 1")

        if new_unit_price < 0:
            raise ValueError("Unit price must be non-negative")

        order_item = db_session.query(OrderItem).get(item_id)
        if not order_item:
            raise ValueError(f"Order item {item_id} not found")

        old_line_total = order_item.line_total
        new_line_total = new_quantity * new_unit_price
        new_line_total - old_line_total

        order_item.quantity = new_quantity
        order_item.unit_price = new_unit_price
        order_item.line_total = new_line_total

        # Recalculate order total
        order = order_item.order
        subtotal = Decimal("0")
        for item in order.items:
            subtotal += item.line_total

        tax = Decimal("0")
        total = subtotal + tax

        order.subtotal = subtotal
        order.tax_amount = tax
        order.total = total

        db_session.commit()
        db_session.refresh(order)

        return order

    def remove_item(self, item_id: str, db_session) -> Order:
        """Remove an order item and recalculate total."""
        order_item = db_session.query(OrderItem).get(item_id)
        if not order_item:
            raise ValueError(f"Order item {item_id} not found")

        order_id = order_item.order_id
        db_session.delete(order_item)

        # Recalculate order total
        order = db_session.query(Order).get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        subtotal = Decimal("0")
        for item in order.items:
            subtotal += item.line_total

        tax = Decimal("0")
        total = subtotal + tax

        order.subtotal = subtotal
        order.tax_amount = tax
        order.total = total

        db_session.commit()
        db_session.refresh(order)

        return order
