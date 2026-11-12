import pytest


@pytest.fixture(scope="session")
def db_session():
    """Session-scoped database fixture."""
    import os
    import sqlite3

    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/bss_core.db")
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def db(db_session):
    """Function-scoped database fixture."""
    conn = db_session
    conn.execute("PRAGMA journal_mode=WAL")
    yield conn
    conn.rollback()


@pytest.fixture()
def dashboard_client(tmp_path):
    """TestClient for the consolidated app with a hermetic dashboard database."""
    from collections.abc import Iterator

    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session, sessionmaker

    from src.api.health import app
    from src.domain.database import get_db
    from src.models.dashboard_metric import Base as DashboardBase
    from src.models.dashboard_metric import DashboardMetric
    from src.models.reporting_period import Base as ReportingBase

    engine: Engine = create_engine(
        f"sqlite:///{tmp_path / 'dashboard.db'}",
        connect_args={"check_same_thread": False},
    )
    DashboardBase.metadata.create_all(engine)
    ReportingBase.metadata.create_all(engine)

    from datetime import UTC, datetime

    now = datetime.now(UTC)
    with sessionmaker(bind=engine)() as session:
        session.add_all(
            [
                DashboardMetric(
                    metric_name="billing.outstanding_balance",
                    value=1500.00,
                    unit="USD",
                    aggregation_type="sum",
                    date_range_start=now,
                    date_range_end=now,
                    reporting_period="custom",
                    category="billing",
                    role_tier="manager",
                    last_refreshed=now,
                    created_at=now,
                    updated_at=now,
                ),
                DashboardMetric(
                    metric_name="orders.total_count",
                    value=42,
                    unit="count",
                    aggregation_type="count",
                    date_range_start=now,
                    date_range_end=now,
                    reporting_period="custom",
                    category="orders",
                    role_tier="operator",
                    last_refreshed=now,
                    created_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.commit()

    def override_get_db() -> Iterator[Session]:
        session = sessionmaker(bind=engine)()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
