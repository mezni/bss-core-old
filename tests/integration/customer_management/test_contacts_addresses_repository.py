"""Integration tests for contact and address persistence."""

from __future__ import annotations

import pytest

from src.models.customer_management.application.commands import (
    AddAddressCommand,
    AddContactCommand,
    CreateCustomerCommand,
    RemoveContactCommand,
    UpdateAddressCommand,
    UpdateContactCommand,
)
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.exceptions import DuplicatePrimaryContact
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerType,
)


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


def test_contact_and_address_roundtrip(service: CustomerService, customer) -> None:
    contact = service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com", True)
    )
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

    fetched = service.get(customer.id)

    assert fetched.version == 3
    assert fetched.eligible is True
    assert fetched.contacts[0].id == contact.id
    assert fetched.addresses[0].id == address.id
    assert fetched.addresses[0].country == "US"


def test_contact_and_address_updates_persist(
    service: CustomerService, customer
) -> None:
    contact = service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com")
    )
    address = service.add_address(
        AddAddressCommand(customer.id, "1 Main St", "Springfield", "62701", "US")
    )

    service.update_contact(
        UpdateContactCommand(
            customer.id,
            contact.id,
            version=3,
            changes={"value": "+1 555 0100", "contact_type": ContactType.PHONE},
        )
    )
    service.update_address(
        UpdateAddressCommand(
            customer.id,
            address.id,
            version=4,
            changes={"line1": "1 Main Street", "region": "IL"},
        )
    )

    fetched = service.get(customer.id)
    assert fetched.contacts[0].contact_type == ContactType.PHONE
    assert fetched.contacts[0].value == "+1 555 0100"
    assert fetched.addresses[0].line1 == "1 Main Street"
    assert fetched.addresses[0].region == "IL"


def test_removed_contact_is_not_persisted(
    service: CustomerService, customer
) -> None:
    contact = service.add_contact(
        AddContactCommand(customer.id, "Jane", ContactType.EMAIL, "jane@example.com")
    )

    service.remove_contact(RemoveContactCommand(customer.id, contact.id, version=2))

    fetched = service.get(customer.id)
    assert fetched.contacts == ()
    assert service.check_eligibility(customer.id).reasons == ("NO_CONTACT", "NO_ADDRESS")


def test_primary_contact_constraint_is_enforced(
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
