"""Application tests for customer lifecycle use cases."""

from __future__ import annotations

import pytest

from src.models.customer_management.application.commands import (
    CreateCustomerCommand,
    DeactivateCustomerCommand,
    ReactivateCustomerCommand,
    UpdateCustomerCommand,
)
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.exceptions import (
    CustomerNotFound,
    DuplicateCustomer,
    StaleUpdate,
)
from src.models.customer_management.domain.value_objects import (
    CustomerStatus,
    CustomerType,
)

from .fakes import InMemoryCustomerRepository


@pytest.fixture()
def service() -> CustomerService:
    return CustomerService(InMemoryCustomerRepository())


def create_individual(service: CustomerService, email: str = "jane@example.com"):
    return service.create(
        CreateCustomerCommand(
            customer_type=CustomerType.INDIVIDUAL,
            display_name="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            email=email,
        )
    )


def test_create_and_get_customer(service: CustomerService) -> None:
    created = create_individual(service)

    assert created.version == 1
    assert created.status == CustomerStatus.ACTIVE
    assert created.eligible is False

    fetched = service.get(created.id)
    assert fetched.id == created.id
    assert fetched.email == "jane@example.com"


def test_update_increments_version(service: CustomerService) -> None:
    created = create_individual(service)

    updated = service.update(
        UpdateCustomerCommand(
            customer_id=created.id,
            version=created.version,
            changes={"display_name": "Jane A. Doe"},
        )
    )

    assert updated.display_name == "Jane A. Doe"
    assert updated.version == created.version + 1


def test_stale_update_is_rejected(service: CustomerService) -> None:
    created = create_individual(service)
    service.update(
        UpdateCustomerCommand(
            customer_id=created.id,
            version=created.version,
            changes={"display_name": "Jane A. Doe"},
        )
    )

    with pytest.raises(StaleUpdate) as error:
        service.update(
            UpdateCustomerCommand(
                customer_id=created.id,
                version=created.version,
                changes={"display_name": "Stale"},
            )
        )

    assert error.value.current_version == created.version + 1


def test_deactivate_and_reactivate(service: CustomerService) -> None:
    created = create_individual(service)

    inactive = service.deactivate(DeactivateCustomerCommand(created.id))
    assert inactive.status == CustomerStatus.INACTIVE
    assert inactive.version == created.version + 1

    active = service.reactivate(ReactivateCustomerCommand(created.id))
    assert active.status == CustomerStatus.ACTIVE
    assert active.version == inactive.version + 1


def test_duplicate_individual_email_is_rejected(service: CustomerService) -> None:
    create_individual(service)

    with pytest.raises(DuplicateCustomer):
        create_individual(service, email="JANE@example.com")


def test_business_may_share_email_with_individual(service: CustomerService) -> None:
    create_individual(service)

    business = service.create(
        CreateCustomerCommand(
            customer_type=CustomerType.BUSINESS,
            display_name="Acme",
            legal_name="Acme Corporation",
            registration_number="US-123456",
            email="jane@example.com",
        )
    )

    assert business.customer_type == CustomerType.BUSINESS


def test_missing_customer_raises_not_found(service: CustomerService) -> None:
    with pytest.raises(CustomerNotFound):
        service.get("does-not-exist")
