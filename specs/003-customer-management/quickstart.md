# Quickstart Validation Guide: Customer Management (S02)

**Purpose**: Runnable validation scenarios that prove the Customer Management feature works end-to-end. This guide references [data-model.md](./data-model.md) and [contracts/](./contracts/) instead of duplicating them.

## Prerequisites

- Python 3.12+ and `uv`
- Repository cloned at the project root
- Backend and frontend dependencies installed

## Setup

```bash
uv sync
uv run alembic upgrade head
```

Expected: the `customers`, `customer_contacts`, and `customer_addresses` tables exist in `db/bss_core.db`, with the partial unique indexes from the data model.

Start the backend:

```bash
uv run uvicorn src.api.health:app --host 0.0.0.0 --port 8000
```

Start the frontend (separate terminal):

```bash
uv run streamlit run src/frontend/app.py
```

## Automated Validation

```bash
uv run pytest tests/unit/customer_management tests/application/customer_management
uv run pytest tests/integration/customer_management
uv run pytest tests/contract/customer_management
uv run ruff check src tests
```

Expected: all customer tests pass and Ruff reports no issues.

## Validation Scenarios

### Scenario 1 — Migration from a clean database

1. Delete `db/bss_core.db` (development only).
2. Run `uv run alembic upgrade head`.
3. Inspect the schema.

**Expected**: the three tables and all indexes/foreign keys listed in `data-model.md` are present; `alembic downgrade base` followed by `upgrade head` succeeds.

---

### Scenario 2 — Register an individual and reject a duplicate

1. `POST /api/v1/customers` with an individual payload (see `contracts/customer-api.md`).
2. Repeat the request with the same `email`.

**Expected**: first request returns `201` with `status = ACTIVE` and `eligible = false`; the repeat returns `409 DUPLICATE_CUSTOMER`. Registering a **business** with the same email is allowed.

---

### Scenario 3 — Register a business and reject a duplicate

1. `POST /api/v1/customers` with a business payload.
2. Repeat with the same `registration_number` but a different display name.

**Expected**: first request returns `201`; the repeat returns `409 DUPLICATE_CUSTOMER`.

---

### Scenario 4 — Contacts, addresses, and eligibility

1. Add one contact and one address to a customer.
2. Call `GET /api/v1/customers/{id}/eligibility`.
3. Remove the only contact.
4. Call eligibility again.

**Expected**: eligibility is `true` after step 1–2; after removing the contact it is `false` with reason `NO_CONTACT`; the customer remains retrievable and editable.

---

### Scenario 5 — Deactivate and reactivate

1. `POST /api/v1/customers/{id}/deactivate`.
2. Retrieve the customer and check eligibility.
3. `POST /api/v1/customers/{id}/reactivate`.

**Expected**: deactivation sets `INACTIVE`, keeps all contacts/addresses, and makes eligibility `false` with reason `INACTIVE`; reactivation restores `ACTIVE` and eligibility based on contacts/addresses.

---

### Scenario 6 — Search, filter, and pagination

1. Seed at least 25 customers of both types and statuses.
2. Call `GET /api/v1/customers?q=<term>` and `?customer_type=BUSINESS&status=ACTIVE`.
3. Call with `page=2&page_size=10`.

**Expected**: matching items only, correct `total`, and non-overlapping pages. A search with no matches returns `200` with an empty `items` array.

---

### Scenario 7 — Stale update conflict

1. Retrieve a customer and note its `version`.
2. Send two `PATCH` requests with the same `version`, changing different fields.
3. Retry the rejected request with the returned `current_version`.

**Expected**: the first update succeeds and increments `version`; the second returns `409 STALE_UPDATE` with `current_version`; the retry succeeds.

---

### Scenario 8 — Authorization

1. Call a read endpoint without credentials or with only `customer:manage`.
2. Call a mutation endpoint with only `customer:view`.

**Expected**: `401` for missing credentials; `403` when the required permission is absent; permitted calls succeed. The frontend never bypasses these checks.

---

### Scenario 9 — Cross-module eligibility port

1. Resolve `CustomerEligibilityPort` from the composition root.
2. Call `get_summary` and `check_eligibility` for an active, eligible customer and for an inactive customer.

**Expected**: summaries match the API; eligibility reasons are correct; no ORM objects cross the boundary. See `contracts/customer-eligibility-port.md`.

---

### Scenario 10 — Streamlit management UI

1. Open the Streamlit app.
2. Create an individual and a business customer.
3. Search/filter the list, edit a customer, add a contact and an address, then deactivate and reactivate.

**Expected**: every action round-trips through the backend API and is reflected after refresh; the UI performs no business-rule enforcement beyond displaying backend errors.

## Acceptance Mapping

| Scenario | Spec coverage |
|---|---|
| 1 | FR-002, data model, constitution Section 7 |
| 2–3 | FR-001, FR-002, FR-006 |
| 4 | FR-007, FR-008, FR-012, SC-009 |
| 5 | FR-005, FR-012, FR-017, SC-007 |
| 6 | FR-010, FR-011, SC-003 |
| 7 | FR-016 |
| 8 | FR-013, SC-006 |
| 9 | FR-014, SC-008 |
| 10 | Vertical-slice completion (constitution Section 6) |
