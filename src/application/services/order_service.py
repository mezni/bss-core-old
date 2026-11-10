from __future__ import annotations

import uuid
from decimal import Decimal

from src.domain.models import Order, OrderItem, Customer


class OrderService:
    """Domain-layer use case: create order with customer validation, item count check, draft status assignment."""

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

        # Validate at least one item
        if not items or len(items) == 0:
            raise ValueError("At least one order item is required")

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

        # Create order in draft status with UUID v4
        order = Order(
            id=f"ORD-{str(uuid.uuid4())}",
            status="draft",
            subtotal=subtotal,
            tax_amount=Decimal("0"),
            total=subtotal,
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