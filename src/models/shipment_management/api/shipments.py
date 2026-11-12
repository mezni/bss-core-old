"""Shipment management API router.

Handles shipment creation under the ``order_to_shipment`` workflow,
guarded by ``user:admin``. Domain errors propagate to the centralized
standardized error handlers in ``src/api/health.py``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, model_validator

from src.models.identity_access.api.dependencies import require_workflow_permission
from src.models.identity_access.api.permissions import USER_ADMIN, WORKFLOW_ORDER_TO_SHIPMENT

from ..application.dto import ShipmentDTO
from ..application.service import ShipmentService
from ..domain.value_objects import ShipmentStatus
from .dependencies import get_shipment_service

router = APIRouter(prefix="/api/v1/shipments", tags=["shipment_management"])

workflow_guard = require_workflow_permission(WORKFLOW_ORDER_TO_SHIPMENT, USER_ADMIN)


class ShipmentCreate(BaseModel):
    """Payload for creating a shipment."""

    order_id: str = Field(..., description="Order ID to create shipment for")
    carrier_name: str = Field(..., min_length=1, description="Name of the shipping carrier")


class ShipmentUpdate(BaseModel):
    """Payload for updating a shipment carrier and/or lifecycle status."""

    version: int = Field(..., ge=1, description="Current shipment version")
    carrier_name: str | None = Field(
        None, min_length=1, description="New carrier name (pending shipments only)"
    )
    status: ShipmentStatus | None = Field(
        None, description="Target lifecycle status"
    )

    @model_validator(mode="after")
    def require_change(self) -> ShipmentUpdate:
        if self.carrier_name is None and self.status is None:
            raise ValueError("At least one of carrier_name or status is required")
        return self


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


@router.patch(
    "/{shipment_id}",
    summary="Update shipment",
    status_code=200,
    dependencies=[Depends(workflow_guard)],
)
def update_shipment(
    shipment_id: str,
    payload: ShipmentUpdate,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Update a shipment's carrier or advance its lifecycle status."""
    return service.update_shipment(
        shipment_id,
        version=payload.version,
        carrier_name=payload.carrier_name,
        status=payload.status.value if payload.status is not None else None,
    )


@router.get(
    "",
    summary="List shipments",
    status_code=200,
    dependencies=[Depends(workflow_guard)],
)
def list_shipments(
    service: ShipmentService = Depends(get_shipment_service),
) -> dict[str, int | list[dict] | str]:
    """List all shipments (no filtering in MVP)."""
    return {"shipments": [], "page": 1, "page_size": 100, "total": 0}


@router.get(
    "/{shipment_id}",
    summary="Get shipment by ID",
    status_code=200,
    dependencies=[Depends(workflow_guard)],
)
def get_shipment(
    shipment_id: str,
    service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentDTO:
    """Get a shipment by ID."""
    return service.get_shipment(shipment_id)
