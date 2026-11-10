"""Order management application DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain.entities import Order, OrderItem


@dataclass(frozen=True)
class OrderItemDTO:
    """Data transfer object for an order item."""
    id: str
    description: str
    quantity: float
    unit_price: float
    line_total: float

    @staticmethod
    def from_domain(item: OrderItem) -> OrderItemDTO:
        return OrderItemDTO(
            id=item.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )


@dataclass(frozen=True)
class OrderDTO:
    """Data transfer object for an order."""
    id: str
    status: str
    subtotal: float
    tax_amount: float
    total: float
    customer_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    items: tuple[OrderItemDTO, ...] = ()

    @staticmethod
    def from_domain(order: Order) -> OrderDTO:
        items_dto = tuple(
            OrderItemDTO.from_domain(item) for item in order.items
        )
        return OrderDTO(
            id=order.id,
            status=order.status.value,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total=order.total,
            customer_id=order.customer_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            version=order.version,
            items=items_dto,
        )


def order_item_to_dto(item: OrderItem) -> OrderItemDTO:
    """Convert an OrderItem domain entity to a DTO."""
    return OrderItemDTO.from_domain(item)


def order_to_dto(order: Order) -> OrderDTO:
    """Convert an Order domain entity to a DTO."""
    return OrderDTO.from_domain(order)