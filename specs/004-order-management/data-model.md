# Data Model: Order Management (S03)

## Entity: Order

**Attributes**:
- `id`: UUID v4 (format: ORD-550e8400-e29b-41d4-a716-446655440000), primary key, globally unique
- `status`: enumeration — `draft`, `confirmed`, `shipped`, `delivered`, `cancelled`
- `subtotal`: Decimal — sum of (quantity × unit price) for all order items
- `tax_amount`: Decimal — calculated as fixed rate × subtotal (S03 MVP uses fixed tax rate)
- `total`: Decimal — subtotal + tax_amount
- `customer_id`: string — identifier referencing eligible customer from S02 Customer Management
- `created_at`: datetime — timestamp of order creation
- `updated_at`: datetime — timestamp of last order update
- `version`: integer — optimistic concurrency counter, incremented on each mutation

**Relationships**:
- **customer** → one-to-one from S02 Customer Management; customer must be eligible (at least one contact + one address per S02 eligibility rules)
- **items** → one-to-many to Order Item entities

**Business Invariants** (enforced in domain layer):
- At least one Order Item must exist before order can be confirmed (status transition precondition)
- Status transitions follow: draft → confirmed → shipped → delivered, and draft → cancelled
- Cancellation is terminal; orders in cancelled state cannot be restored
- To create a new order after cancellation, customer creates a fresh order
- Order total must be calculated correctly (±2% tolerance) from item prices and quantities
- Invalid status transitions rejected with appropriate error (409 for stale/invalid, 400 for missing requirements)

**Domain Responsibilities**:
- Order aggregate owns business invariants
- Enforces status transition preconditions in domain layer
- Documents required checks: item count, customer eligibility, sequence order
- Cancellation is terminal; no restoration from cancelled state
