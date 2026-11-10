from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator

from src.application.services.order_service import OrderService
from src.presentation.api.auth import get_current_user, create_access_token
from src.infrastructure.db import get_db
from src.domain.models import Order, Customer

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


class OrderItemCreate(BaseModel):
    """Request model for order item creation."""

    description: str = Field(..., min_length=1, description="Product/service description")
    quantity: int = Field(ge=1, le=10000, description="Number of units (≥1)")
    unit_price: Decimal = Field(ge=0, le=100000, description="Price per unit (≥0)")

    @validator("unit_price", pre=True)
    def parse_unit_price(cls, v):
        if isinstance(v, str):
            return Decimal(v)
        return v


class OrderCreate(BaseModel):
    """Request model for order creation."""

    customer_id: int = Field(..., ge=1, description="Customer identifier")
    items: list[OrderItemCreate] = Field(
        ..., min_length=1, description="Order items array (min 1 item)"
    )

    @validator("items")
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError("At least one item is required")
        return v


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def create_order(
    order_create: OrderCreate,
    current_user: Customer = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new order in draft status.

    **End POST /api/v1/orders**
    - Requires valid JWT token with `customer:manage` permission
    - Customer must be eligible for order creation
    - At least one order item must be provided
    - Order starts in draft status with subtotal calculated from item prices
    """
    order_service = OrderService()
    order = order_service.create_order(
        customer_id=order_create.customer_id,
        items=[{
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        } for item in order_create.items],
        db_session=db,
    )

    return {
        "id": order.id,
        "status": order.status,
        "subtotal": float(order.subtotal) if order.subtotal else 0.0,
        "tax_amount": float(order.tax_amount) if order.tax_amount else 0.0,
        "total": float(order.total) if order.total else 0.0,
        "customer_id": order.customer_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "items": [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else 0.0,
                "line_total": float(item.line_total) if item.line_total else 0.0,
            }
            for item in order.items
        ] if hasattr(order, 'items') else [],
    }