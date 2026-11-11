# Quickstart: Billing Validation

**Generated**: 2026-11-10
**Feature**: Billing (S05)
**Spec**: specs/005-billing/spec.md
**Research**: specs/005-billing/research.md
**Contracts**: contracts/invoice_create_api_contract.md, contracts/invoice_list_api_contract.md, contracts/invoice_retrieve_api_contract.md, contracts/invoice_update_api_contract.md

## Prerequisites

- Python 3.12+ installed
- UV package manager configured
- BSS-Core repository cloned and dependencies installed (`uv sync`)
- SQLite3 available (comes with Python)
- JWT authentication token for API tests (obtain via S02 auth flow)

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Apply database migrations
cd src
alembic upgrade head

# 3. Start the backend server
uv run uvicorn main:app --reload

# 4. (Optional) Run tests
uv run pytest tests/ -v
```

## Validation Scenarios

### Scenario 1: Generate Invoice (P1 - Core Flow)

**Goal**: Verify an authenticated user can generate an invoice for a completed order.

**Steps**:
1. Obtain a valid JWT token for an eligible user (from S02 auth flow)
2. Ensure a completed order exists in the system (from S03 Order Management)
3. POST to `/api/v1/invoices` with:
   ```json
   {
     "reference_id": "<order-uuid>",
     "due_days": 30
   }
   ```
4. Verify response status: `201 Created`
5. Verify invoice response contains:
   - `status`: `pending`
   - `invoice_number`: `INV-YYYYMMDD-####` format
   - `total_amount`: matches order total amount
   - `reference_id`: the order UUID provided
   - `billing_date`: current timestamp
   - `due_date`: billing date + due_days
   - `version`: `1`

**Expected outcome**: Invoice is persisted with pending status, unique invoice number, total amount from order, and billing due date calculated from due_days parameter.

---

### Scenario 2: List Invoices (P2 - Consistency)

**Goal**: Verify invoice listing follows expected query patterns and pagination.

**Steps**:
1. Obtain a valid JWT token for an eligible user (from S02 auth flow)
2. GET `/api/v1/invoices?page=1&page_size=20`
3. Verify response includes invoices with pagination metadata
4. Test filter parameters:
   - `status=pending` (filter by pending status)
   - `status=paid` (filter by paid status)
   - `customer_id=<id>` (filter by customer)
5. Verify default values: `page` defaults to 1, `page_size` defaults to 20, max `page_size` is 100

**Expected outcome**: Invoice listing is consistent; search matches invoice ID, invoice number, total amount, and status.

---

### Scenario 3: Process Payment (P2 - Payment Processing)

**Goal**: Verify payment can be processed against an invoice in pending status.

**Steps**:
1. Generate an invoice (Scenario 1) and note its `invoice_id`
2. PATCH to `/api/v1/invoices/{invoice_id}` with:
   ```json
   {
     "version": 1,
     "status": "paid"
   }
   ```
3. Verify response status: `200 OK`
4. Verify invoice response `status`: `paid`
5. Verify `payment_date` timestamp is set
6. Verify `payment_method` is recorded (or note as pending if not provided)

**Expected outcome**: Invoice status updates to paid; payment timestamp is recorded; payment is processed successfully.

---

### Scenario 4: View Billing History (P3 - History View)

**Goal**: Verify billing history for a customer.

**Steps**:
1. Obtain a valid JWT token for an eligible user (from S02 auth flow)
2. GET `/api/v1/invoices?customer_id=<customer-uuid>`
3. Verify response includes all invoices for the customer with pagination metadata
4. Verify invoices are listed with correct amounts, dates, and statuses, ordered by date (most recent first)

**Expected outcome**: Billing history lists all customer invoices with correct data; pagination works correctly.

---

### Scenario 5: Reject Invoice Generation for Non-Billable Order (P2 - Precondition)

**Goal**: Verify the system rejects invoice generation for an order not in billable status.

**Steps**:
1. Ensure an order exists in draft or confirmed status (not billable)
2. POST to `/api/v1/invoices` with a valid `reference_id` referencing the non-billable order
3. Verify response status: `400 Bad Request`
4. Verify error response contains clear message about order not being in billable status

**Expected outcome**: Invoice generation is rejected with descriptive error; order remains in non-billable status.

---

### Scenario 6: Reject Payment for Already-Paid Invoice (P3 - Boundary Rule)

**Goal**: Verify invalid payment status transitions are rejected.

**Steps**:
1. Generate an invoice (Scenario 1) and process payment (Scenario 3) to make it paid
2. PATCH to `/api/v1/invoices/{invoice_id}` with:
   ```json
   {
     "version": 2,
     "status": "pending"
   }
   ```
3. Verify response status: `409 Conflict`
4. Verify error response contains clear message indicating invalid state transition (paid → pending without intermediate step)

**Expected outcome**: Status transition is rejected; invoice remains in `paid` status. Invalid transitions are rejected at least 95% of the time in automated testing.

---

## Expected Outcomes Summary

| Scenario | Pass Criteria |
|---|---|
| 1. Generate Invoice | 201 response; pending status; unique invoice number; total amount from order; due date calculated |
| 2. List Invoices | Pagination; filter by status, customer; defaults 1/20/100 |
| 3. Process Payment | 200; invoice status → paid; payment_date recorded |
| 4. Billing History | Pagination; invoices listed by customer with correct data, ordered by date |
| 5. Non-Billable Order | 400; clear error message about billable status requirement |
| 6. Invalid Transition | 409; rejected with message indicating invalid transition |

## Notes

- All validation relies on the BSS-Core constitution constraints (SQLite, SQLAlchemy 2.x, Pydantic validation, JWT auth, Argon2id password hashing)
- Invoice status transitions: pending → paid (terminal); payment is terminal; invoices in paid status cannot be modified
- Invoice total must match associated order/shipment total exactly
- Due date is calculated from billing date + due_days parameter
- Split invoices are out of scope for S05 MVP (single invoice per order)
- Data volume assumption: 10-100 invoices per month, supporting <500 active invoices with ~10% monthly growth

## Integration Notes

- Invoice creation requires `user:billing` permission (S02 Identity & Access)
- Invoice listing/retrieval requires `user:view` permission
- Invoice update requires `user:billing` permission
- All endpoints under `/api/v1/invoices` versioned v1
- JWT authentication required for all operations
- Invoice total must exactly match associated order/shipment total