"""Application tests for contact and address use cases."""

from __future__ import annotations

import pytest

from src.models.customer_management.application.commands import (
    AddAddressCommand,
    AddContactCommand,
    CreateCustomerCommand,
    RemoveAddressCommand,
    RemoveContactCommand,
    UpdateAddressCommand,
    UpdateContactCommand,
)
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.exceptions import (
    AddressNotFound,
    ContactNotFound,
    DuplicatePrimaryContact,
    StaleUpdate,
)
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerType,
)

from .fakes import InMemoryCustomerRepository


@pytest.fixture()
def service() -> CustomerService:
    return CustomerService(InMemoryCustomerRepository())


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


def test_add_update_remove_contact(service: CustomerService, customer) -> None:
    contact = service.add_contact(
        AddContactCommand(
            customer.id, "Jane", ContactType.EMAIL, "jane@example.com", True
        )
    )
    assert contact.is_primary is True

    updated = service.update_contact(
        UpdateContactCommand(
            customer_id=customer.id,
            contact_id=contact.id,
            version=2,
            changes={"value": "+1 555 0100", "contact_type": ContactType.PHONE},
        )
    )
    assert updated.value == "+1 555 0100"
    assert updated.contact_type == ContactType.PHONE

    service.remove_contact(
        RemoveContactCommand(customer.id, contact.id, version=3)
    )

    fetched = service.get(customer.id)
    assert fetched.contacts == ()
    assert fetched.version == 4
    assert "NO_CONTACT" in service.check_eligibility(customer.id).reasons


def test_add_update_remove_address(service: CustomerService, customer) -> None:
    address = service.add_address(
        AddAddressCommand(
            customer.id,
            "1 Main St",
            "Springfield",
            "62701",
            "US",
            label="Billing",
            is_primary=True,
        )
    )
    assert address.label == "Billing"

    updated = service.update_address(
        UpdateAddressCommand(
            customer_id=customer.id,
            address_id=address.id,
            version=2,
            changes={"line1": "1 Main Street", "region": "IL"},
        )
    )
    assert updated.line1 == "1 Main Street"
    assert updated.region == "IL"

    service.remove_address(
        RemoveAddressCommand(customer.id, address.id, version=3)
    )

    fetched = service.get(customer.id)
    assert fetched.addresses == ()
    assert "NO_ADDRESS" in service.check_eligibility(customer.id).reasons


def test_duplicate_primary_contact_is_rejected(
    service: CustomerService, customer
) -> None:
    service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com", True)
    )

    with pytest.raises(DuplicatePrimaryContact):
        service.add_contact(
            AddContactCommand(
                customer.id, "Jane", ContactType.PHONE, "+1 555 0100", True
            )
        )


def test_stale_child_update_is_rejected(service: CustomerService, customer) -> None:
    contact = service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com")
    )

    with pytest.raises(StaleUpdate):
        service.update_contact(
            UpdateContactCommand(
                customer_id=customer.id,
                contact_id=contact.id,
                version=1,
                changes={"value": "other@example.com"},
            )
        )


def test_missing_child_raises_not_found(service: CustomerService, customer) -> None:
    with pytest.raises(ContactNotFound):
        service.remove_contact(RemoveContactCommand(customer.id, "missing", 1))

    with pytest.raises(AddressNotFound):
        service.remove_address(RemoveAddressCommand(customer.id, "missing", 1))
