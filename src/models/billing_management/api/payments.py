"""Payment API router (invoice-to-payment workflow)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from src.models.identity_access.api.dependencies import (
    require_user_view,
    require_workflow_permission,
)
from src.models.identity_access.api.permissions import (
    USER_BILLING,
    WORKFLOW_INVOICE_TO_PAYMENT,
)

from ..application.dto import PaymentDTO
from ..application.service import BillingService
from .dependencies import get_billing_service
from .schemas import PaymentCreate

router = APIRouter(prefix="/api/v1/payments", tags=["billing_management"])

billing_guard = require_workflow_permission(WORKFLOW_INVOICE_TO_PAYMENT, USER_BILLING)

BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]


@router.post(
    "",
    summary="Process payment",
    status_code=201,
    dependencies=[Depends(billing_guard)],
)
def create_payment(payload: PaymentCreate, service: BillingServiceDep) -> PaymentDTO:
    """Process a payment against a pending invoice."""
    return service.process_payment(
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        transaction_id=payload.transaction_id,
    )


@router.get(
    "/{payment_id}",
    summary="Get payment",
    dependencies=[Depends(require_user_view)],
)
def get_payment(payment_id: str, service: BillingServiceDep) -> PaymentDTO:
    """Retrieve a payment by ID."""
    return service.get_payment(payment_id)
