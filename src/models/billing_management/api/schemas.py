"""Pydantic request schemas for the billing management API."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class InvoiceCreate(BaseModel):
    """Payload for generating an invoice from an order."""

    order_id: str | None = Field(None, description="Confirmed order ID")
    reference_id: str | None = Field(
        None, description="Alias for order_id per the billing contract"
    )
    due_days: int = Field(30, gt=0, description="Days until the invoice is due")

    @model_validator(mode="after")
    def _resolve_order_id(self) -> InvoiceCreate:
        if not (self.order_id or self.reference_id):
            raise ValueError("order_id or reference_id is required")
        return self

    @property
    def resolved_order_id(self) -> str:
        return self.order_id or self.reference_id or ""


class InvoiceUpdate(BaseModel):
    """Payload for updating an invoice status."""

    version: int = Field(..., ge=1)
    status: str = Field(..., description="Target status; only 'paid' is supported")
    payment_method: str | None = Field(None, description="card | bank_transfer | cash")


class PaymentCreate(BaseModel):
    """Payload for processing a payment against an invoice."""

    invoice_id: str = Field(..., description="Pending invoice ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: str = Field(..., description="card | bank_transfer | cash")
    transaction_id: str | None = Field(None, description="Processor transaction ID")
