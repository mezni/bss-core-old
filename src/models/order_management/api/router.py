"""Order management API router.

Workflow entry points (create, confirm) are guarded by the
``customer_to_order`` workflow permission (``user:view`` or
``user:admin``). Domain errors propagate to the centralized standardized
error handlers in ``src/api/health.py``.
"""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends

from src.models.identity_access.api.dependencies import require_workflow_permission
from src.models.identity_access.api.permissions import (
    USER_VIEW,
    WORKFLOW_CUSTOMER_TO_ORDER,
)

from ..application.dto import OrderDTO
from ..application.service import OrderService
from .dependencies import get_order_service
from .schemas import OrderCreate, OrderItemCreate, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["order_management"])

workflow_guard = require_workflow_permission(WORKFLOW_CUSTOMER_TO_ORDER, USER_VIEW)


@router.post("", summary="Create order", status_code=201, dependencies=[Depends(workflow_guard)])
def create_order(
    order_create: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Create a new order with at least one item."""
    return service.create(
        customer_id=order_create.customer_id,
        items=[item.model_dump() for item in order_create.items],
    )


@router.get("/{order_id}", summary="Get order by ID")
def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Get an order by ID."""
    return service.get(order_id)


@router.patch("/{order_id}/status", summary="Update order status")
def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Update order status with version validation."""
    return service.update_status(
        order_id=order_id, status=status_update.status, version=status_update.version
    )


@router.post("/{order_id}/items", summary="Add order item")
def add_order_item(
    order_id: str,
    item: OrderItemCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Add an item to a draft order."""
    return service.add_item(order_id, item.description, item.quantity, item.unit_price)


@router.patch("/{order_id}/items/{item_id}", summary="Update order item")
def update_order_item(
    order_id: str,
    item_id: str,
    quantity: float = Body(...),
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Update an order item quantity."""
    return service.update_item_quantity(order_id, item_id, quantity)


@router.delete("/{order_id}/items/{item_id}", summary="Remove order item")
def remove_order_item(
    order_id: str,
    item_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Remove an item from a draft order."""
    return service.remove_item(order_id, item_id)


@router.patch(
    "/{order_id}/transitions/confirm",
    summary="Confirm order",
    dependencies=[Depends(workflow_guard)],
)
def confirm_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Confirm an order (draft → confirmed, requires at least one item)."""
    return service.confirm_order(order_id)


@router.patch("/{order_id}/transitions/ship", summary="Ship order")
def ship_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Ship an order (confirmed → shipped)."""
    return service.ship_order(order_id)


@router.patch("/{order_id}/transitions/deliver", summary="Deliver order")
def deliver_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Deliver an order (shipped → delivered)."""
    return service.deliver_order(order_id)


@router.post("/{order_id}/transitions/cancel", summary="Cancel order")
def cancel_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    """Cancel an order (draft → cancelled, terminal state)."""
    return service.cancel_order(order_id)
