"""Shipment aggregate root."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from .exceptions import (
    InvalidTransition,
    ShipmentConflictError,
    ShipmentValidationError,
)
from .value_objects import ShipmentStatus


@dataclass
class Shipment:
    """Represents a delivery request for an order."""

    id: str
    status: ShipmentStatus
    tracking_reference: str
    carrier_name: str
    order_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    delivered_at: datetime | None = None

    @classmethod
    def create(cls, order_id: str, carrier_name: str) -> Shipment:
        """Create a new shipment in PENDING status."""
        if not carrier_name or not carrier_name.strip():
            raise ShipmentValidationError("Carrier name is required for shipment creation")

        now = datetime.now(UTC)
        # Format: SHIP-550e8400-e29b-41d4-a716-446655440000
        ship_id = f"SHIP-{uuid4()}"
        # Format: SHIP-[UUID v4 substring]
        tracking = f"SHIP-{str(uuid4())[:8].upper()}"

        return cls(
            id=ship_id,
            status=ShipmentStatus.PENDING,
            tracking_reference=tracking,
            carrier_name=carrier_name.strip(),
            order_id=order_id,
            created_at=now,
            updated_at=now,
            version=1,
        )

    def update_carrier(self, carrier_name: str) -> None:
        """Update the carrier while the shipment is still pending."""
        if self.status == ShipmentStatus.DELIVERED:
            raise InvalidTransition(
                self.status.value,
                self.status.value,
                "Shipments in delivered status cannot be modified",
            )
        if self.status != ShipmentStatus.PENDING:
            raise ShipmentConflictError(
                "Carrier name can only be updated while the shipment is pending"
            )
        if not carrier_name or not carrier_name.strip():
            raise ShipmentValidationError("Carrier name cannot be empty")

        normalized = carrier_name.strip()
        if normalized == self.carrier_name:
            return
        self.carrier_name = normalized
        self.updated_at = datetime.now(UTC)
        self.version += 1

    def transition_to(self, target_status: ShipmentStatus) -> None:
        """Enforce valid status transitions: pending -> in-transit -> delivered."""
        if self.status == ShipmentStatus.DELIVERED:
            raise InvalidTransition(
                self.status.value,
                target_status.value,
                "Shipments in delivered status cannot be modified",
            )

        valid_transitions = {
            ShipmentStatus.PENDING: [ShipmentStatus.IN_TRANSIT, ShipmentStatus.EXCEPTION],
            ShipmentStatus.IN_TRANSIT: [ShipmentStatus.DELIVERED, ShipmentStatus.EXCEPTION],
            ShipmentStatus.EXCEPTION: [ShipmentStatus.PENDING, ShipmentStatus.IN_TRANSIT],
        }

        allowed = valid_transitions.get(self.status, [])
        if target_status not in allowed:
            raise InvalidTransition(self.status.value, target_status.value)

        self.status = target_status
        self.updated_at = datetime.now(UTC)
        if target_status == ShipmentStatus.DELIVERED:
            self.delivered_at = self.updated_at
        self.version += 1
