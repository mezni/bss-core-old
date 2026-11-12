"""Shipment management DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.entities import Shipment


@dataclass
class ShipmentDTO:
    """Data transfer object for a shipment."""

    id: str
    status: str
    tracking_reference: str
    carrier_name: str
    order_id: str
    created_at: str
    updated_at: str
    version: int
    delivered_at: str | None = None

    @staticmethod
    def from_domain(shipment: Shipment) -> ShipmentDTO:
        return ShipmentDTO(
            id=shipment.id,
            status=shipment.status.value,
            tracking_reference=shipment.tracking_reference,
            carrier_name=shipment.carrier_name,
            order_id=shipment.order_id,
            created_at=shipment.created_at.isoformat(),
            updated_at=shipment.updated_at.isoformat(),
            version=shipment.version,
            delivered_at=(
                shipment.delivered_at.isoformat()
                if shipment.delivered_at is not None
                else None
            ),
        )
