# Quickstart Validation Guide: Order Management (S03)

**Purpose**: Runnable validation scenarios that prove the Order Management feature works end-to-end. This guide references [data-model.md](./data-model.md) and [contracts/](./contracts/) instead of duplicating them.

## Prerequisites

- Python 3.12+ and `uv`
- Repository cloned at the project root
- Backend and frontend dependencies installed

## Setup

```bash
uv sync
uv run alembic upgrade head
```

Expected: the `orders` table exists in `db/bss_core.db`, with columns for all Order attributes (id, status, subtotal, tax_amount, total, customer_id, version, created_at, updated_at) and appropriate indexes.

Start the backend:

```bash
uv run uvicorn src.api.health:app --host 0.0.0.0 --port 8000
```

## Automated Validation

```bash
uv run pytest tests/unit/customer_management  # baseline (S02)
uv run pytest tests/integration/customer_management  # S02 integration tests
uv run ruff check src tests
```

Expected: Ruff reports no issues; S02 tests pass.

## Validation Scenarios

### Scenario 1 — Migration from a clean database

1. Delete `db/bss_core.db` (development only).
2. Run `uv run alembic upgrade head`.
3. Inspect the schema.

**Expected**: the `orders` table and all indexes listed in `data-model.md` are present; `alembic downgrade base` followed by `upgrade head` succeeds.

---

### Scenario 2 — Create an order with items

1. `POST /api/v1/orders` with a valid `customer_id` (from S02, eligible customer) and at least one order item.
2. Verify the response has `status = draft` and `version = 1`.
3. Repeat the request with the same payload.

**Expected**: first request returns `201` with `status = draft` and `version = 1`; the repeat returns `409 DUPLICATE_ORDER` (or equivalent error for duplicate creation without idempotency key). *Note: exact error code depends on idempotency design.*

---

### Scenario 3 — Order status transitions

1. Create an order with at least one item (Scenario 2).
2. `PATCH /api/v1/orders/{{order_id}}` with `status = confirmed` and matching `version`.
3. Verify the order status is now `confirmed` and `version` incremented.
4. Attempt to `PATCH` with `status = drafted` (invalid transition) — should return `409 INVALID_TRANSITION`.
5. Attempt to `PATCH` with `status = confirmed` and stale `version` — should return `409 STALE_UPDATE` with `current_version`.

**Expected**: confirmed transition succeeds with version increment; invalid transitions rejected; stale updates rejected with current version.

---

### Scenario 4 — Order cancellation (terminal)

1. Create an order with at least one item.
2. `POST /api/v1/orders/{{order_id}}/cancel` (or `PATCH` with `status = cancelled` and valid version).
3. Verify the order status is now `cancelled`.
4. Attempt to confirm or modify the cancelled order — should return `409 INVALID_TRANSITION` or appropriate error.

**Expected**: order status becomes `cancelled`; cancellation is terminal; no restoration from cancelled state; creating a new order requires a fresh order.

---

### Scenario 5 — Order listing with pagination and search

1. Create multiple orders (at least 5) with different statuses and customers.
2. `GET /api/v1/orders?status=confirmed` — verify only confirmed orders returned, correct `total`.
3. `GET /api/v1/orders?page=1&page_size=10` — verify pagination; first page has 10 items, `total` reflects all matching orders.
4. `GET /api/v1/orders?q=ORDER` — verify search matches against order ID, customer reference, and status.
5. `GET /api/v1/orders?page=2&page_size=10` — verify non-overlapping pages.

**Expected**: matching items only, correct `total`, non-overlapping pages. A search with no matches returns `200` with empty `items` array.

---

### Scenario 6 — Order retrieval

1. `GET /api/v1/orders/{{order_id}}` with a valid order ID from Scenario 2.
2. Verify the response includes all order attributes, items, customer info, and version.
3. `GET /api/v1/orders/{{nonexistent_id}}` — should return `404 NOT FOUND`.

**Expected**: full order details returned; 404 for nonexistent order.

---

## Acceptance Mapping

| Scenario | Spec coverage |
|---|---|
| 1 | FR-002, data model, constitution Section 7 |
| 2–3 | FR-001, FR-002, FR-005, FR-006 |
| 4 | FR-005, FR-012, SC-007 |
| 5 | FR-010, FR-011, SC-003 |
| 6 | FR-007, SC-005 |

## Notes

- All API endpoints require appropriate permissions: `customer:view` for read operations, `customer:manage` for write/list operations.
- Order totals (subtotal, tax, total) are calculated correctly with ±2% tolerance per success criteria SC-003.
- Status transition boundaries are strict; the system enforces these boundaries without exposing internal implementation details.
- Cancellation is terminal; orders in cancelled state cannot be restored.
