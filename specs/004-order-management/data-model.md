# Data Model: Order Management

**Generated**: 2026-11-10
**Feature**: Order Management (S03)
**Spec**: specs/004-order-management/spec.md

## Entity: Order

**Description**: Represents a customer's purchase request. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique identifier | Format: ORD-550e8400-e29b-41d4-a716-446655440000; generated on creation; unique across all orders |
| `status` | Enum | Current lifecycle stage | Values: `draft`, `confirmed`, `shipped`, `delivered`, `cancelled`; defaults to `draft` |
| `subtotal` | Decimal | Sum of item line totals before tax | Calculated from order items; precision: 2 decimal places |
| `tax_amount` | Decimal | Tax calculated on subtotal | Fixed rate applied to subtotal (per assumption); precision: 2 decimal places |
| `total` | Decimal | Grand total (subtotal + tax) | Calculated; precision: 2 decimal places |
| `customer_id` | Identifier | Reference to customer | Must reference an eligible customer from S02 Customer Management; foreign key constraint |
| `created_at` | datetime | Order creation timestamp | Auto-generated; not modifiable after creation |
| `updated_at` | datetime | Last update timestamp | Auto-updated on status changes |

**Business invariants**:
- At least one order item must exist before order can be confirmed
- Status transitions follow: draft → confirmed → shipped → delivered, and draft → cancelled
- Cancellation is terminal; orders in cancelled state cannot be restored
- Order total = subtotal + tax_amount
- Each order references exactly one customer that passes eligibility validation

**Responsibility**: Owns business invariants (item count, valid status transitions, terminal cancellation); enforces status transition preconditions in domain layer; documents required checks (item count, customer eligibility, sequence order)

---

## Entity: Order Item

**Description**: Represents a line item within an order. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | UUID v4 | Unique line item identifier | Generated on creation |
| `order_id` | UUID v4 | Parent order reference | Foreign key to Order; cascade delete on order removal |
| `description` | free-form text | Product/service description | Carries all product/service details inline; no product ID stored |
| `quantity` | integer | Number of units | Minimum 1; used in line total calculation |
| `unit_price` | Decimal | Price per unit | Precision: 2 decimal places; must be ≥ 0 |
| `line_total` | Decimal | Quantity × unit price | Calculated; precision: 2 decimal places |

**Business invariants**:
- Belongs to exactly one order
- Line total = quantity × unit price
- Description is free-form and carries all product/service details inline
- No product ID stored; a product_id field may be added later when a catalog is introduced

**Responsibility**: Belongs to exactly one order; line total computed from quantity and unit price

---

## Entity: Customer

**Description**: Represents an individual or business customer. Key attributes:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | Identifier | Unique customer identifier | From S02 Customer Management |
| `type` | Enum | Customer classification | Values: `individual`, `business` |
| `contact_info` | struct | Contact information | Email, phone; used for order communication |
| `eligibility_status` | boolean | Order eligibility flag | Must be `true` for order creation; validated via S02 eligibility port |

**Business invariants**:
- Customers must have at least one contact and one address to be considered eligible for order creation
- Each order references exactly one customer that passes eligibility validation

**Responsibility**: Validated for order eligibility; each order references exactly one customer; eligibility check draws from S02 eligibility port

## Relationships

| Parent | Child | Relationship | Cardinality |
|---|---|---|---|
| Customer | Order | One-to-many | One customer can have many orders; each order belongs to exactly one customer |
| Order | Order Item | One-to-many | One order can have many items; each item belongs to exactly one order |

## Validation Rules (from Requirements)

- **FR-001**: System MUST allow a registered customer to create a new order in draft status
- **FR-002**: System MUST require at least one order item before an order can be confirmed
- **FR-003**: System MUST calculate the order subtotal from item prices and quantities
- **FR-004**: System MUST calculate taxes and total order amount from the subtotal
- **FR-005**: System MUST enforce valid status transitions: draft → confirmed → shipped → delivered, and draft → cancelled
- **FR-006**: System MUST reject invalid status transitions with a clear error message
- **FR-007**: System MUST associate every order with a valid, eligible customer
- **FR-008**: System MUST expose order creation and management through REST API endpoints under `/api/v1/orders`
- **FR-009**: System MUST provide a customer-order relationship that ensures orders belong only to eligible customers