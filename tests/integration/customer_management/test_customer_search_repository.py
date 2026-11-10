"""Integration tests for search and filtering over 10,000 rows."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from src.models.customer_management.domain.value_objects import (
    CustomerStatus,
    CustomerType,
)
from src.models.customer_management.infrastructure.orm import CustomerORM
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)

ROW_COUNT = 10_000


@pytest.fixture()
def populated_session(session: Session) -> Session:
    now = datetime.now(UTC)
    rows = []
    for index in range(ROW_COUNT):
        is_individual = index % 2 == 0
        rows.append(
            CustomerORM(
                id=f"customer-{index:05d}",
                customer_type=(
                    CustomerType.INDIVIDUAL.value
                    if is_individual
                    else CustomerType.BUSINESS.value
                ),
                display_name=f"Customer {index:05d}",
                first_name="Jane" if is_individual else None,
                last_name=f"Person{index:05d}" if is_individual else None,
                legal_name=None if is_individual else f"Customer {index:05d} LLC",
                email=f"jane{index:05d}@example.com" if is_individual else None,
                registration_number=None if is_individual else f"US-{index:07d}",
                status=(
                    CustomerStatus.ACTIVE.value
                    if index % 2 == 0
                    else CustomerStatus.INACTIVE.value
                ),
                version=1,
                created_at=now,
                updated_at=now,
            )
        )
    session.add_all(rows)
    session.commit()
    return session


@pytest.mark.performance
def test_search_and_filter_at_scale(populated_session: Session) -> None:
    repository = SQLAlchemyCustomerRepository(populated_session)

    page, total = repository.search(page=1, page_size=100)
    assert total == ROW_COUNT
    assert len(page) == 100

    individuals, individual_total = repository.search(
        customer_type=CustomerType.INDIVIDUAL, page=1, page_size=10
    )
    businesses, business_total = repository.search(
        customer_type=CustomerType.BUSINESS, page=1, page_size=10
    )
    assert individual_total == ROW_COUNT // 2
    assert business_total == ROW_COUNT // 2
    assert all(item.customer_type == CustomerType.INDIVIDUAL for item in individuals)
    assert all(item.customer_type == CustomerType.BUSINESS for item in businesses)

    active, active_total = repository.search(
        status=CustomerStatus.ACTIVE, page=1, page_size=10
    )
    assert active_total == ROW_COUNT // 2
    assert all(item.status == CustomerStatus.ACTIVE for item in active)

    matches, match_total = repository.search(q="Customer 00042", page=1, page_size=10)
    assert match_total == 1
    assert matches[0].display_name == "Customer 00042"

    missing, missing_total = repository.search(q="no-such-customer")
    assert missing_total == 0
    assert missing == []


@pytest.mark.performance
def test_pagination_is_stable_at_scale(populated_session: Session) -> None:
    repository = SQLAlchemyCustomerRepository(populated_session)

    first, total = repository.search(page=1, page_size=100)
    second, _ = repository.search(page=2, page_size=100)

    assert total == ROW_COUNT
    assert {item.id for item in first}.isdisjoint({item.id for item in second})
