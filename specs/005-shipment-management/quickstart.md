# Quickstart: Shipment Management Validation

**Generated**: 2026-11-10
**Feature**: Shipment Management (S04)
**Spec**: specs/005-shipment-management/spec.md
**Research**: specs/005-shipment-management/research.md
**Contracts**: contracts/shipment_create_api_contract.md, contracts/shipment_list_api_contract.md, contracts/shipment_retrieve_api_contract.md, contracts/shipment_update_api_contract.md

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

### Scenario 1: Create Shipment (P1 - Core Flow)

**Goal**: Verify an authenticated user can create a new shipment for a confirmed order.

**Steps**:
1. Obtain a valid JWT token for an eligible customer (from S01 auth flow)
2. Ensure a order exists in confirmed status (from S03 Order Management)
3. POST to `/api/v1/shipments` with:
   ```json
   {
     "order_id": "<confirmed-order-uuid>",
     "carrier_name": "Carrier A"
   }
   ```
4. Verify response status: `201 Created`
5. Verify shipment response contains:
   - `status`: `pending`
   - `tracking_reference`: generated in format `SHIP-[UUID v4 substring]`
   - `carrier_name`: `Carrier A`
   - `order_id`: the order UUID provided
   - `version`: `1`

**Expected outcome**: Shipment is persisted with pending status, unique tracking reference, and carrier information. Shipment is associated with a confirmed order that passes eligibility validation.

---

### Scenario 2: List Shipments (P2 - S02 Consistency)

**Goal**: Verify shipment listing follows expected query patterns and pagination.

**Steps**:
1. Obtain a valid JWT token for an eligible customer (from S01 auth flow)
2. GET `/api/v1/shipments?page=1&page_size=20`
3. Verify response includes shipments with pagination metadata
4. Test filter parameters:
   - `status=pending` (filter by pending status)
   - `status=delivered` (filter by delivered status)
   - `q=SHIP-` (search by tracking reference prefix)
5. Verify default values: `page` defaults to 1, `page_size` defaults to 20, max `page_size` is 100

**Expected outcome**: Shipment listing is consistent with S02 pattern; search matches shipment ID, tracking reference, carrier, and status.

---

### Scenario 3: Update Shipment Carrier (P2 - Carrier Update)

**Goal**: Verify shipment carrier and tracking information can be updated while shipment is in pending status.

**Steps**:
1. Create a shipment (Scenario 1) and note its `shipment_id`
2. PATCH to `/api/v1/shipments/{shipment_id}` with:
   ```json
   {
     "version": 1,
     "carrier_name": "Carrier B"
   }
   ```
3. Verify response status: `200 OK`
4. Verify shipment response `carrier_name`: `Carrier B`

**Expected outcome**: Shipment carrier is updated to Carrier B while shipment remains in pending status. Status transition rules are enforced.

---

### Scenario 4: Confirm Delivery (P3 - Terminal State)

**Goal**: Verify delivery confirmation changes shipment status to delivered.

**Steps**:
1. Create a shipment (Scenario 1) and note its `shipment_id`
2. Update shipment status to in-transit (PATCH with status: in-transit, version 1)
3. PATCH to `/api/v1/shipments/{shipment_id}` with:
   ```json
   {
     "version": 2,
     "status": "delivered"
   }
   ```
4. Verify response status: `200 OK`
5. Verify shipment `status`: `delivered`
6. Verify `delivered_at` timestamp is set

**Expected outcome**: Shipment status changes to delivered; delivery timestamp is recorded. Delivery confirmation is terminal; further modifications are rejected.

---

### Scenario 5: Reject Shipment Creation for Non-Confirmed Order (P2 - Precondition)

**Goal**: Verify the system rejects shipment creation for an order that is not in confirmed status.

**Steps**:
1. Create an order in draft status (via S03 API or database)
2. POST to `/api/v1/shipments` with a valid `order_id` referencing the draft order
3. Verify response status: `400 Bad Request`
4. Verify error response contains clear message about order not being in confirmed status

**Expected outcome**: Shipment creation is rejected with descriptive error; order remains in draft status. Cancellation is terminal; orders in cancelled state cannot be restored.

---

### Scenario 6: Reject Invalid Status Transition (P3 - Boundary Rule)

**Goal**: Verify invalid status transitions are rejected.

**Steps**:
1. Create a shipment in pending status (Scenario 1) and note its `shipment_id`
2. PATCH to `/api/v1/shipments/{shipment_id}` with:
   ```json
   {
     "version": 1,
     "status": "delivered"
   }
   ```
3. Verify response status: `409 Conflict`
4. Verify error message indicates invalid state transition (pending → delivered without in-transit intermediate)

**Expected outcome**: Status transition is rejected; shipment remains in `pending` status. Invalid transitions are rejected at least 95% of the time in automated testing.

---

## Expected Outcomes Summary

| Scenario | Pass Criteria |
|---|---|
| 1. Create Shipment | 201 response; pending status; tracking reference format SHIP-UUID; associated with confirmed order |
| 2. List Shipments | Pagination; filter by status, q, order_id; defaults 1/20/100 |
| 3. Update Carrier | 200; carrier_name updated; shipment remains in pending status |
| 4. Confirm Delivery | 200; status → delivered; delivered_at timestamp recorded; terminal state |
| 5. Non-Confirmed Order | 400; clear error message about order status requirement |
| 6. Invalid Transition | 409; rejected with message indicating invalid transition |

## Notes

- All validation relies on the BSS-Core constitution constraints (SQLite, SQLAlchemy 2.x, Pydantic validation, JWT auth, Argon2id password hashing)
- Shipment status transitions: pending → in-transit → delivered (terminal); delivery confirmation properly closes the shipment lifecycle
- Shipment carrier and tracking information can be updated while shipment is in pending status
- Split shipments are out of scope for S04 MVP (single shipment per order)
- Data volume assumption: 100-500 shipments/day, supporting <10,000 active shipments with ~20% monthly growth