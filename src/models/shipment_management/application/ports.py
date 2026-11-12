"""Ports for the shipment management application module."""

from __future__ import annotations

from typing import Protocol

from ..domain.entities import Shipment


class ShipmentRepositoryPort(Protocol):
    """Persistence boundary for the shipment aggregate."""

    def get(self, shipment_id: str) -> Shipment | None:
        """Return a shipment aggregate or ``None`` when it does not exist."""
        ...

    def create(self, shipment: Shipment) -> Shipment:
        """Persist a new shipment aggregate."""
        ...

    def update(self, shipment: Shipment, expected_version: int) -> Shipment:
        """Persist changes when ``expected_version`` matches the stored version."""
        ...

    def delete(self, shipment_id: str) -> None:
        """Remove a shipment aggregate."""
        ...


class ShipmentOrderPort(Protocol):
    """Order-module contract required by the order-to-shipment workflow."""

    def get_status(self, order_id: str) -> str | None:
        """Return the order status, or ``None`` when the order does not exist."""
        ...

    def mark_as_shipped(self, order_id: str) -> None:
        """Transition the order to ``shipped``.

        Raises:
            OrderNotFound: When the order does not exist.
            OrderNotConfirmed: When the order is not in ``confirmed`` status.
        """
        ...
