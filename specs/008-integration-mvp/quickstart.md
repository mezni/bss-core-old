# Quickstart: Integration & MVP Release Validation

**Generated**: 2026-11-11
**Feature**: Integration & MVP Release (S07)
**Spec**: specs/008-integration-mvp/spec.md
**Research**: specs/008-integration-mvp/research.md
**Contracts**: contracts/ (workflow sequences, error format, authorization, data generator)

## Prerequisites

- Python 3.12+ installed
- uv package manager configured
- BSS-Core repository cloned and dependencies installed (`uv sync`)
- SQLite3 available (comes with Python)
- `BSS_JWT_SECRET` set in the environment (e.g., `export BSS_JWT_SECRET="dev-secret"`)

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Apply database migrations from a CLEAN database (SC-007 sign-off gate)
rm -f db/bss_core.db && uv run alembic upgrade head

# 3. Generate interconnected synthetic data
uv run bss-datagen --seed 42

# 4. Start the backend (single consolidated app)
uv run uvicorn src.api.health:app --host 0.0.0.0 --port 8000

# 5. (Optional) Run the full test suite
uv run pytest tests/ -v
```

## Minting Test Tokens

All scenarios need a JWT bearer token with a `permissions` claim (PyJWT HS256, `BSS_JWT_SECRET`):

```bash
uv run python -c "
import jwt
print(jwt.encode({'sub': 'tester', 'permissions': ['user:view']}, 'dev-secret', 'HS256'))"
```

Repeat with `['user:billing']` and `['user:admin']` for the other roles. Use `Authorization: Bearer <token>` on every request.

## Validation Scenarios

### Scenario 1: Clean-Database Migrations (SC-007 — sign-off gate)

**Goal**: Verify all module schema is established from a completely clean database.

**Steps**:
1. `rm -f db/bss_core.db`
2. `uv run alembic upgrade head`
3. Verify the command exits without errors
4. Verify all module tables exist (customers, orders, order_items, shipments, invoices, payments)

**Expected outcome**: Migrations succeed from a clean state; all schema present; no manual steps required.

---

### Scenario 2: Data Generator Determinism (SC-003)

**Goal**: Verify deterministic, FK-valid synthetic data generation.

**Steps**:
1. On a clean database: `uv run bss-datagen --seed 42 --manifest-path /tmp/m1.json`
2. Inspect `/tmp/m1.json`: `created` counts match `volumes`; `fk_chains` counts equal the created record counts
3. Re-run on a fresh clean database with the same seed: `uv run bss-datagen --seed 42 --manifest-path /tmp/m2.json`
4. Compare `created` and `fk_chains` between the two manifests

**Expected outcome**: Identical manifests (same counts, same referential chains); every generated order/shipment/invoice/payment references an existing parent record.

---

### Scenario 3: Customer-to-Order Workflow (P1)

**Goal**: Verify the customer-to-order end-to-end workflow.

**Steps**:
1. Mint a `user:view` token
2. `POST /api/v1/customers` with a valid customer payload → verify `201`
3. `POST /api/v1/orders` with the returned customer id and at least one order item → verify `201`, order `status="confirmed"`, correct customer/item association
4. `POST /api/v1/orders` with **no items** → verify `400 VALIDATION_ERROR` (standardized envelope) and no order created

**Expected outcome**: Order created as `confirmed` with correct associations; empty order rejected per the error contract.

---

### Scenario 4: Order-to-Shipment Workflow (P1)

**Goal**: Verify the order-to-shipment workflow and status transition.

**Steps**:
1. Mint a `user:admin` token (order-to-shipment is admin-only per the clarified role mapping)
2. Create a confirmed order (Scenario 3 or generator data)
3. `POST /api/v1/shipments` referencing the order → verify `201`, unique tracking number, order `status="shipped"`
4. Repeat shipment creation for the same order → verify standardized conflict error
5. Attempt shipment creation for a `draft` order → verify `409 CONFLICT`, order status unchanged

**Expected outcome**: Shipment created with tracking number; order transitions to `shipped`; failures leave the order `confirmed`.

---

### Scenario 5: Order-to-Invoice Workflow (P2)

**Goal**: Verify invoice generation from a confirmed order.

**Steps**:
1. Mint a `user:billing` token
2. `POST /api/v1/invoices` referencing a confirmed order → verify `201`, invoice number `INV-` format, `status="pending"`, line items mirror the order items, total **exactly** matches the order total
3. Repeat invoice generation for the same order → verify `409 CONFLICT` and **no duplicate invoice** created

**Expected outcome**: One pending invoice per order with exactly matching totals; duplicates rejected.

---

### Scenario 6: Invoice-to-Payment Workflow (P2)

**Goal**: Verify payment processing and terminal invoice state.

**Steps**:
1. With the `user:billing` token, `POST /api/v1/payments` referencing a pending invoice → verify `201`, payment recorded with amount and timestamp, invoice `status="paid"`
2. `POST /api/v1/payments` for the same (now paid) invoice → verify rejection with standardized error; invoice remains `paid`

**Expected outcome**: Payment recorded; invoice reaches terminal `paid` state; double payment rejected.

---

### Scenario 7: Cross-Module Authorization (security review sign-off gate)

**Goal**: Verify the role-to-workflow enforcement matrix.

**Steps** (for each of the four workflow entry points):
1. Call with a `user:view` token → customer-to-order granted; order-to-shipment, order-to-invoice, invoice-to-payment denied with `403 FORBIDDEN`
2. Call with a `user:billing` token → order-to-invoice and invoice-to-payment granted; customer-to-order and order-to-shipment denied with `403`
3. Call with a `user:admin` token → all four granted
4. Call with no/invalid token → `401 UNAUTHENTICATED`

**Expected outcome**: The enforcement matrix in `contracts/authorization_contract.md` holds exactly; denials create no records; denials appear in structured logs.

---

### Scenario 8: Standardized Error Format (FR-007)

**Goal**: Verify the error envelope across endpoints.

**Steps**:
1. Trigger `400` (invalid payload), `401` (missing token), `403` (under-privileged workflow call), `404` (unknown resource id), `409` (duplicate/conflict) on different module endpoints
2. Verify every response body has exactly the fields `error`, `message`, `code` per `contracts/error_response_contract.md`
3. Verify messages are human-readable and contain no stack traces or secrets

**Expected outcome**: One consistent envelope on every endpoint and status class.

---

### Scenario 9: Automated Test Suite (SC-001 — sign-off gate)

**Goal**: Verify all four workflows pass end-to-end from a clean database via automated tests.

**Steps**:
1. `uv run pytest tests/integration/e2e/ -v`
2. `uv run pytest tests/contract/integration/ -v`
3. `uv run pytest tests/ -v` (full suite)
4. `uv run ruff check src tests` (quality gate)

**Expected outcome**: All four workflow journey tests pass (customer-to-order, order-to-shipment, order-to-invoice, invoice-to-payment) plus clean-database migration test; error-format and authorization contract tests pass; full suite green; Ruff clean.

---

### Scenario 10 (optional): Database Backup Procedure (S07-10, Should)

**Goal**: Verify the documented SQLite backup and recovery procedure.

**Steps**:
1. Back up: `sqlite3 db/bss_core.db "VACUUM INTO 'backup.db'"`
2. Restore to a fresh file and re-run Scenario 3 read checks against the restored database

**Expected outcome**: Backup and restore succeed; restored database serves valid workflow reads.

## Expected Outcomes Summary

| Scenario | Pass Criteria (sign-off gate in bold) |
|---|---|
| 1. Clean migrations | **Migrations succeed from clean DB; all schema present (SC-007)** |
| 2. Generator determinism | Identical manifests for same seed; FK chains valid |
| 3. Customer-to-order | Order `confirmed`; empty order rejected |
| 4. Order-to-shipment | Shipment + tracking number; order `shipped`; failures safe |
| 5. Order-to-invoice | Pending invoice; totals match exactly; no duplicates |
| 6. Invoice-to-payment | Payment recorded; invoice `paid` terminal; double payment rejected |
| 7. Authorization matrix | **Enforcement matrix holds; no critical auth defects (security gate)** |
| 8. Error format | One envelope on all endpoints/status classes |
| 9. Test suite | **All four workflow e2e tests pass (SC-001)**; suite green; Ruff clean |
| 10. Backup procedure | Backup/restore succeed (Should priority, non-blocking) |

## Notes

- All endpoints are under `/api/v1`, served by the single consolidated app (`src.api.health:app`)
- JWT authentication with `permissions` claim required on every request
- MVP sign-off gates: SC-001, SC-007, security review (spec clarification); other criteria are quality targets
- Out of scope: real-time WebSocket updates, performance optimization, non-SQLite databases, auth method changes, module-specific metrics
- Invoice total must exactly match the associated order total (constitution alignment)
- Structured JSON logging for all workflow events; no secrets exposed
