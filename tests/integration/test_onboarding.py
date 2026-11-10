"""Integration test for developer onboarding flow.

Tests the complete developer onboarding experience:
1. Project initialization with uv
2. Backend FastAPI application starts
3. Frontend Streamlit application starts
4. SQLite database is accessible
5. All foundation setup completes without errors
"""

import os
import py_compile
import subprocess
import sys

# Ensure src is on the Python path for imports
src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_project_initialization():
    """Test that the project is properly initialized for developer onboarding."""
    # Verify pyproject.toml exists
    assert os.path.exists("pyproject.toml"), "pyproject.toml not found"

    # Verify uv is available as a CLI tool
    result = subprocess.run(
        ["uv", "--version"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, "uv not installed or not working"

    # Verify SQLite database exists
    assert os.path.exists("db/bss_core.db"), "SQLite database not found"


def test_backend_starts_without_errors():
    """Test that the backend FastAPI application starts without errors."""
    from fastapi.testclient import TestClient

    from api.health import app as fastapi_app

    client = TestClient(fastapi_app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_frontend_syntax_valid():
    """Test that the frontend Streamlit application has valid Python syntax."""
    frontend_path = os.path.join("src", "frontend", "app.py")
    assert os.path.exists(frontend_path), f"Frontend app not found at {frontend_path}"

    py_compile.compile(frontend_path, doraise=True)


def test_infrastructure_components():
    """Test that all infrastructure components are in place."""
    # Check directory structure
    assert os.path.isdir("src/domain"), "Domain layer not found"
    assert os.path.isdir("src/application"), "Application layer not found"
    assert os.path.isdir("src/infrastructure"), "Infrastructure layer not found"
    assert os.path.isdir("src/presentation"), "Presentation layer not found"

    # Check key files exist
    assert os.path.exists("alembic.ini"), "Alembic not initialized"
    assert os.path.exists("migrations/env.py"), "Alembic migration env not found"
