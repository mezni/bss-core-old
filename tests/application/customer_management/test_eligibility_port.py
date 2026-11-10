"""Application tests for the downstream customer eligibility port."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.models.customer_management.application.commands import (
    AddAddressCommand,
    AddContactCommand,
    CreateCustomerCommand,
    DeactivateCustomerCommand,
)
from src.models.customer_management.application.dto import (
    CustomerEligibilityDTO,
    CustomerSummaryDTO,
)
from src.models.customer_management.application.service import (
    CustomerEligibilityAdapter,
)
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.exceptions import CustomerNotFound
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerStatus,
    CustomerType,
)

from .fakes import InMemoryCustomerRepository


@pytest.fixture()
def repository() -> InMemoryCustomerRepository:
    return InMemoryCustomerRepository()


@pytest.fixture()
def service(repository: InMemoryCustomerRepository) -> CustomerService:
    return CustomerService(repository)


@pytest.fixture()
def port(repository: InMemoryCustomerRepository) -> CustomerEligibilityAdapter:
    return CustomerEligibilityAdapter(repository)


@pytest.fixture()
def customer(service: CustomerService):
    return service.create(
        CreateCustomerCommand(
            customer_type=CustomerType.INDIVIDUAL,
            display_name="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
    )


def test_get_summary_returns_none_for_missing(port: CustomerEligibilityAdapter) -> None:
    assert port.get_summary("missing") is None


def test_get_summary_returns_current_data(
    port: CustomerEligibilityAdapter, customer
) -> None:
    summary = port.get_summary(customer.id)

    assert isinstance(summary, CustomerSummaryDTO)
    assert summary.id == customer.id
    assert summary.customer_type == CustomerType.INDIVIDUAL
    assert summary.status == CustomerStatus.ACTIVE
    assert summary.eligible is False
    assert summary.version == 1


def test_eligibility_reasons_are_complete(
    service: CustomerService, port: CustomerEligibilityAdapter, customer
) -> None:
    initial = port.check_eligibility(customer.id)
    assert initial.eligible is False
    assert initial.reasons == ("NO_CONTACT", "NO_ADDRESS")

    service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com")
    )
    no_address = port.check_eligibility(customer.id)
    assert no_address.reasons == ("NO_ADDRESS",)

    service.add_address(
        AddAddressCommand(customer.id, "1 Main St", "Springfield", "62701", "US")
    )
    eligible = port.check_eligibility(customer.id)
    assert eligible.eligible is True
    assert eligible.reasons == ()

    service.deactivate(DeactivateCustomerCommand(customer.id))
    inactive = port.check_eligibility(customer.id)
    assert inactive.eligible is False
    assert inactive.reasons == ("INACTIVE",)


def test_missing_customer_raises_not_found(port: CustomerEligibilityAdapter) -> None:
    with pytest.raises(CustomerNotFound):
        port.check_eligibility("missing")


def test_dtos_are_immutable_and_orm_free(
    port: CustomerEligibilityAdapter, customer
) -> None:
    summary = port.get_summary(customer.id)
    eligibility = port.check_eligibility(customer.id)

    assert isinstance(eligibility, CustomerEligibilityDTO)
    assert not hasattr(summary, "_sa_instance_state")
    assert not hasattr(eligibility, "_sa_instance_state")
    with pytest.raises(FrozenInstanceError):
        summary.display_name = "Changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        eligibility.eligible = True  # type: ignore[misc]
