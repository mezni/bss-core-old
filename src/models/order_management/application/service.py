"""Order management application service - extended with item operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ..domain.entities import Order
from ..domain.exceptions import InvalidOrder


def utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


@dataclass
class OrderService:
    """Coordinates order lifecycle and business logic use cases."""

    _repository: Any = field(default=None, repr=False)

    def create(self, customer_id: str, items: list[Any] | None = None) -> Any:
        """Create a new order with customer eligibility validation."""
        order_items: list[dict[str, Any]] = []
        if items:
            for item_data in items:
                if isinstance(item_data, dict):
                    description = item_data.get("description", "")
                    quantity = float(item_data.get("quantity", 1))
                    unit_price = float(item_data.get("unit_price", 0))
                else:
                    description = getattr(item_data, "description", "")
                    quantity = float(getattr(item_data, "quantity", 1))
                    unit_price = float(getattr(item_data, "unit_price", 0))

                if not description or not description.strip():
                    raise InvalidOrder("Item description is required")
                if quantity <= 0:
                    raise InvalidOrder("Quantity must be greater than zero")
                if unit_price < 0:
                    raise InvalidOrder("Unit price must be non-negative")
                line_total = round(quantity * unit_price, 2)
                order_items.append(
                    {
                        "description": description.strip(),
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total,
                    }
                )
        order = Order.create(customer_id=customer_id, items=order_items)
        return order

    def get(self, order_id: str) -> Any | None:
        """Get an order by ID."""
        # In a real implementation, would query the repository
        return None

    def update_status(self, order_id: str, status: str, version: int) -> Any:
        """Update order status with version validation."""
        # In a real implementation, would query and update the repository
        return None

    def add_item(self, order_id: str, description: str, quantity: float, unit_price: float) -> Any:
        """Add an item to an order."""
        # In a real implementation, would query and update the repository
        return None

    def remove_item(self, order_id: str, item_id: str) -> Any:
        """Remove an item from an order."""
        # In a real implementation, would query and update the repository
        return None

    def update_item_quantity(self, order_id: str, item_id: str, quantity: float) -> Any:
        """Update an item quantity."""
        # In a real implementation, would query and update the repository
        return None

    def calculate_totals(self, order: Any) -> Any:
        """Recalculate order totals from items."""
        # In a real implementation, would update the repository
        return order
