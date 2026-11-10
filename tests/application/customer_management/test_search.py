"""Application tests for customer search, filtering, and pagination."""

from __future__ import annotations

import pytest

from src.models.customer_management.application.commands import CreateCustomerCommand
from src.models.customer_management.application.queries import CustomerSearchQuery
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.value_objects import (
    CustomerStatus,
    CustomerType,
)

from .fakes import InMemoryCustomerRepository


@pytest.fixture()
def service() -> CustomerService:
    return CustomerService(InMemoryCustomerRepository())


def seed(service: CustomerService) -> None:
    for index in range(25):
        if index % 2 == 0:
            service.create(
                CreateCustomerCommand(
                    customer_type=CustomerType.INDIVIDUAL,
                    display_name=f"Individual {index:02d}",
                    first_name="Jane",
                    last_name=f"Person{index:02d}",
                    email=f"jane{index:02d}@example.com",
                )
            )
        else:
            service.create(
                CreateCustomerCommand(
                    customer_type=CustomerType.BUSINESS,
                    display_name=f"Business {index:02d}",
                    legal_name=f"Business {index:02d} LLC",
                    registration_number=f"US-{index:06d}",
                )
            )


def test_search_by_display_name(service: CustomerService) -> None:
    seed(service)

    result = service.search(CustomerSearchQuery(q="Individual 04"))

    assert result.total == 1
    assert result.items[0].display_name == "Individual 04"


def test_search_by_email_and_registration(service: CustomerService) -> None:
    seed(service)

    by_email = service.search(CustomerSearchQuery(q="jane12@example.com"))
    by_registration = service.search(CustomerSearchQuery(q="US-000013"))

    assert by_email.total == 1
    assert by_registration.total == 1


def test_filter_by_type_and_status(service: CustomerService) -> None:
    seed(service)

    individuals = service.search(
        CustomerSearchQuery(customer_type=CustomerType.INDIVIDUAL)
    )
    businesses = service.search(CustomerSearchQuery(customer_type=CustomerType.BUSINESS))
    active = service.search(CustomerSearchQuery(status=CustomerStatus.ACTIVE))

    assert individuals.total == 13
    assert businesses.total == 12
    assert active.total == 25


def test_pagination_totals_and_non_overlapping_pages(
    service: CustomerService,
) -> None:
    seed(service)

    first = service.search(CustomerSearchQuery(page=1, page_size=10))
    second = service.search(CustomerSearchQuery(page=2, page_size=10))
    third = service.search(CustomerSearchQuery(page=3, page_size=10))

    assert first.total == 25
    assert len(first.items) == 10
    assert len(second.items) == 10
    assert len(third.items) == 5
    assert {item.id for item in first.items}.isdisjoint(
        {item.id for item in second.items}
    )
    assert {item.id for item in second.items}.isdisjoint(
        {item.id for item in third.items}
    )


def test_empty_search_returns_empty_page(service: CustomerService) -> None:
    seed(service)

    result = service.search(CustomerSearchQuery(q="does-not-exist"))

    assert result.total == 0
    assert result.items == ()


def test_page_size_is_clamped(service: CustomerService) -> None:
    seed(service)

    too_small = service.search(CustomerSearchQuery(page=0, page_size=0))
    too_large = service.search(CustomerSearchQuery(page_size=500))

    assert too_small.page == 1
    assert too_small.page_size == 1
    assert too_large.page_size == 100
