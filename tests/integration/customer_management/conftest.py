"""Fixtures for SQLite-backed customer integration tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.infrastructure.orm import Base
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)


@pytest.fixture()
def engine(tmp_path) -> Iterator[Engine]:
    database = tmp_path / "customers.db"
    test_engine = create_engine(
        f"sqlite:///{database}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as db_session:
        yield db_session


@pytest.fixture()
def repository(session: Session) -> SQLAlchemyCustomerRepository:
    return SQLAlchemyCustomerRepository(session)


@pytest.fixture()
def service(repository: SQLAlchemyCustomerRepository) -> CustomerService:
    return CustomerService(repository)
