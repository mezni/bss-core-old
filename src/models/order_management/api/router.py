"""Order management API router."""

from fastapi import APIRouter, Body, HTTPException

from ..application.dto import OrderDTO
from ..application.service import OrderService
from ..domain.exceptions import InvalidOrder, OrderNotFound, StaleUpdate
from .schemas import OrderCreate, OrderItemCreate, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["order_management"])


def get_order_service() -> OrderService:
    """Get order service instance."""
    # In a real implementation, would inject repository via dependency injection
    # Session would be provided by the FastAPI dependency injection system
    # For now, return a service with no repository (read-only operations will fail)
    return OrderService()


@router.post("/", summary="Create order", status_code=201)
def create_order(
    order_create: OrderCreate,
) -> OrderDTO:
    """Create a new order with at least one item."""
    service = get_order_service()
    try:
        order_dto = service.create(customer_id=order_create.customer_id, items=order_create.items)
        return order_dto
    except InvalidOrder as e:
        raise HTTPException(status_code=400, detail=e.message) from None


@router.get("/{order_id}", summary="Get order by ID")
def get_order(
    order_id: str,
) -> OrderDTO:
    """Get an order by ID."""
    service = get_order_service()
    order_dto = service.get(order_id)
    if order_dto is None:
        raise OrderNotFound(f"Order {order_id} was not found")
    return order_dto


@router.patch("/{order_id}/status", summary="Update order status")
def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
) -> OrderDTO:
    """Update order status with version validation."""
    service = get_order_service()
    try:
        order_dto = service.update_status(
            order_id=order_id, status=status_update.status, version=status_update.version
        )
        return order_dto
    except StaleUpdate as e:
        raise HTTPException(
            status_code=409,
            detail=e.message,
            headers={"current_version": str(e.current_version)},
        ) from None


@router.post("/{order_id}/items", summary="Add order item")
def add_order_item(
    order_id: str,
    item: OrderItemCreate,
) -> OrderDTO:
    """Add an item to an order."""
    service = get_order_service()
    try:
        order_dto = service.add_item(order_id, item.description, item.quantity, item.unit_price)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.patch("/{order_id}/items/{item_id}", summary="Update order item")
def update_order_item(
    order_id: str,
    item_id: str,
    quantity: float = Body(...),
) -> OrderDTO:
    """Update an order item quantity."""
    service = get_order_service()
    try:
        order_dto = service.update_item_quantity(order_id, item_id, quantity)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.delete("/{order_id}/items/{item_id}", summary="Remove order item")
def remove_order_item(
    order_id: str,
    item_id: str,
) -> OrderDTO:
    """Remove an item from an order."""
    service = get_order_service()
    try:
        order_dto = service.remove_item(order_id, item_id)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.patch("/{order_id}/transitions/confirm", summary="Confirm order")
def confirm_order(
    order_id: str,
) -> OrderDTO:
    """Confirm an order (draft → confirmed, requires at least one item)."""
    service = get_order_service()
    try:
        order_dto = service.confirm_order(order_id)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.patch("/{order_id}/transitions/ship", summary="Ship order")
def ship_order(
    order_id: str,
) -> OrderDTO:
    """Ship an order (confirmed → shipped)."""
    service = get_order_service()
    try:
        order_dto = service.ship_order(order_id)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.patch("/{order_id}/transitions/deliver", summary="Deliver order")
def deliver_order(
    order_id: str,
) -> OrderDTO:
    """Deliver an order (shipped → delivered)."""
    service = get_order_service()
    try:
        order_dto = service.deliver_order(order_id)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None


@router.post("/{order_id}/transitions/cancel", summary="Cancel order")
def cancel_order(
    order_id: str,
) -> OrderDTO:
    """Cancel an order (draft → cancelled, terminal state)."""
    service = get_order_service()
    try:
        order_dto = service.cancel_order(order_id)
        return order_dto
    except (InvalidOrder, OrderNotFound) as e:
        code = 400 if isinstance(e, InvalidOrder) else 404
        raise HTTPException(status_code=code, detail=e.message) from None