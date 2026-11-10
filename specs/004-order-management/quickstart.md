# Quickstart: Order Management Validation

**Generated**: 2026-11-10
**Feature**: Order Management (S03)
**Spec**: specs/004-order-management/spec.md
**Research**: specs/004-order-management/research.md
**Contracts**: contracts/order_management/order_management_api.yaml

## Prerequisites

- Python 3.12+ installed
- UV package manager configured
- BSS-Core repository cloned and dependencies installed (`uv sync`)
- SQLite3 available (comes with Python)
- JWT authentication token for API tests (obtain via S01 auth flow)

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Apply database migrations
cd src/infrastructure
alembic upgrade head

# 3. Start the backend server
uv run uvicorn src.presentation.api:app --reload

# 4. (Optional) Start the Streamlit frontend
uv run streamlit run src/presentation/streamlit_app.py
```

## Validation Scenarios

### Scenario 1: Create Order (P1 - Core Flow)

**Goal**: Verify a registered customer can create a new order in draft status.

**Steps**:
1. Obtain a valid JWT token for an eligible customer (from S01 auth flow)
2. POST to `/api/v1/orders` with:
   ```json
   {
     "customer_id": "<eligible-customer-uuid>",
     "items": [
       {
         "description": "Widget A",
         "quantity": 2,
         "unit_price": 10.50
       }
     ]
   }
   ```
3. Verify response status: `201 Created`
4. Verify order response contains:
   - `status`: `draft`
   - `subtotal`: `21.0` (2 × 10.50)
   - `tax_amount`: calculated (fixed rate × subtotal)
   - `total`: subtotal + tax_amount
   - `items`: line item with `line_total`: `21.0`

**Expected outcome**: Order is persisted with draft status, correct total calculation, and unique UUID v4 identifier.

---

### Scenario 2: Confirm Order (P2 - Status Transition)

**Goal**: Verify an order in draft status can be confirmed when it has at least one item.

**Steps**:
1. Create an order (Scenario 1) and note its `order_id`
2. POST to `/api/v1/orders/{order_id}/confirm`
3. Verify response status: `200 OK`
4. Verify order response `status` field: `confirmed`

**Expected outcome**: Order status transitions from `draft` to `confirmed`. Order cannot be arbitrarily modified after confirmation.

---

### Scenario 3: Reject Confirmation Without Items (P2 - Precondition)

**Goal**: Verify the system rejects order confirmation without any items.

**Steps**:
1. Create an order with 0 items (or remove all items)
2. POST to `/api/v1/orders/{order_id}/confirm`
3. Verify response status: `400 Bad Request`
4. Verify error response contains clear message about missing items

**Expected outcome**: Confirmation is rejected with descriptive error; order remains in draft status.

---

### Scenario 4: Cancel Order (P3 - Terminal State)

**Goal**: Verify order cancellation is terminal and cannot be restored.

**Steps**:
1. Create an order in draft status (no items required for draft cancellation)
2. POST to `/api/v1/orders/{order_id}/cancel`
3. Verify response status: `200 OK`
4. Verify order `status`: `cancelled`
5. Attempt to restore the order:
   - POST to a restoration endpoint (should not exist) or attempt confirmation
   - Verify the system rejects the restoration attempt
6. Attempt to create a new order for the same customer
7. Verify a fresh order can be created (cancellation is terminal, not retroactive)

**Expected outcome**: Order status becomes `cancelled`; restoration is rejected; customer must create a fresh order.

---

### Scenario 5: Invalid Status Transition (P3 - Boundary Rule)

**Goal**: Verify invalid status transitions are rejected.

**Steps**:
1. Create an order and confirm it (status: `confirmed`)
2. Attempt to cancel the confirmed order:
   - POST to `/api/v1/orders/{order_id}/cancel`
3. Verify response status: `400` or `409 Conflict`
4. Verify error message indicates invalid state transition

**Expected outcome**: Cancellation of confirmed order is rejected; order remains in `confirmed` status.

---

### Scenario 6: Order Listing with Pagination (P3 - S02 Consistency)

**Goal**: Verify order listing follows S02 pagination/search pattern.

**Steps**:
1. GET `/api/v1/orders?page=1&page_size=20`
2. Verify response includes orders with pagination metadata
3. Test search parameters:
   - `q=ord-` (search by order ID prefix)
   - `q=cust-` (search by customer reference - if supported)
   - `status=confirmed` (filter by status)
4. Verify default values: `page` defaults to 1, `page_size` defaults to 20, max `page_size` is 100

**Expected outcome**: Order listing is consistent with S02 pattern; search matches order ID, customer reference, and status.

## Expected Outcomes Summary

| Scenario | Pass Criteria |
|---|---|
| 1. Create Order | 201 response; correct subtotal/tax/total; draft status; UUID v4 ID |
| 2. Confirm Order | 200; status → confirmed |
| 3. Confirm Without Items | 400; clear error message |
| 4. Cancel Order | 200; status → cancelled; fresh order creatable |
| 5. Invalid Transition | 400/409; rejected with message |
| 6. Order Listing | Pagination; search by q, status; defaults 1/20/100 |

## Notes

- All validation relies on the BSS-Core constitution constraints (SQLite, SQLAlchemy 2.x, Pydantic validation, JWT auth, Argon2id password hashing)
- Order totals use fixed tax rate applied to subtotal (no jurisdiction-specific logic for S03 MVP)
- Order items carry inline description/price/quantity; no separate product catalog in S03
- Cancellation is terminal; orders in cancelled state cannot be restored
- Order listing follows S02 pagination/search pattern for consistency