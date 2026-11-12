"""Invoice API router (order-to-invoice workflow)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.models.identity_access.api.dependencies import (
    require_user_view,
    require_workflow_permission,
)
from src.models.identity_access.api.permissions import (
    USER_BILLING,
    WORKFLOW_ORDER_TO_INVOICE,
)

from ..application.dto import InvoiceDTO
from ..application.service import BillingService
from ..domain.exceptions import InvoiceValidationError
from .dependencies import get_billing_service
from .schemas import InvoiceCreate, InvoiceUpdate

router = APIRouter(prefix="/api/v1/invoices", tags=["billing_management"])

billing_guard = require_workflow_permission(WORKFLOW_ORDER_TO_INVOICE, USER_BILLING)

BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]


@router.post(
    "",
    summary="Generate invoice",
    status_code=201,
    dependencies=[Depends(billing_guard)],
)
def create_invoice(payload: InvoiceCreate, service: BillingServiceDep) -> InvoiceDTO:
    """Generate an invoice for a confirmed order."""
    return service.generate_invoice(
        order_id=payload.resolved_order_id, due_days=payload.due_days
    )


@router.get("", summary="List invoices", dependencies=[Depends(require_user_view)])
def list_invoices(
    service: BillingServiceDep,
    customer_id: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """List invoices with optional filters and pagination."""
    items, total = service.list_invoices(
        customer_id=customer_id, status=status, page=page, page_size=page_size
    )
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get(
    "/{invoice_id}",
    summary="Get invoice",
    dependencies=[Depends(require_user_view)],
)
def get_invoice(invoice_id: str, service: BillingServiceDep) -> InvoiceDTO:
    """Retrieve a single invoice by ID."""
    return service.get_invoice(invoice_id)


@router.patch(
    "/{invoice_id}",
    summary="Update invoice status",
    dependencies=[Depends(billing_guard)],
)
def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    service: BillingServiceDep,
) -> InvoiceDTO:
    """Transition an invoice to paid."""
    if payload.status != "paid":
        raise InvoiceValidationError("Only transition to 'paid' is supported")
    if not payload.payment_method:
        raise InvoiceValidationError("payment_method is required when marking paid")
    return service.mark_invoice_paid(invoice_id, payload.payment_method)
