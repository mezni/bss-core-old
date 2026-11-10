"""Unit tests for individual/business type rules and type changes."""

from __future__ import annotations

import pytest

from src.models.customer_management.domain.entities import Customer
from src.models.customer_management.domain.exceptions import InvalidCustomer
from src.models.customer_management.domain.value_objects import CustomerType


def individual() -> Customer:
    return Customer.create(
        CustomerType.INDIVIDUAL,
        "Jane Doe",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
    )


def business() -> Customer:
    return Customer.create(
        CustomerType.BUSINESS,
        "Acme",
        legal_name="Acme Corporation",
        registration_number="US-123456",
    )


def test_individual_rejects_business_only_identity() -> None:
    customer = individual()
    assert customer.registration_number is None
    assert customer.legal_name is None


def test_business_rejects_individual_only_identity() -> None:
    customer = business()
    assert customer.first_name is None
    assert customer.last_name is None


def test_invalid_registration_number_is_rejected() -> None:
    with pytest.raises(InvalidCustomer):
        Customer.create(
            CustomerType.BUSINESS,
            "Acme",
            legal_name="Acme Corporation",
            registration_number="not valid!",
        )


def test_change_individual_to_business() -> None:
    customer = individual()

    customer.change_type(
        CustomerType.BUSINESS,
        legal_name="Acme Corporation",
        registration_number="us-654321",
    )

    assert customer.customer_type == CustomerType.BUSINESS
    assert customer.legal_name == "Acme Corporation"
    assert customer.registration_number == "US-654321"
    assert customer.first_name is None
    assert customer.last_name is None
    assert customer.email == "jane@example.com"


def test_change_individual_to_business_requires_business_fields() -> None:
    customer = individual()

    with pytest.raises(InvalidCustomer):
        customer.change_type(CustomerType.BUSINESS)


def test_change_business_to_individual() -> None:
    customer = business()

    customer.change_type(
        CustomerType.INDIVIDUAL,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )

    assert customer.customer_type == CustomerType.INDIVIDUAL
    assert customer.first_name == "John"
    assert customer.last_name == "Doe"
    assert customer.email == "john@example.com"
    assert customer.legal_name is None
    assert customer.registration_number is None


def test_change_business_to_individual_requires_individual_fields() -> None:
    customer = business()

    with pytest.raises(InvalidCustomer):
        customer.change_type(CustomerType.INDIVIDUAL)


def test_changing_to_same_type_is_a_noop() -> None:
    customer = individual()
    before = customer.updated_at

    customer.change_type(CustomerType.INDIVIDUAL)

    assert customer.customer_type == CustomerType.INDIVIDUAL
    assert customer.updated_at == before
