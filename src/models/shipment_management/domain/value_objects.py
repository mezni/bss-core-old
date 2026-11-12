"""Value objects for shipment management."""

from __future__ import annotations

from enum import StrEnum


class ShipmentStatus(StrEnum):
    PENDING = "pending"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
