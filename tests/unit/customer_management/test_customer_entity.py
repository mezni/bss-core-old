"""Unit tests for customer lifecycle invariants."""

from __future__ import annotations

import pytest

from src.models.customer_management.domain.entities import Customer
from src.models.customer_management.domain.exceptions import InvalidCustomer
from src.models.customer_management.domain.value_objects import (
    ContactType,
    CustomerStatus,
    CustomerType,
    EligibilityReason,
)


def make_individual(**overrides) -> Customer:
    values = {
        "customer_type": CustomerType.INDIVIDUAL,
        "display_name": "Jane Doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "Jane.Doe@Example.com",
    }
    values.update(overrides)
    return Customer.create(**values)


def test_create_individual_normalizes_identity_and_defaults() -> None:
    customer = make_individual()

    assert customer.status == CustomerStatus.ACTIVE
    assert customer.version == 1
    assert customer.email == "jane.doe@example.com"
    assert customer.eligible is False
    assert customer.eligibility_reasons() == (
        EligibilityReason.NO_CONTACT,
        EligibilityReason.NO_ADDRESS,
    )


@pytest.mark.parametrize("field", ["first_name", "last_name", "email"])
def test_individual_requires_type_specific_fields(field: str) -> None:
    with pytest.raises(InvalidCustomer):
        make_individual(**{field: None})


def test_business_requires_legal_name_and_registration() -> None:
    with pytest.raises(InvalidCustomer):
        Customer.create(
            CustomerType.BUSINESS,
            "Acme",
            legal_name="Acme Corp",
        )
    with pytest.raises(InvalidCustomer):
        Customer.create(
            CustomerType.BUSINESS,
            "Acme",
            registration_number="US-123",
        )


def test_business_may_have_a_general_email() -> None:
    customer = Customer.create(
        CustomerType.BUSINESS,
        "Acme",
        legal_name="Acme Corporation",
        registration_number="us-123456",
        email="Accounts@Acme.Example",
    )

    assert customer.registration_number == "US-123456"
    assert customer.email == "accounts@acme.example"
    assert customer.first_name is None
    assert customer.last_name is None


def test_deactivate_and_reactivate_preserve_children() -> None:
    customer = make_individual()
    customer.add_contact("Jane", ContactType.EMAIL, "jane@example.com", is_primary=True)
    customer.add_address("1 Main St", "Springfield", "62701", "US", is_primary=True)
    assert customer.eligible is True

    customer.deactivate()
    assert customer.status == CustomerStatus.INACTIVE
    assert customer.eligibility_reasons() == (EligibilityReason.INACTIVE,)
    assert len(customer.contacts) == 1
    assert len(customer.addresses) == 1

    customer.reactivate()
    assert customer.status == CustomerStatus.ACTIVE
    assert customer.eligible is True


def test_update_revalidates_and_changes_timestamp() -> None:
    customer = make_individual()
    before = customer.updated_at

    customer.update(display_name="Jane A. Doe", email="JANE.A@EXAMPLE.COM")

    assert customer.display_name == "Jane A. Doe"
    assert customer.email == "jane.a@example.com"
    assert customer.updated_at >= before
    assert customer.version == 1


def test_invalid_contact_and_address_are_rejected() -> None:
    customer = make_individual()

    with pytest.raises(InvalidCustomer):
        customer.add_contact("Jane", ContactType.EMAIL, "not-an-email")
    with pytest.raises(InvalidCustomer):
        customer.add_address("", "Springfield", "62701", "US")
    with pytest.raises(InvalidCustomer):
        customer.add_address("1 Main St", "Springfield", "62701", "USA")
