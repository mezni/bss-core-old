"""Fixtures for customer API contract tests."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.health import app
from src.domain.database import get_db
from src.models.customer_management.infrastructure.orm import Base

TEST_SECRET = "bss-core-test-secret-0123456789abcdef"
os.environ["BSS_JWT_SECRET"] = TEST_SECRET


@pytest.fixture()
def api_engine(tmp_path) -> Iterator[Engine]:
    database = tmp_path / "api.db"
    test_engine = create_engine(
        f"sqlite:///{database}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def api_session_factory(api_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=api_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client(api_session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        session = api_session_factory()
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
    def _headers(*permissions: str) -> dict[str, str]:
        token = jwt.encode(
            {
                "sub": "contract-test-user",
                "permissions": list(permissions) or ["customer:view", "customer:manage"],
            },
            TEST_SECRET,
            algorithm="HS256",
        )
        return {"Authorization": f"Bearer {token}"}

    return _headers
