"""Shipment management API router.

Handles shipment creation under the ``order_to_shipment`` workflow,
guarded by ``user:admin``. Domain errors propagate to the centralized
standardized error handlers in ``src/api/health.py``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.models.identity_access.api.dependencies import require_workflow_permission
from src.models.identity_access.api.permissions import USER_ADMIN, WORKFLOW_ORDER_TO_SHIPMENT

from ..application.dto import ShipmentDTO
from ..application.service import ShipmentService
from .dependencies import get_shipment_service

router = APIRouter(prefix="/api/v1/shipments", tags=["shipment_management"])

workflow_guard = require_workflow_permission(WORKFLOW_ORDER_TO_SHIPMENT, USER_ADMIN)


class ShipmentCreate(BaseModel):
    """Payload for creating a shipment."""

    order_id: str = Field(..., description="Order ID to create shipment for")
    carrier_name: str = Field(..., min_length=1, description="Name of the shipping carrier")


@router.post(
    "",
    summary="Create shipment",
    status_code=201,
    dependencies=[Depends(workflow_guard)],
)
def create_shipment(
    shipment: ShipmentCreate,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Create a new shipment for a confirmed order."""
    return service.create_shipment(
        order_id=shipment.order_id, carrier_name=shipment.carrier_name
    )
