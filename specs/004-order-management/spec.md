# Feature Specification: Order Management

**Feature Branch**: `004-feature-order-management`

**Created**: 2026-11-09

**Status**: Draft

**Input**: User description: "from docs/sprint-planning.md s03"

## Clarifications

**Session 2026-11-09**

- Q: How should order identifiers be generated and what format should they use? → A: UUID v4 format (e.g., ORD-550e8400-e29b-41d4-a716-446655440000)
- Q: How should order items reference the product or service being ordered? → A: Free-form description field + inline price/quantity (no product ID; all details carried within the order item itself; extensible with product_id added later when a catalog is introduced)
- Q: What preconditions govern order status transitions? → A: Domain-layer enforcement with API-layer validation; confirmed requires ≥1 item, cancelled only in draft, shipped requires confirmed, delivered requires shipped; preconditions documented in entity responsibilities and return appropriate errors (409 for stale/invalid, 400 for missing requirements)
- Q: Can orders in cancelled state be restored? → A: Cancellation is terminal; orders in cancelled state cannot be restored. To create a new order, the customer creates a fresh order. Aligns with simple domain modeling and avoids state-transition ambiguity.

- Q: Should order listing endpoints support pagination and search/filter? → A: Follow S02 pattern with `q`, `status`, `page`, `page_size` parameters; maintain consistency across modules; search matches order ID, customer reference, and status; page defaults to 1, page_size defaults to 20, max 100

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Order (Priority: P1)
**Describe this user journey in plain language**:  
A registered customer can create a new order for their business. The order starts in a draft state and requires at least one order item before it can be confirmed.

**Why this priority**:  
This is the foundational order flow — without the ability to create orders, no subsequent order lifecycle actions are possible. It delivers immediate business value by enabling the core commerce operation.

**Independent Test**:  
Can be fully tested by creating an order with valid customer ID and at least one item, verifying the order is assigned an ID, status is set to draft, and the total is calculated correctly. The test succeeds even if no other order flows are exercised.

**Acceptance Scenarios**:
1. **Given** a valid customer exists, **When** a new order is created with at least one order item, **Then** the order is assigned a unique identifier, status is set to draft, and the subtotal reflects the item prices.
2. **Given** a customer does not exist, **When** an attempt is made to create an order, **Then** the request is rejected and the customer is validated for eligibility.

---

### User Story 2 - Manage Order Items (Priority: P2)
**Describe this user journey in plain language**:  
An authenticated user can add, modify, or remove individual items from an order. Each item represents a product or service line with a quantity, description, and price. The order total updates automatically as items change.

**Why this priority**:  
Orders must contain items before they can be confirmed. This flow allows the user to build up the order incrementally, which is essential for a flexible commerce workflow.

**Independent Test**:  
Can be fully tested by creating an order with one item, adding a second item, modifying the quantity of the first item, removing the second item, and verifying the order total reflects only the remaining item. The test passes regardless of whether the order is later confirmed or cancelled.

**Acceptance Scenarios**:
1. **Given** an order in draft status, **When** a new item is added, **Then** the order contains the item and the total reflects its price.
2. **Given** an order with items, **When** an item is removed, **Then** the order total is recalculated without the removed item.
3. **Given** an order with items, **When** item quantities are updated, **Then** the order total reflects the new quantities.

---

### User Story 3 - Order Lifecycle Transitions (Priority: P3)
**Describe this user journey in plain language**:  
An order progresses through well-defined status stages — draft → confirmed → shipped → delivered → cancelled. Each transition has preconditions and is irreversible or requires specific actions (e.g., confirmation requires at least one item; cancellation is only permitted in draft status).

**Why this priority**:  
Business operations need to track order progress. Clear status boundaries prevent invalid states and enable downstream processes (e.g., shipping cannot begin until the order is confirmed).

**Independent Test**:  
Can be fully tested by creating an order, attempting status transitions under the correct conditions, and verifying that invalid transitions are rejected. The test validates the boundary rules without requiring the full shipment or billing workflows.

