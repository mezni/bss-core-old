"""Value objects for shipment management."""

from __future__ import annotations

from enum import Enum


class ShipmentStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
