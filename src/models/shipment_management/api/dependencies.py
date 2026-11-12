"""Dependency wiring for the shipment management API."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from src.domain.database import get_db
from src.models.order_management.api.dependencies import get_order_service
from src.models.order_management.application.service import OrderService

from ..application.service import ShipmentService
from ..infrastructure.order_adapter import OrderModuleAdapter
from ..infrastructure.repository import ShipmentRepository


def get_shipment_repository(
    session: Session = Depends(get_db),
) -> ShipmentRepository:
    return ShipmentRepository(session)


def get_shipment_service(
    repository: ShipmentRepository = Depends(get_shipment_repository),
    orders: OrderService = Depends(get_order_service),
) -> ShipmentService:
    """Build the shipment service with persistence and order integration."""
    return ShipmentService(repository=repository, orders=OrderModuleAdapter(orders))
