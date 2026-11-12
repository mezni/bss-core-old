"""Adapter exposing order-module operations to the shipment use case."""

from __future__ import annotations

from src.models.order_management.application.service import OrderService
from src.models.order_management.domain.exceptions import (
    OrderDomainError as OrderModuleError,
)
from src.models.order_management.domain.exceptions import (
    OrderNotFound as OrderModuleNotFound,
)

from ..application.ports import ShipmentOrderPort
from ..domain.exceptions import OrderNotConfirmed, OrderNotFound


class OrderModuleAdapter(ShipmentOrderPort):
    """Bridge the order module's application service to the shipment port."""

    def __init__(self, orders: OrderService) -> None:
        self._orders = orders

    def get_status(self, order_id: str) -> str | None:
        """Return the order status, or ``None`` when the order does not exist."""
        try:
            return self._orders.get(order_id).status
        except OrderModuleNotFound:
            return None

    def mark_as_shipped(self, order_id: str) -> None:
        """Transition the order to ``shipped``, translating module errors."""
        try:
            self._orders.mark_as_shipped(order_id)
        except OrderModuleNotFound as error:
            raise OrderNotFound(str(error)) from error
        except OrderModuleError as error:
            raise OrderNotConfirmed(str(error)) from error
