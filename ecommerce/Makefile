## General

.PHONY: help install check clean lint format typecov

help:
	@echo "Available targets:"
	@echo "  install      Install the project with uv sync"
	@echo "  check        Run all checks (lint, format, typecheck, test)"
	@echo "  clean        Clean cache and coverage files"
	@echo "  lint         Run ruff check"
	@echo "  format       Run ruff format --check"
	@echo "  typecheck    Run mypy"
	@echo "  test         Run pytest"
	@echo "  coverage     Run pytest with coverage"
	@echo ""
	@echo "Planned targets (not yet implemented):"
	@echo "  bootstrap    Bootstrap the project"
	@echo "  migrate      Run alembic migrations"
	@echo "  migrate-new  Create a new alembic migration"
	@echo "  migration-status Check migration status"
	@echo "  seed         Seed the database with fake data"
	@echo "  seed-test    Seed the database with test data"
	@echo "  seed-large   Seed the database with large data"
	@echo "  seed-args    Seed the database with custom args"
	@echo "  reset        Reset the database"
	@echo "  db-reset     Reset the database via alembic"
	@echo "  run          Run the development server"

install:
	uv sync

check: lint format typecheck test

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

typecheck:
	uv run mypy src

test:
	uv run pytest

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__/ .coverage data/