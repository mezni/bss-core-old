# S07 MVP Verification

**Date:** 2026-11-12
**Scope:** Integration & MVP Release (S07)

## Quality gates

| Gate | Command | Result |
|---|---|---|
| Full test suite | `uv run pytest -q` | **194 passed** |
| Lint (project code) | `uv run ruff check .` | **clean** |
| Clean-database migrations (SC-007) | `uv run pytest tests/integration/e2e/test_clean_database_migrations.py` | **passed** |
| Authorization matrix | `uv run pytest tests/contract/integration/test_workflow_authorization_contract.py` | **22 passed** |
| Datagen determinism (SC-003) | `uv run pytest tests/integration/test_datagen_determinism.py` | **3 passed** |
| Performance baseline (S07-07) | `uv run pytest tests/integration/e2e/test_workflow_performance.py` | **1 passed** |
| Backup procedure (S07-10) | `VACUUM INTO` verified on a temporary SQLite database | **passed** |

## Workflow evidence (SC-001)

| Workflow | Test | Result |
|---|---|---|
| Customer → Order | `tests/integration/e2e/test_customer_to_order.py` | passed |
| Order → Shipment | `tests/integration/e2e/test_order_to_shipment.py` | passed |
| Order → Invoice | `tests/integration/e2e/test_order_to_invoice.py` | passed |
| Invoice → Payment | `tests/integration/e2e/test_invoice_to_payment.py` | passed |

All four workflows run against a temporary SQLite database created from the
combined module metadata and use JWTs for the `user:view`, `user:billing`, and
`user:admin` permission flavors.

## Security sign-off

No critical authorization defects found. The full permission matrix,
401 behavior, denial logging, and no-partial-state-on-denial checks pass.
Details: `docs/security.md` §20.

## Deferred items

- Frontend order/shipment/billing pages (only customers and dashboard are
  currently rendered); the MVP workflows are verified through the API and E2E
  tests.
