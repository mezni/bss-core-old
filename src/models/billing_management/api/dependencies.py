"""Dependency wiring for the billing management API."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.domain.database import get_db
from src.models.order_management.api.dependencies import get_order_service
from src.models.order_management.application.service import OrderService

from ..application.service import BillingService
from ..infrastructure.order_adapter import OrderModuleAdapter
from ..infrastructure.repository import InvoiceRepository, PaymentRepository


def get_invoice_repository(
    session: Annotated[Session, Depends(get_db)],
) -> InvoiceRepository:
    return InvoiceRepository(session)


def get_payment_repository(
    session: Annotated[Session, Depends(get_db)],
) -> PaymentRepository:
    return PaymentRepository(session)


def get_billing_service(
    invoices: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
    payments: Annotated[PaymentRepository, Depends(get_payment_repository)],
    orders: Annotated[OrderService, Depends(get_order_service)],
) -> BillingService:
    """Build the billing service with persistence and order integration."""
    return BillingService(
        invoices=invoices,
        payments=payments,
        orders=OrderModuleAdapter(orders),
    )