**Acceptance Scenarios**:
1. **Given** an order in draft status with at least one item, **When** the order is confirmed, **Then** the status changes to confirmed and the order cannot be arbitrarily modified.
2. **Given** an order in draft status, **When** the order is cancelled, **Then** the status changes to cancelled and the order is removed from active order queues.
3. **Given** a confirmed order, **When** an attempt is made to cancel it, **Then** the request is rejected with an appropriate error indicating invalid state.
4. **Given** a confirmed order, **When** the status is changed to shipped, **Then** the order timestamp is recorded and the order moves to the next lifecycle stage.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a registered customer to create a new order in draft status.
- **FR-002**: System MUST require at least one order item before an order can be confirmed.
- **FR-003**: System MUST calculate the order subtotal from item prices and quantities.
- **FR-004**: System MUST calculate taxes and total order amount from the subtotal.
- **FR-005**: System MUST enforce valid status transitions: draft → confirmed → shipped → delivered, and draft → cancelled.
- **FR-006**: System MUST reject invalid status transitions with a clear error message.
- **FR-007**: System MUST associate every order with a valid, eligible customer.
- **FR-008**: System MUST expose order creation and management through REST API endpoints under `/api/v1/orders`.
- **FR-009**: System MUST provide a customer-order relationship that ensures orders belong only to eligible customers.

### Key Entities *(include if feature involves data)*

- **Order**: Represents a customer's purchase request. Key attributes: unique identifier (UUID v4, format: ORD-550e8400-e29b-41d4-a716-446655440000), status (draft, confirmed, shipped, delivered, cancelled), subtotal, tax amount, total, customer reference, creation timestamp, last update timestamp.  
  *Responsibility*: Owns its business invariants (e.g., at least one item before confirmation, valid status transitions); enforces status transition preconditions in the domain layer and documents required checks (item count, customer eligibility, sequence order); cancellation is terminal and cannot be restored; to create a new order after cancellation, the customer creates a fresh order.

- **Order Item**: Represents a line item within an order. Key attributes: description (free-form), quantity, unit price, line total.  
  *Responsibility*: Belongs to exactly one order; line total = quantity × unit price. Description is free-form and carries all product/service details inline; no product ID is stored; a product_id field may be added later when a catalog is introduced.

- **Customer**: Represents an individual or business customer. Key attributes: identifier, type (individual/business), contact information, eligibility status.  
  *Responsibility*: Validated for order eligibility; each order references exactly one customer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A customer can create an order in under 2 minutes from the order management interface.
- **SC-002**: An order cannot be confirmed without at least one order item; the system rejects the confirmation request with a clear error.
- **SC-003**: Order totals (subtotal, tax, total) are calculated correctly for any combination of item prices and quantities, with a measurement tolerance of ±2%.
- **SC-004**: Status transitions follow the defined sequence: draft → confirmed → shipped → delivered, and draft → cancelled; invalid transitions are rejected at least 95% of the time in automated testing.
- **SC-005**: Every order is associated with a customer that passes eligibility validation; orders for ineligible customers are rejected.

### Qualitative Measures

- Users can understand order status at a glance without needing to interpret internal codes.
- Error messages for invalid operations are descriptive and actionable.
- The order lifecycle is consistent across API and frontend interface.

## Assumptions

- **Existing customer management (S02) provides customer records for order creation.**
- **Customers must have at least one contact and one address to be considered eligible for order creation.**
- **Order items reference products or services by description and price; no separate product catalog is in scope for S03 MVP.**
- **Tax calculation uses a fixed rate applied to the subtotal; no jurisdiction-specific tax logic is required for S03 MVP.**

## Dependencies

- **S02 Customer Management**: Must be fully implemented and tested; orders reference customers from the S02 module; order listing follows S02 pagination/search pattern for consistency.
- **S01 Identity & Access**: JWT authentication and permission checks must be available for order API endpoints; order endpoints use `customer:view` for read and `customer:manage` for write/list operations.

## Notes

- This specification focuses on the business problem and requirements. Implementation details will be addressed in technical planning and development tasks.
- The customer-order eligibility check (FR-007) draws from the S02 eligibility port and does not duplicate business rules.
- Status transition boundaries are designed to be strict; the system enforces these boundaries without exposing internal implementation details.