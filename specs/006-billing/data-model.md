# Data Model: Billing (S05)

**Generated**: 2026-11-10
**Feature**: Billing (S05)
**Spec**: specs/005-billing/spec.md

## Entity: Invoice

**Description**: Represents a billing document for an order or shipment. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: INV-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all invoices |
| `invoice_number` | string | Invoice number | Required; unique; format: INV-YYYYMMDD-#### |
| `status` | Enum | Current lifecycle stage | Values: `pending`, `paid`, `terminal`; defaults to `pending` |
| `total_amount` | decimal | Total invoice amount | Must match associated order/shipment total; precision: 2 decimal places |
| `reference_id` | UUID v4 | Associated order or shipment ID | Foreign key to Order or Shipment; must reference a completed billable order/shipment |
| `billing_date` | datetime | Invoice generation timestamp | Auto-generated; not modifiable after creation |
| `due_date` | datetime | Payment due date | Required; must be after billing_date |
| `payment_date` | datetime | Payment completion timestamp | Set only when status transitions to `paid`; nullable |
| `payment_method` | string | Payment method used | Required when status is `paid`; values: `card`, `bank_transfer`, `cash` |
| `customer_id` | string | Customer identifier | Required; references customer from S02 Customer Management |

**Business invariants**:
- Invoice can only be generated for orders or shipments in billable status
- Status transitions follow: pending → paid (terminal)
- Payment is terminal; invoices in paid status cannot be modified
- Invoice total must match associated order/shipment total exactly
- Due date must be after billing date

**Responsibility**: Owns its business invariants (valid status transitions, amount calculation); enforces status transition preconditions in the domain layer; documents required checks (order/shipment billable status, sequence order); payment is terminal; invoice status progresses: pending → paid (terminal)

---

## Entity: Payment

**Description**: Represents a payment record against an invoice. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: PAY-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all payments |
| `invoice_id` | UUID v4 | Associated invoice ID | Foreign key to Invoice; cascade delete on invoice removal |
| `amount` | decimal | Payment amount | Must match invoice total; precision: 2 decimal places |
| `payment_method` | string | Payment method | Required; values: `card`, `bank_transfer`, `cash` |
| `status` | Enum | Payment status | Values: `pending`, `completed`, `terminal`; defaults to `pending` |
| `transaction_id` | string | Payment processor transaction ID | Required when status is `completed`; unique |
| `payment_date` | datetime | Payment completion timestamp | Auto-generated when status becomes `completed` |
| `customer_id` | string | Customer identifier | Required; references customer from S02 Customer Management |

**Relationships**:
- Each payment belongs to exactly one invoice
- Payment amount must match invoice total

---

## Entity: Order/Shipment

**Description**: Represents a customer's purchase or delivery request. Each order/shipment can have associated invoices that track billing progress. One order/shipment can have multiple invoices; each invoice belongs to exactly one order or shipment.

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: ORD-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all orders |
| `status` | Enum | Current lifecycle stage | Values: `draft`, `confirmed`, `shipped`, `delivered`, `billable`; defaults to `draft` |
| `customer_id` | string | Customer identifier | Required; references customer from S02 Customer Management |
| `total_amount` | decimal | Order/shipment total amount | Used as basis for invoice total calculation |
| `status_date` | datetime | Status change timestamp | Auto-generated; not modifiable after creation |

**Relationships**:
- One order/shipment can have multiple invoices that track billing progress
- Each invoice belongs to exactly one order or shipment

## Validation Rules (from Requirements)

- **FR-001**: System MUST allow an authenticated user to generate an invoice for a completed order or shipment
- **FR-002**: System MUST require an order or shipment to be in a billable status before an invoice can be generated
- **FR-003**: System MUST calculate the invoice total from associated order/shipment amounts
- **FR-004**: System MUST allow processing a payment against an invoice
- **FR-005**: System MUST enforce valid payment status transitions: pending → paid (terminal)
- **FR-006**: System MUST reject invalid payment status transitions with a clear error message
- **FR-007**: System MUST associate every invoice with a valid, confirmed order or shipment
- **FR-008**: System MUST expose invoice creation and management through REST API endpoints under `/api/v1/invoices`
- **FR-009**: System MUST provide order/shipment-invoice relationship ensuring invoices belong only to billable orders or shipments

## Index Recommendations

Based on query patterns and data volume assumptions (10-100 invoices per month, <500 active invoices with ~10% monthly growth):

- **reference_id index**: Foreign key lookup for invoice generation validation; high cardinality; recommended
- **status index**: Frequent filtering by invoice status for invoice listing and status transition validation; medium cardinality; recommended
- **due_date index**: Sorting and filtering by due date for aging reports; low-to-medium cardinality; recommended
- **customer_id index**: Customer-based reporting and lookup; medium cardinality; recommended
- **invoice_number index**: Unique constraint; point lookup for invoice retrieval; high cardinality; unique index recommended