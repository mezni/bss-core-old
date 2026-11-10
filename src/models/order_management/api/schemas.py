"""Pydantic models for order management API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, validator


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""
    description: str = Field(min_length=1, description="Item description")
    quantity: float = Field(gt=0, description="Item quantity")
    unit_price: float = Field(ge=0, description="Unit price")

    @validator("description")
    def description_not_empty(cls, v: str) -> str:
        """Ensure description is not just whitespace."""
        if not v.strip():
            raise ValueError("Description is required")
        return v.strip()


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    customer_id: str = Field(..., description="Customer ID")
    items: list[OrderItemCreate] = Field(
        min_length=1,
        description="At least one order item required",
    )

    @validator("items")
    def at_least_one_item(cls, v: list[Any]) -> list[Any]:
        """Ensure at least one item is provided."""
        if len(v) < 1:
            raise ValueError("At least one order item is required")
        return v


class OrderResponse(BaseModel):
    """Schema for order creation response."""
    id: str = Field(..., description="Order ID")
    status: str = Field(default="draft", description="Order status")
    subtotal: float = Field(..., description="Order subtotal")
    tax_amount: float = Field(..., description="Tax amount")
    total: float = Field(..., description="Order total")
    version: int = Field(default=1, description="Optimistic concurrency version")


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str = Field(..., description="Target status")
    version: int = Field(..., ge=1, description="Current version for optimistic concurrency")