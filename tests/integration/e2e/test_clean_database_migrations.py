"""Clean-database migration gate (SC-007).

A fresh database must reach ``alembic upgrade head`` and contain every
module table wired by the consolidated application.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect

REPO_ROOT = Path(__file__).resolve().parents[3]

EXPECTED_TABLES = {
    "customers",
    "customer_addresses",
    "customer_contacts",
    "orders",
    "order_items",
    "shipments",
    "invoices",
    "invoice_items",
    "payments",
    "dashboard_metric",
    "reporting_period",
}


def test_clean_database_reaches_head(tmp_path) -> None:
    database = tmp_path / "clean.db"
    env = os.environ.copy()
    env["BSS_DATABASE_URL"] = f"sqlite:///{database}"

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    engine = create_engine(f"sqlite:///{database}")
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert EXPECTED_TABLES <= tables
    assert "alembic_version" in tables
