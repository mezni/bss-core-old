"""SQLAlchemy implementation of the shipment repository port."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.entities import Shipment
from ..domain.exceptions import ShipmentNotFound, ShipmentStaleUpdate
from ..domain.value_objects import ShipmentStatus
from ..infrastructure.orm import ShipmentORM


class ShipmentRepository:
    """Persist shipment aggregates in SQLAlchemy-backed tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, shipment_id: str) -> Shipment | None:
        """Return a shipment aggregate or None when it does not exist."""
        shipment = self.session.get(ShipmentORM, shipment_id)
        if shipment is None:
            return None
        return Shipment(
            id=shipment.id,
            status=ShipmentStatus(shipment.status),
            tracking_reference=shipment.tracking_reference,
            carrier_name=shipment.carrier_name,
            order_id=shipment.order_id,
            created_at=shipment.created_at,
            updated_at=shipment.updated_at,
            version=shipment.version,
            delivered_at=shipment.delivered_at,
        )

    def create(self, shipment: Shipment) -> Shipment:
        """Persist a new shipment aggregate."""
        orm = ShipmentORM(
            id=shipment.id,
            status=shipment.status.value,
            tracking_reference=shipment.tracking_reference,
            carrier_name=shipment.carrier_name,
            order_id=shipment.order_id,
            created_at=shipment.created_at,
            updated_at=shipment.updated_at,
            version=shipment.version,
            delivered_at=shipment.delivered_at,
        )
        self.session.add(orm)
        self.session.commit()
        return shipment

    def update(self, shipment: Shipment, expected_version: int) -> Shipment:
        """Persist changes when ``expected_version`` matches the stored version."""
        orm = self.session.get(ShipmentORM, shipment.id)
        if orm is None:
            raise ShipmentNotFound(f"Shipment {shipment.id} was not found")
        if orm.version != expected_version:
            raise ShipmentStaleUpdate(expected_version, orm.version)
        orm.status = shipment.status.value
        orm.tracking_reference = shipment.tracking_reference
        orm.carrier_name = shipment.carrier_name
        orm.updated_at = shipment.updated_at
        orm.delivered_at = shipment.delivered_at
        orm.version = shipment.version
        self.session.commit()
        return shipment

    def delete(self, shipment_id: str) -> None:
        """Remove a shipment aggregate."""
        orm = self.session.get(ShipmentORM, shipment_id)
        if orm is None:
            return
        self.session.delete(orm)
        self.session.commit()
