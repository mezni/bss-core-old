"""Order management application service.

Coordinates the order lifecycle use cases, wiring persistence through the
order repository port and customer reference validation through the
``CustomerEligibilityPort``. Emits ``customer_to_order`` workflow events
(FR-008) on the workflow entry points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.infrastructure.logging import (
    log_workflow_completed,
    log_workflow_failed,
    log_workflow_started,
)

from ..domain.entities import Order, OrderItem
from ..domain.exceptions import (
    InvalidOrder,
    InvalidTransition,
    OrderDomainError,
    OrderNotFound,
)
from ..domain.value_objects import OrderStatus
from .dto import OrderDTO
from .ports import OrderRepository

WORKFLOW_NAME = "customer_to_order"
WORKFLOW_MODULES = ["customer_management", "order_management"]


def _item_payload(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    return {
        "description": getattr(item, "description", ""),
        "quantity": getattr(item, "quantity", 1),
        "unit_price": getattr(item, "unit_price", 0),
    }


@dataclass
class OrderService:
    """Coordinates order lifecycle and business logic use cases."""

    repository: OrderRepository
    eligibility: Any | None = field(default=None, repr=False)

    def create(self, customer_id: str, items: list[Any] | None = None) -> OrderDTO:
        """Create a new order with customer reference validation."""
        log_workflow_started(WORKFLOW_NAME, step="create_order", modules=WORKFLOW_MODULES)
        if self.eligibility is not None and self.eligibility.get_summary(customer_id) is None:
            log_workflow_failed(
                WORKFLOW_NAME,
                step="create_order",
                error=f"Customer {customer_id} was not found",
                modules=WORKFLOW_MODULES,
            )
            raise OrderNotFound(f"Customer {customer_id} was not found")
        try:
            payloads = [_item_payload(item) for item in items or []]
            order = Order.create(customer_id=customer_id, items=payloads)
            order = self.repository.add(order)
        except OrderDomainError as error:
            log_workflow_failed(
                WORKFLOW_NAME, step="create_order", error=error.message, modules=WORKFLOW_MODULES
            )
            raise
        log_workflow_completed(WORKFLOW_NAME, step="create_order", modules=WORKFLOW_MODULES)
        return OrderDTO.from_domain(order)

    def get(self, order_id: str) -> OrderDTO:
        """Get an order by ID."""
        order = self._get_or_raise(order_id)
        return OrderDTO.from_domain(order)

    def update_status(self, order_id: str, status: str, version: int) -> OrderDTO:
        """Update order status with version validation."""
        order = self._get_or_raise(order_id)
        transition = self._transition_for(order, status)
        order = self._apply_transition(order, transition, expected_version=version)
        return OrderDTO.from_domain(order)

    def confirm_order(self, order_id: str) -> OrderDTO:
        """Confirm an order (draft -> confirmed)."""
        log_workflow_started(WORKFLOW_NAME, step="confirm_order", modules=WORKFLOW_MODULES)
        try:
            order = self._transition(order_id, "confirm")
        except OrderDomainError as error:
            log_workflow_failed(
                WORKFLOW_NAME, step="confirm_order", error=error.message, modules=WORKFLOW_MODULES
            )
            raise
        log_workflow_completed(WORKFLOW_NAME, step="confirm_order", modules=WORKFLOW_MODULES)
        return OrderDTO.from_domain(order)

    def mark_as_shipped(self, order_id: str) -> OrderDTO:
        """Mark an order as shipped (OrderStatusPort implementation)."""
        return self.ship_order(order_id)

    def ship_order(self, order_id: str) -> OrderDTO:
        """Ship an order (confirmed -> shipped)."""
        order = self._transition(order_id, "ship")
        return OrderDTO.from_domain(order)

    def deliver_order(self, order_id: str) -> OrderDTO:
        """Deliver an order (shipped -> delivered)."""
        order = self._transition(order_id, "deliver")
        return OrderDTO.from_domain(order)

    def cancel_order(self, order_id: str) -> OrderDTO:
        """Cancel an order (draft -> cancelled, terminal)."""
        order = self._transition(order_id, "cancel")
        return OrderDTO.from_domain(order)

    def add_item(
        self, order_id: str, description: str, quantity: float, unit_price: float
    ) -> OrderDTO:
        """Add an item to a draft order."""
        order = self._get_or_raise(order_id)
        self._require_draft(order, "add items to")
        expected_version = order.version
        item = OrderItem(
            id=str(uuid4()),
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            line_total=round(quantity * unit_price, 2),
            created_at=datetime.now(UTC),
            order_id=order.id,
        )
        order.add_item(item)
        order.calculate_totals()
        order = self.repository.update(order, expected_version=expected_version)
        return OrderDTO.from_domain(order)

    def remove_item(self, order_id: str, item_id: str) -> OrderDTO:
        """Remove an item from a draft order."""
        order = self._get_or_raise(order_id)
        self._require_draft(order, "remove items from")
        expected_version = order.version
        order.remove_item(item_id)
        order.validate()
        order.calculate_totals()
        order = self.repository.update(order, expected_version=expected_version)
        return OrderDTO.from_domain(order)

    def update_item_quantity(
        self, order_id: str, item_id: str, quantity: float
    ) -> OrderDTO:
        """Update an item quantity on a draft order."""
        order = self._get_or_raise(order_id)
        self._require_draft(order, "update items on")
        expected_version = order.version
        order.update_item_quantity(item_id, quantity)
        order.calculate_totals()
        order = self.repository.update(order, expected_version=expected_version)
        return OrderDTO.from_domain(order)

    def calculate_totals(self, order: Order) -> OrderDTO:
        """Recalculate order totals from items."""
        expected_version = order.version
        order.calculate_totals()
        order = self.repository.update(order, expected_version=expected_version)
        return OrderDTO.from_domain(order)

    def _get_or_raise(self, order_id: str) -> Order:
        order = self.repository.get(order_id)
        if order is None:
            raise OrderNotFound(f"Order {order_id} was not found")
        return order

    def _transition(self, order_id: str, transition: str) -> Order:
        """Load, apply a domain transition, and persist with version check."""
        order = self._get_or_raise(order_id)
        return self._apply_transition(order, transition)

    def _apply_transition(
        self, order: Order, transition: str, expected_version: int | None = None
    ) -> Order:
        if expected_version is None:
            expected_version = order.version
        getattr(order, transition)()
        return self.repository.update(order, expected_version=expected_version)

    def _transition_for(self, order: Order, status: str) -> str:
        try:
            target = OrderStatus(status)
        except ValueError as error:
            raise InvalidTransition(order.status.value, status) from error
        mapping = {
            OrderStatus.CONFIRMED: "confirm",
            OrderStatus.SHIPPED: "ship",
            OrderStatus.DELIVERED: "deliver",
            OrderStatus.CANCELLED: "cancel",
        }
        transition = mapping.get(target)
        if transition is None:
            raise InvalidTransition(order.status.value, status)
        return transition

    def _require_draft(self, order: Order, action: str) -> None:
        if order.status != OrderStatus.DRAFT:
            raise InvalidOrder(f"Can only {action} draft orders")
