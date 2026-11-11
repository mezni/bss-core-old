# Data Model: Shipment Management (S04)

**Generated**: 2026-11-10
**Feature**: Shipment Management (S04)
**Spec**: specs/005-shipment-management/spec.md

## Entity: Shipment

**Description**: Represents a delivery request for an order. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: SHIP-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all shipments |
| `status` | Enum | Current lifecycle stage | Values: `pending`, `in-transit`, `delivered`, `exception`; defaults to `pending` |
| `tracking_reference` | string | Tracking reference number | Format: SHIP-[UUID v4 substring]; generated on creation; unique per order |
| `carrier_name` | string | Name of shipping carrier | Required for pending status; optional for in-transit/delivered |
| `order_id` | UUID v4 | Parent order reference | Foreign key to Order; must reference a confirmed order; cascade delete on order removal |
| `created_at` | datetime | Shipment creation timestamp | Auto-generated; not modifiable after creation |
| `updated_at` | datetime | Last update timestamp | Auto-updated on status changes |
| `delivered_at` | datetime | Delivery timestamp | Set only when status transitions to `delivered`; nullable |

**Business invariants**:
- Shipment can only be created for orders in confirmed status
- Status transitions follow: pending → in-transit → delivered (terminal)
- Delivery confirmation is terminal; shipments in delivered status cannot be modified
- Tracking reference is generated on creation and follows format: SHIP-[UUID v4 substring]
- Carrier name is required for pending status; may be updated during pending status

**Responsibility**: Owns its business invariants (valid status transitions, tracking reference requirements); enforces status transition preconditions in the domain layer; documents required checks (order confirmation status, sequence order); delivery confirmation is terminal; shipment status progresses: pending → in-transit → delivered

---

## Entity: Order

**Description**: Represents a customer's purchase request. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: ORD-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all orders |
| `status` | Enum | Current lifecycle stage | Values: `draft`, `confirmed`, `shipped`, `delivered`, `cancelled`; defaults to `draft` |
| `customer_id` | Identifier | Reference to customer | Must reference an eligible customer from S02 Customer Management; foreign key constraint |
| `created_at` | datetime | Order creation timestamp | Auto-generated; not modifiable after creation |
| `updated_at` | datetime | Last update timestamp | Auto-updated on status changes |

**Relationships**:
- One order can have associated shipments that track delivery progress
- One order can have multiple shipments (e.g., split shipments); each shipment belongs to exactly one order

**Responsibility**: Validated for order eligibility; each order references exactly one customer; eligibility check draws from S02 eligibility port

---

## Relationships

| Parent | Child | Relationship | Cardinality |
|---|---|---|---|
| Customer | Order | One-to-many | One customer can have many orders; each order belongs to exactly one customer |
| Order | Shipment | One-to-many | One order can have many shipments; each shipment belongs to exactly one order |

## Validation Rules (from Requirements)

- **FR-001**: System MUST allow an authenticated user to create a new shipment for a confirmed order
- **FR-002**: System MUST require an order to be in confirmed status before a shipment can be created
- **FR-003**: System MUST calculate and assign a tracking reference number on shipment creation
- **FR-004**: System MUST allow updating shipment carrier and tracking number while in pending status
- **FR-005**: System MUST enforce valid status transitions: pending → in-transit → delivered
- **FR-006**: System MUST reject invalid status transitions with a clear error message
- **FR-007**: System MUST associate every shipment with a valid, confirmed order
- **FR-008**: System MUST expose shipment creation and management through REST API endpoints under `/api/v1/shipments`
- **FR-009**: System MUST provide order-shipment relationship ensuring shipments belong only to confirmed orders

## Index Recommendations

Based on query patterns and data volume assumptions (100-500 shipments/day, <10,000 active shipments):

- **Order_id index**: Foreign key lookup for shipment creation validation; high cardinality; recommended
- **Status index**: Frequent filtering by status for shipment listing and status transition validation; medium cardinality; recommended
- **Tracking_reference index**: Unique constraint; point lookup for shipment retrieval; high cardinality; unique index recommended
- **Created_at index**: Time-based queries for shipment history and reporting; low-to-medium cardinality; recommended for S05+ when history queries become frequent