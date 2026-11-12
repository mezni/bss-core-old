"""Shipment management application service.

Coordinates shipment lifecycle use cases: create shipment for a confirmed order,
transition status, and failure semantics (leaves order confirmed on failure).
Emits ``order_to_shipment`` workflow events (FR-008).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.logging import (
    log_workflow_completed,
    log_workflow_failed,
    log_workflow_started,
)

from ..domain.entities import Shipment
from ..domain.exceptions import (
    InvalidTransition,
    OrderNotConfirmed,
    OrderNotFound,
    ShipmentDomainError,
    ShipmentNotFound,
    ShipmentStaleUpdate,
    ShipmentValidationError,
)
from ..domain.value_objects import ShipmentStatus
from .dto import ShipmentDTO
from .ports import ShipmentOrderPort, ShipmentRepositoryPort

WORKFLOW_NAME = "order_to_shipment"
WORKFLOW_MODULES = ["order_management", "shipment_management"]


@dataclass
class ShipmentService:
    """Coordinates shipment lifecycle and business logic use cases."""

    repository: ShipmentRepositoryPort
    orders: ShipmentOrderPort

    def create_shipment(self, order_id: str, carrier_name: str) -> ShipmentDTO:
        """Create a shipment for a confirmed order and mark the order shipped."""
        log_workflow_started(
            WORKFLOW_NAME, step="create_shipment", modules=WORKFLOW_MODULES
        )
        try:
            status = self.orders.get_status(order_id)
            if status is None:
                raise OrderNotFound(f"Order {order_id} was not found")
            if status != "confirmed":
                raise OrderNotConfirmed(
                    "Shipment can only be created for confirmed orders"
                )
            shipment = Shipment.create(order_id=order_id, carrier_name=carrier_name)
            shipment = self.repository.create(shipment)
            try:
                self.orders.mark_as_shipped(order_id)
            except ShipmentDomainError:
                self.repository.delete(shipment.id)
                raise
        except ShipmentDomainError as error:
            log_workflow_failed(
                WORKFLOW_NAME,
                step="create_shipment",
                error=error.message,
                modules=WORKFLOW_MODULES,
            )
            raise
        log_workflow_completed(WORKFLOW_NAME, step="create_shipment", modules=WORKFLOW_MODULES)
        return ShipmentDTO.from_domain(shipment)

    def get_shipment(self, shipment_id: str) -> ShipmentDTO:
        """Get a shipment by ID."""
        shipment = self.repository.get(shipment_id)
        if shipment is None:
            raise ShipmentNotFound(f"Shipment {shipment_id} was not found")
        return ShipmentDTO.from_domain(shipment)

    def update_shipment(
        self,
        shipment_id: str,
        version: int,
        carrier_name: str | None = None,
        status: str | None = None,
    ) -> ShipmentDTO:
        """Update carrier and/or status with optimistic concurrency control."""
        shipment = self.repository.get(shipment_id)
        if shipment is None:
            raise ShipmentNotFound(f"Shipment {shipment_id} was not found")
        if version != shipment.version:
            raise ShipmentStaleUpdate(version, shipment.version)
        if carrier_name is None and status is None:
            raise ShipmentValidationError(
                "At least one of carrier_name or status must be provided"
            )

        if carrier_name is not None:
            shipment.update_carrier(carrier_name)
        if status is not None:
            try:
                target = ShipmentStatus(status)
            except ValueError as error:
                raise ShipmentValidationError(
                    f"Unsupported shipment status: {status}"
                ) from error
            try:
                shipment.transition_to(target)
            except InvalidTransition as error:
                raise InvalidTransition(shipment.status.value, status) from error

        shipment = self.repository.update(shipment, expected_version=version)
        return ShipmentDTO.from_domain(shipment)

    def update_status(self, shipment_id: str, status: str, version: int) -> ShipmentDTO:
        """Update shipment status with version validation."""
        return self.update_shipment(shipment_id, version=version, status=status)
