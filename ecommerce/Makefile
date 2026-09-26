## General

.PHONY: help install check clean lint format typecheck test coverage test-api run

# Start command defaults. Override per-invocation, e.g. `PORT=9000 make run`.
HOST ?= 127.0.0.1
PORT ?= 8000

help:
	@echo "Available targets:"
	@echo "  install      Install the project with uv sync"
	@echo "  run          Start the server (HOST=$(HOST) PORT=$(PORT))"
	@echo "  check        Run all checks (lint, format, typecheck, test)"
	@echo "  clean        Clean cache and coverage files"
	@echo "  lint         Run ruff check"
	@echo "  format       Run ruff format --check"
	@echo "  typecheck    Run mypy (strict)"
	@echo "  test         Run pytest"
	@echo "  test-api     Run only the API tests"
	@echo "  coverage     Run pytest with coverage"
	@echo ""
	@echo "Planned targets (not yet implemented):"
	@echo "  migrate      Run alembic migrations"
	@echo "  migrate-new  Create a new alembic migration"
	@echo "  migration-status Check migration status"
	@echo "  seed         Seed the database with fake data"
	@echo "  seed-test    Seed with test data"
	@echo "  seed-large   Seed with large data"
	@echo "  reset        Reset the database"

install:
	uv sync

run:
	uv run uvicorn ecommerce.main:app --host $(HOST) --port $(PORT)

check: lint format typecheck test

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

typecheck:
	uv run mypy src

test:
	uv run pytest

test-api:
	uv run pytest tests/api -m api

coverage:
	uv run pytest --cov=ecommerce --cov-report=term-missing

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__/ src/ecommerce/__pycache__/ .coverage htmlcov/ data/
