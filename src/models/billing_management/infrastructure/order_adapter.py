"""Adapter exposing the order module's read model to the billing use case."""

from __future__ import annotations

from src.models.order_management.application.service import OrderService
from src.models.order_management.domain.exceptions import (
    OrderNotFound as OrderModuleNotFound,
)

from ..application.ports import OrderItemSummary, OrderReadPort, OrderSummary


class OrderModuleAdapter(OrderReadPort):
    """Bridge the order application service to the billing read port."""

    def __init__(self, orders: OrderService) -> None:
        self._orders = orders

    def get_order(self, order_id: str) -> OrderSummary | None:
        try:
            order = self._orders.get(order_id)
        except OrderModuleNotFound:
            return None
        return OrderSummary(
            id=order.id,
            status=order.status,
            customer_id=order.customer_id,
            total=order.total,
            items=tuple(
                OrderItemSummary(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                for item in order.items
            ),
        )
