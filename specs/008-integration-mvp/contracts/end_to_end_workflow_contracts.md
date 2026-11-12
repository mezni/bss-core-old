# Contract: End-to-End Workflow API Sequences

**Applies to**: All four S07 integration workflows, executed against the single consolidated application (`src.api.health:app`), versioned under `/api/v1`.

**Description**: Each workflow is an ordered sequence of existing module API operations. The contracts below define the required sequence, payloads, expected intermediate states, and terminal evidence for each workflow. All endpoints use the standardized error envelope (see `error_response_contract.md`) and enforce the workflow permission (see `authorization_contract.md`).

---

## Workflow 1: Customer-to-Order (`customer_to_order`)

**Required permission**: `user:view` (also granted by `user:admin`)
**Participating modules**: identity, customer, order

**Sequence**:

| Step | Operation | Endpoint | Success Evidence |
|---|---|---|---|
| 1 | Create customer | `POST /api/v1/customers` | `201 Created`; customer id returned |
| 2 | Create order with items | `POST /api/v1/orders` | `201 Created`; order `status="confirmed"`, correct `customer_id`, items with quantities/prices |

**Payloads**: customer payload per `specs/003-customer-management/contracts`; order payload per `specs/004-order-management/contracts` (customer reference + order items).

**Terminal evidence**: order exists with `status="confirmed"` and the correct customer/item association.

**Failure branches**:
- Order without items → `400 VALIDATION_ERROR`; no order created (empty-cart mapping)
- Invalid customer reference → `404 NOT_FOUND`; no order created
- Under-privileged token → `403 FORBIDDEN` before any record is created

---

## Workflow 2: Order-to-Shipment (`order_to_shipment`)

**Required permission**: `user:admin` (per clarified role mapping; `user:admin` grants all four workflows)
**Participating modules**: identity, order, shipment

**Precondition**: order exists with `status="confirmed"`.

**Sequence**:

| Step | Operation | Endpoint | Success Evidence |
|---|---|---|---|
| 1 | Create shipment for order | `POST /api/v1/shipments` | `201 Created`; unique tracking number; references the order |
| 2 | Order status update (via order port) | (internal to shipment use case) | order `status="shipped"` |

**Payloads**: shipment payload per `specs/005-shipment-management/contracts` (order reference, delivery details).

**Terminal evidence**: shipment record with unique tracking number exists; order `status="shipped"`.

**Failure branches**:
- Shipment creation failure → standardized error; order status remains `confirmed` (no partial state change)
- Shipment for non-confirmed order → `409 CONFLICT` (invalid state for shipment)
- Under-privileged token → `403 FORBIDDEN`

---

## Workflow 3: Order-to-Invoice (`order_to_invoice`)

**Required permission**: `user:billing` (also granted by `user:admin`)
**Participating modules**: identity, order, billing

**Precondition**: order exists with `status="confirmed"`.

**Sequence**:

| Step | Operation | Endpoint | Success Evidence |
|---|---|---|---|
| 1 | Generate invoice for order | `POST /api/v1/invoices` | `201 Created`; invoice number `INV-` format; `status="pending"`; line items mirror order items; total matches order total exactly |

**Payloads**: invoice payload per `specs/006-billing/contracts` (order reference).

**Terminal evidence**: invoice exists with `status="pending"`, invoice total exactly matching the order total.

**Failure branches**:
- Repeated invoice generation for the same order → no duplicate created; standardized error response (`409 CONFLICT`)
- Non-confirmed order → `409 CONFLICT`
- Under-privileged token → `403 FORBIDDEN`

---

## Workflow 4: Invoice-to-Payment (`invoice_to_payment`)

**Required permission**: `user:billing` (also granted by `user:admin`)
**Participating modules**: identity, billing

**Precondition**: invoice exists with `status="pending"`.

**Sequence**:

| Step | Operation | Endpoint | Success Evidence |
|---|---|---|---|
| 1 | Process payment for invoice | `POST /api/v1/payments` | `201 Created`; payment record with amount and timestamp; invoice `status="paid"` |

**Payloads**: payment payload per `specs/006-billing/contracts` (invoice reference, amount).

**Terminal evidence**: payment transaction recorded with the correct amount and timestamp; invoice `status="paid"` (terminal).

**Failure branches**:
- Payment on a `paid` invoice → rejected with standardized error; invoice remains `paid`
- Payment amount exceeding outstanding balance → `400 VALIDATION_ERROR`
- Under-privileged token → `403 FORBIDDEN`

---

## Cross-Workflow Rules

- Every workflow emits `workflow.started` / `workflow.completed` / `workflow.failed` structured log events with correlation id (FR-008)
- Workflow steps execute in dependency order; failure at any step leaves prior records in their last valid state
- All responses use the standardized error envelope; all success responses follow each module's documented schema
- Authentication: JWT bearer token with `permissions` claim on every request
