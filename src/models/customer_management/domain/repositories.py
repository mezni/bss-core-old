"""Repository port for the customer aggregate."""

from __future__ import annotations

from typing import Protocol

from .entities import Customer
from .value_objects import CustomerStatus, CustomerType


class CustomerRepository(Protocol):
    """Persistence boundary for the customer aggregate.

    Implementations must persist the full aggregate (customer, contacts, and
    addresses) atomically and enforce optimistic concurrency on updates.
    """

    def add(self, customer: Customer) -> Customer:
        """Persist a new customer aggregate."""
        ...

    def get(self, customer_id: str) -> Customer | None:
        """Return a customer aggregate or ``None`` when it does not exist."""
        ...

    def update(self, customer: Customer, expected_version: int) -> Customer:
        """Persist changes when ``expected_version`` matches the stored version."""
        ...

    def search(
        self,
        *,
        q: str | None = None,
        customer_type: CustomerType | None = None,
        status: CustomerStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Customer], int]:
        """Return a page of matching customers and the total match count."""
        ...

    def exists_identity(
        self,
        customer_type: CustomerType,
        *,
        email: str | None = None,
        registration_number: str | None = None,
        exclude_id: str | None = None,
    ) -> bool:
        """Check type-scoped identity uniqueness."""
        ...
