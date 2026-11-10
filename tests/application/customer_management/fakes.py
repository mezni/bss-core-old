"""In-memory repository fake for application-layer tests."""

from __future__ import annotations

from copy import deepcopy

from src.models.customer_management.domain.entities import Customer
from src.models.customer_management.domain.exceptions import (
    CustomerNotFound,
    StaleUpdate,
)
from src.models.customer_management.domain.value_objects import (
    CustomerStatus,
    CustomerType,
    normalize_email,
    normalize_registration_number,
)


class InMemoryCustomerRepository:
    """A deterministic repository fake that preserves aggregate versions."""

    def __init__(self) -> None:
        self.customers: dict[str, Customer] = {}

    def add(self, customer: Customer) -> Customer:
        stored = deepcopy(customer)
        self.customers[stored.id] = stored
        return deepcopy(stored)

    def get(self, customer_id: str) -> Customer | None:
        customer = self.customers.get(customer_id)
        return deepcopy(customer) if customer is not None else None

    def update(self, customer: Customer, expected_version: int) -> Customer:
        stored = self.customers.get(customer.id)
        if stored is None:
            raise CustomerNotFound(f"Customer {customer.id} was not found")
        if stored.version != expected_version:
            raise StaleUpdate(expected_version, stored.version)
        updated = deepcopy(customer)
        updated.version = expected_version + 1
        self.customers[updated.id] = updated
        return deepcopy(updated)

    def search(
        self,
        *,
        q: str | None = None,
        customer_type: CustomerType | None = None,
        status: CustomerStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Customer], int]:
        items = list(self.customers.values())
        if q:
            needle = q.strip().lower()
            items = [
                customer
                for customer in items
                if needle in customer.display_name.lower()
                or (customer.email is not None and needle in customer.email.lower())
                or (
                    customer.registration_number is not None
                    and needle in customer.registration_number.lower()
                )
            ]
        if customer_type is not None:
            items = [
                customer
                for customer in items
                if customer.customer_type == CustomerType(customer_type)
            ]
        if status is not None:
            items = [
                customer
                for customer in items
                if customer.status == CustomerStatus(status)
            ]
        items.sort(key=lambda customer: (customer.created_at, customer.id), reverse=True)
        total = len(items)
        offset = (page - 1) * page_size
        return [deepcopy(item) for item in items[offset : offset + page_size]], total

    def exists_identity(
        self,
        customer_type: CustomerType,
        *,
        email: str | None = None,
        registration_number: str | None = None,
        exclude_id: str | None = None,
    ) -> bool:
        if CustomerType(customer_type) == CustomerType.INDIVIDUAL:
            if not email:
                return False
            try:
                normalized = normalize_email(email)
            except ValueError:
                normalized = email.strip().lower()
            return any(
                customer.id != exclude_id
                and customer.customer_type == CustomerType.INDIVIDUAL
                and customer.email == normalized
                for customer in self.customers.values()
            )
        if not registration_number:
            return False
        try:
            normalized_registration = normalize_registration_number(registration_number)
        except ValueError:
            normalized_registration = registration_number.strip().upper()
        return any(
            customer.id != exclude_id
            and customer.customer_type == CustomerType.BUSINESS
            and customer.registration_number == normalized_registration
            for customer in self.customers.values()
        )
