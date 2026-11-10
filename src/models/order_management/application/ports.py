"""Application-level ports for the order management module."""

from __future__ import annotations

from typing import Any, Protocol

from ..domain.entities import Order
from .dto import OrderDTO


class OrderRepository(Protocol):
    """Persistence boundary for the order aggregate.

    Implementations must persist the full aggregate (order, items) atomically
    and enforce optimistic concurrency on updates.
    """

    def add(self, order: Order) -> Order:
        """Persist a new order aggregate."""
        ...

    def get(self, order_id: str) -> Order | None:
        """Return an order aggregate or ``None`` when it does not exist."""
        ...

    def update(self, order: Order, expected_version: int) -> Order:
        """Persist changes when ``expected_version`` matches the stored version."""
        ...


class OrderServicePort(Protocol):
    """Read-write order contract for API and integration."""

    def create(self, customer_id: str, items: list[dict[str, Any]] | None = None) -> OrderDTO:
        """Create a new order."""
        ...

    def get(self, order_id: str) -> OrderDTO | None:
        """Get an order by ID."""
        ...

    def update_status(self, order_id: str, status: str, version: int) -> OrderDTO:
        """Update order status."""
        ...

    def add_item(
        self,
        order_id: str,
        description: str,
        quantity: float,
        unit_price: float,
    ) -> OrderDTO:
        """Add an item to an order."""
        ...

    def remove_item(self, order_id: str, item_id: str) -> OrderDTO:
        """Remove an item from an order."""
        ...

    def update_item_quantity(self, order_id: str, item_id: str, quantity: float) -> OrderDTO:
        """Update an item quantity."""
        ...
