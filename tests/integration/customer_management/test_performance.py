"""Performance smoke test for search and filtering over 10,000 records."""

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

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
MAX_SEARCH_SECONDS = 5.0


@pytest.fixture()
def large_dataset(session: Session) -> Session:
    now = datetime.now(UTC)
    session.add_all(
        [
            CustomerORM(
                id=f"perf-{index:05d}",
                customer_type=(
                    CustomerType.INDIVIDUAL.value
                    if index % 2 == 0
                    else CustomerType.BUSINESS.value
                ),
                display_name=f"Perf Customer {index:05d}",
                first_name="Jane" if index % 2 == 0 else None,
                last_name=f"Person{index:05d}" if index % 2 == 0 else None,
                legal_name=None if index % 2 == 0 else f"Perf {index:05d} LLC",
                email=f"perf{index:05d}@example.com" if index % 2 == 0 else None,
                registration_number=None if index % 2 == 0 else f"REG-{index:07d}",
                status=(
                    CustomerStatus.ACTIVE.value
                    if index % 3
                    else CustomerStatus.INACTIVE.value
                ),
                version=1,
                created_at=now,
                updated_at=now,
            )
            for index in range(ROW_COUNT)
        ]
    )
    session.commit()
    return session


@pytest.mark.performance
def test_search_performance_smoke(large_dataset: Session) -> None:
    repository = SQLAlchemyCustomerRepository(large_dataset)

    start = perf_counter()
    page, total = repository.search(q="Perf Customer", page=1, page_size=50)
    elapsed = perf_counter() - start

    assert total == ROW_COUNT
    assert len(page) == 50
    assert elapsed < MAX_SEARCH_SECONDS


@pytest.mark.performance
def test_filter_performance_smoke(large_dataset: Session) -> None:
    repository = SQLAlchemyCustomerRepository(large_dataset)

    start = perf_counter()
    page, total = repository.search(
        customer_type=CustomerType.BUSINESS,
        status=CustomerStatus.ACTIVE,
        page=1,
        page_size=20,
    )
    elapsed = perf_counter() - start

    assert total > 0
    assert len(page) == 20
    assert all(item.customer_type == CustomerType.BUSINESS for item in page)
    assert elapsed < MAX_SEARCH_SECONDS
