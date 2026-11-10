"""Integration tests for customer repository persistence."""

from __future__ import annotations

import pytest

from src.models.customer_management.application.commands import (
    AddAddressCommand,
    AddContactCommand,
    CreateCustomerCommand,
    DeactivateCustomerCommand,
)
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.entities import Customer
from src.models.customer_management.domain.exceptions import (
    DuplicateCustomer,
    StaleUpdate,
)
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerStatus,
    CustomerType,
)
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)


def make_customer(email: str = "jane@example.com") -> Customer:
    return Customer.create(
        CustomerType.INDIVIDUAL,
        "Jane Doe",
        first_name="Jane",
        last_name="Doe",
        email=email,
    )


def test_add_and_get_roundtrip(repository: SQLAlchemyCustomerRepository) -> None:
    saved = repository.add(make_customer())

    fetched = repository.get(saved.id)

    assert fetched is not None
    assert fetched.id == saved.id
    assert fetched.email == "jane@example.com"
    assert fetched.version == 1


def test_update_increments_version_and_persists(
    repository: SQLAlchemyCustomerRepository,
) -> None:
    saved = repository.add(make_customer())
    saved.update(display_name="Jane A. Doe")

    updated = repository.update(saved, expected_version=1)

    assert updated.display_name == "Jane A. Doe"
    assert updated.version == 2
    assert repository.get(saved.id).display_name == "Jane A. Doe"


def test_stale_version_is_rejected(repository: SQLAlchemyCustomerRepository) -> None:
    saved = repository.add(make_customer())
    saved.update(display_name="First")
    repository.update(saved, expected_version=1)

    stale = repository.get(saved.id)
    stale.update(display_name="Second")

    with pytest.raises(StaleUpdate):
        repository.update(stale, expected_version=1)


def test_duplicate_individual_email_is_rejected(
    repository: SQLAlchemyCustomerRepository,
) -> None:
    repository.add(make_customer())

    with pytest.raises(DuplicateCustomer):
        repository.add(make_customer(email="JANE@example.com"))


def test_duplicate_business_registration_is_rejected(
    repository: SQLAlchemyCustomerRepository,
) -> None:
    first = Customer.create(
        CustomerType.BUSINESS,
        "Acme",
        legal_name="Acme Corporation",
        registration_number="US-123456",
    )
    repository.add(first)

    with pytest.raises(DuplicateCustomer):
        repository.add(
            Customer.create(
                CustomerType.BUSINESS,
                "Acme Two",
                legal_name="Acme Two",
                registration_number="us-123456",
            )
        )


def test_business_may_share_email_with_individual(
    repository: SQLAlchemyCustomerRepository,
) -> None:
    repository.add(make_customer())

    business = repository.add(
        Customer.create(
            CustomerType.BUSINESS,
            "Acme",
            legal_name="Acme Corporation",
            registration_number="US-123456",
            email="jane@example.com",
        )
    )

    assert business.email == "jane@example.com"


def test_deactivation_preserves_children(service: CustomerService) -> None:
    created = service.create(
        CreateCustomerCommand(
            customer_type=CustomerType.INDIVIDUAL,
            display_name="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
    )
    service.add_contact(
        AddContactCommand(
            created.id, "Jane", ContactType.EMAIL, "jane@example.com", True
        )
    )
    service.add_address(
        AddAddressCommand(
            created.id,
            "1 Main St",
            "Springfield",
            "62701",
            "US",
            is_primary=True,
        )
    )

    deactivated = service.deactivate(DeactivateCustomerCommand(created.id))

    assert deactivated.status == CustomerStatus.INACTIVE
    assert len(deactivated.contacts) == 1
    assert len(deactivated.addresses) == 1
