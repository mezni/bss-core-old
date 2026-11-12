"""Dependency wiring for the order management API."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from src.domain.database import get_db
from src.models.customer_management.application.service import CustomerEligibilityAdapter
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)

from ..application.service import OrderService
from ..infrastructure.repository import SQLAlchemyOrderRepository


def get_order_repository(
    session: Session = Depends(get_db),
) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(session)


def get_order_service(
    session: Session = Depends(get_db),
    repository: SQLAlchemyOrderRepository = Depends(get_order_repository),
) -> OrderService:
    """Build the order service with persistence and customer eligibility."""
    eligibility = CustomerEligibilityAdapter(SQLAlchemyCustomerRepository(session))
    return OrderService(repository=repository, eligibility=eligibility)
