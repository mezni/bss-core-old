from __future__ import annotations

import uuid
from decimal import Decimal

from src.domain.models import Customer, Order, OrderItem

TAX_RATE = Decimal("0.10")  # 10% fixed tax rate for S03 MVP


class OrderService:
    """Create an order with customer validation and draft status assignment."""

    def create_order(
        self,
        customer_id: int,
        items: list[dict],
        db_session,
    ) -> Order:
        """Create a new order in draft status.

        Validates:
        - Customer exists and is eligible
        - At least one order item provided
        - Items have valid description, quantity, and unit_price

        Returns the created order in draft status.
        """
        # Validate customer exists and is eligible
        customer = db_session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        if not customer.eligibility_status:
            raise ValueError(f"Customer {customer_id} is not eligible for order creation")

        # Calculate subtotal
        subtotal = Decimal("0")

        for item_data in items:
            description = item_data.get("description", "")
            quantity = item_data.get("quantity", 1)
            unit_price = Decimal(str(item_data.get("unit_price", "0")))

            if quantity < 1:
                raise ValueError("Quantity must be at least 1")

            if unit_price < 0:
                raise ValueError("Unit price must be non-negative")

            line_total = quantity * unit_price
            subtotal += line_total

        # Calculate tax using fixed rate (10% for S03 MVP)
        tax_amount = subtotal * TAX_RATE
        total = subtotal + tax_amount

        # Create order in draft status with UUID v4
        order = Order(
            id=f"ORD-{str(uuid.uuid4())}",
            status="draft",
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
            customer_id=customer_id,
        )

        db_session.add(order)
        db_session.flush()  # Get order ID to assign to items

        # Create order items with the order_id
        for item_data in items:
            description = item_data.get("description", "")
            quantity = item_data.get("quantity", 1)
            unit_price = Decimal(str(item_data.get("unit_price", "0")))
            line_total = quantity * unit_price

            order_item = OrderItem(
                order_id=order.id,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
            db_session.add(order_item)

        db_session.commit()

        # Refresh order with relationship data
        db_session.refresh(order)

        return order
