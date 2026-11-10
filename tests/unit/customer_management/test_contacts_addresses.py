"""Unit tests for contact and address invariants."""

from __future__ import annotations

import pytest

from src.models.customer_management.domain.entities import Customer
from src.models.customer_management.domain.exceptions import (
    AddressNotFound,
    ContactNotFound,
    DuplicatePrimaryAddress,
    DuplicatePrimaryContact,
    InvalidCustomer,
)
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerType,
    EligibilityReason,
)


@pytest.fixture()
def customer() -> Customer:
    return Customer.create(
        CustomerType.INDIVIDUAL,
        "Jane Doe",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
    )


def test_multiple_contacts_with_single_primary(customer: Customer) -> None:
    primary = customer.add_contact(
        "Jane", ContactType.EMAIL, "Jane@Example.com", is_primary=True
    )
    secondary = customer.add_contact("Jane", ContactType.PHONE, "+1 555 0100")

    assert primary.value == "jane@example.com"
    assert secondary.value == "+1 555 0100"
    assert len(customer.contacts) == 2
    assert sum(contact.is_primary for contact in customer.contacts) == 1


def test_second_primary_contact_is_rejected(customer: Customer) -> None:
    customer.add_contact("Jane", ContactType.EMAIL, "jane@example.com", is_primary=True)

    with pytest.raises(DuplicatePrimaryContact):
        customer.add_contact(
            "Jane", ContactType.PHONE, "+1 555 0100", is_primary=True
        )


def test_contact_update_and_removal(customer: Customer) -> None:
    contact = customer.add_contact("Jane", ContactType.EMAIL, "jane@example.com")

    customer.update_contact(
        contact.id,
        contact_type=ContactType.PHONE,
        value="+1 555 0199",
        name="Jane Doe",
    )
    assert customer.contacts[0].contact_type == ContactType.PHONE
    assert customer.contacts[0].value == "+1 555 0199"

    customer.remove_contact(contact.id)
    assert customer.contacts == []

    with pytest.raises(ContactNotFound):
        customer.remove_contact(contact.id)


def test_address_validation_and_primary_rules(customer: Customer) -> None:
    address = customer.add_address(
        "1 Main St", "Springfield", "62701", "us", is_primary=True
    )
    assert address.country == "US"

    with pytest.raises(DuplicatePrimaryAddress):
        customer.add_address("2 Main St", "Springfield", "62702", "US", is_primary=True)

    with pytest.raises(InvalidCustomer):
        customer.add_address("", "Springfield", "62702", "US")


def test_address_update_and_removal(customer: Customer) -> None:
    address = customer.add_address("1 Main St", "Springfield", "62701", "US")

    customer.update_address(address.id, line1="1 Main Street", region="IL")
    assert customer.addresses[0].line1 == "1 Main Street"
    assert customer.addresses[0].region == "IL"

    customer.remove_address(address.id)
    assert customer.addresses == []

    with pytest.raises(AddressNotFound):
        customer.remove_address(address.id)


def test_eligibility_tracks_contacts_and_addresses(customer: Customer) -> None:
    contact = customer.add_contact("Jane", ContactType.EMAIL, "jane@example.com")
    address = customer.add_address("1 Main St", "Springfield", "62701", "US")
    assert customer.eligible is True

    customer.remove_contact(contact.id)
    assert customer.eligibility_reasons() == (EligibilityReason.NO_CONTACT,)

    customer.add_contact("Jane", ContactType.EMAIL, "jane@example.com")
    customer.remove_address(address.id)
    assert customer.eligibility_reasons() == (EligibilityReason.NO_ADDRESS,)
