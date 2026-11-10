"""Read-side queries for customer management."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.value_objects import CustomerStatus, CustomerType
from .dto import CustomerListDTO


@dataclass(frozen=True)
class CustomerSearchQuery:
    q: str | None = None
    customer_type: CustomerType | None = None
    status: CustomerStatus | None = None
    page: int = 1
    page_size: int = 20


__all__ = ["CustomerListDTO", "CustomerSearchQuery"]
