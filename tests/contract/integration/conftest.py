"""Shared fixtures for cross-module integration contract tests.

App fixture on a temporary database with JWT minting helpers for the four
workflow permission flavors (``user:view``, ``user:billing``,
``user:admin``, ``customer:manage``), following
``tests/contract/customer_management/conftest.py``.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.health import app
from src.domain.database import get_db
from src.models.billing_management.infrastructure.orm import Base as BillingBase
from src.models.customer_management.infrastructure.orm import Base as CustomerBase
from src.models.order_management.infrastructure.orm import Base as OrderBase
from src.models.shipment_management.infrastructure.orm import Base as ShipmentBase

TEST_SECRET = "bss-core-test-secret-0123456789abcdef"
os.environ["BSS_JWT_SECRET"] = TEST_SECRET

ALL_MODULE_BASES = (CustomerBase, OrderBase, ShipmentBase, BillingBase)


def _combined_metadata() -> MetaData:
    """Single metadata holding every module table so cross-module FKs resolve."""
    combined = MetaData()
    for base in ALL_MODULE_BASES:
        for table in base.metadata.tables.values():
            table.to_metadata(combined)
    return combined


@pytest.fixture()
def integration_engine(tmp_path) -> Iterator[Engine]:
    database = tmp_path / "integration.db"
    test_engine = create_engine(
        f"sqlite:///{database}", connect_args={"check_same_thread": False}
    )
    _combined_metadata().create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def integration_session_factory(
    integration_engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(bind=integration_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client(
    integration_session_factory: sessionmaker[Session],
) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        session = integration_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers() -> Callable[..., dict[str, str]]:
    """Mint bearer headers carrying the given permissions."""

    def _headers(*permissions: str) -> dict[str, str]:
        token = jwt.encode(
            {
                "sub": "integration-test-user",
                "permissions": list(permissions),
            },
            TEST_SECRET,
            algorithm="HS256",
        )
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture()
def view_headers(auth_headers: Callable[..., dict[str, str]]) -> dict[str, str]:
    """Token granting the customer-to-order workflow permission."""
    return auth_headers("user:view")


@pytest.fixture()
def billing_headers(auth_headers: Callable[..., dict[str, str]]) -> dict[str, str]:
    """Token granting the order-to-invoice and invoice-to-payment workflows."""
    return auth_headers("user:billing")


@pytest.fixture()
def admin_headers(auth_headers: Callable[..., dict[str, str]]) -> dict[str, str]:
    """Token granting every workflow (full access)."""
    return auth_headers("user:admin")


@pytest.fixture()
def customer_manage_headers(auth_headers: Callable[..., dict[str, str]]) -> dict[str, str]:
    """Token granting the customer management module permission."""
    return auth_headers("customer:manage")
