# Feature Specification: Shipment Management (S04)

**Feature Branch**: `004-feature-shipment-management`

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "from docs/sprint-planning.md s04"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Shipment (Priority: P1)
**Describe this user journey in plain language**:  
An authenticated user can create a new shipment record for an order, initiating the delivery process. The shipment starts in a pending status and carries tracking information.

**Why this priority**:  
This is the foundational shipment flow — without the ability to create shipments, no subsequent delivery lifecycle actions are possible. It delivers immediate business value by enabling the core logistics operation.

**Independent Test**:  
Can be fully tested by creating a shipment for a confirmed order, verifying the shipment is assigned an ID, status is set to pending, and tracking information is captured. The test succeeds even if no other shipment flows are exercised.

**Acceptance Scenarios**:
1. **Given** a confirmed order exists, **When** a new shipment is created, **Then** the shipment is assigned a unique identifier, status is set to pending, and tracking reference is generated.
2. **Given** an order cannot be shipped (e.g., not confirmed), **When** an attempt is made to create a shipment, **Then** the request is rejected with an appropriate error.

---

### User Story 2 - Update Shipment (Priority: P2)
**Describe this user journey in plain language**:  
An authenticated user can update shipment information such as carrier, tracking number, or status. This allows the logistics team to correct or update shipment details as needed.

**Why this priority**:  
Shipment details may need correction during processing (e.g., wrong carrier selected, tracking number typo). This flow ensures data accuracy without requiring creation of a new shipment.

**Independent Test**:  
Can be fully tested by creating a shipment, updating its carrier and tracking number, and verifying the updated information is reflected in the shipment response. The test passes regardless of subsequent status changes.

**Acceptance Scenarios**:
1. **Given** a shipment in pending status, **When** carrier and tracking number are updated, **Then** the shipment reflects the new carrier and tracking information.
2. **Given** a shipment in in-transit status, **When** an attempt is made to update the order reference, **Then** the update is rejected with a clear error indicating the shipment is locked.

---

### User Story 3 - Confirm Delivery (Priority: P3)
**Describe this user journey in plain language**:  
An authenticated user can confirm that an order has been delivered, updating the shipment status to delivered and closing the delivery lifecycle.

**Why this priority**:  
Business operations need to track delivery completion. Clear delivery boundaries enable downstream processes (e.g., billing, feedback requests, order archival).

**Independent Test**:  
Can be fully tested by creating a shipment, updating its status to in-transit, confirming delivery, and verifying the shipment status changes to delivered. The test validates the boundary rules without requiring the full billing workflow.

**Acceptance Scenarios**:
1. **Given** a shipment in in-transit status, **When** delivery is confirmed, **Then** the status changes to delivered and a delivery timestamp is recorded.
2. **Given** a shipment delivered, **When** an attempt is made to confirm delivery again, **Then** the request is rejected with an appropriate error indicating delivery already confirmed.

---

### Edge Cases

- What happens when a shipment is created for a non-confirmed order? → System rejects with error indicating order must be confirmed first
- How does system handle lost tracking information? → System allows updating tracking reference; original tracking is preserved in history
- What occurs when delivery is confirmed for an already-delivered shipment? → System rejects with error indicating delivery already confirmed

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an authenticated user to create a new shipment for a confirmed order
- **FR-002**: System MUST require an order to be in confirmed status before a shipment can be created
- **FR-003**: System MUST calculate and assign a tracking reference number on shipment creation
- **FR-004**: System MUST allow updating shipment carrier and tracking number while in pending status
- **FR-005**: System MUST enforce valid status transitions: pending → in-transit → delivered
- **FR-006**: System MUST reject invalid status transitions with a clear error message
- **FR-007**: System MUST associate every shipment with a valid, confirmed order and ensure shipments belong only to confirmed orders
- **FR-008**: System MUST expose shipment creation and management through REST API endpoints under `/api/v1/shipments`:
  - `POST /api/v1/shipments` (create)
  - `GET /api/v1/shipments` (list with pagination and filtering)
  - `GET /api/v1/shipments/{shipment_id}` (retrieve)
  - `PATCH /api/v1/shipments/{shipment_id}` (update)

## Key Entities *(include if feature involves data)*

- **Shipment**: Represents a delivery request for an order. Key attributes: unique identifier (UUID v4 format: SHIP-550e8400-e29b-41d4-a716-446655440000), status (pending, in-transit, delivered, exception), tracking reference, carrier name, order reference, creation timestamp, delivery timestamp.  
  *Responsibility*: Owns its business invariants (valid status transitions, tracking reference requirements); enforces status transition preconditions in the domain layer; documents required checks (order confirmation status, sequence order); delivery confirmation is terminal; shipment status progresses: pending → in-transit → delivered

- **Order**: Represents a customer's purchase request. Each order can have associated shipments that track delivery progress. One order can have multiple shipments (e.g., split shipments); each shipment belongs to exactly one order.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A customer can create a shipment for a confirmed order in under 2 minutes from the order management interface.
- **SC-002**: A shipment cannot be created for an order that is not in confirmed status; the system rejects the creation request with a clear error.
- **SC-003**: Shipment tracking reference is generated on creation and follows format: SHIP-[UUID v4 substring].
- **SC-004**: Status transitions follow the defined sequence: pending → in-transit → delivered; invalid transitions are rejected at least 95% of the time in automated testing.
- **SC-005**: Every shipment is associated with a confirmed order that passes eligibility validation; shipments for non-confirmed orders are rejected.
- **SC-006**: Shipment carrier and tracking information can be updated while shipment is in pending status.
- **SC-007**: Shipment API create and list operations respond in under 200ms (aligned with S03 Order Management performance goals).

### Qualitative Measures

- Users can understand shipment status at a glance without needing to interpret internal codes.
- Error messages for invalid operations are descriptive and actionable.
- The shipment lifecycle is consistent across API and frontend interface.
- Delivery confirmation properly closes the shipment lifecycle.

## Assumptions

- **Existing order management (S03) provides confirmed orders for shipment creation.**
- **Customers must have at least one confirmed order to be eligible for shipment creation.**
- **Tracking reference is generated automatically on shipment creation; carrier and tracking number can be updated during pending status.**
- **Delivery confirmation is terminal; shipments in delivered status cannot be modified.**
- **S03 Order Management tax calculation applies; no additional shipment-specific pricing is required for S03 MVP.**
- **Shipments reference orders by identifier; no duplicate order data is stored in shipment records.**
- **Split shipments are out of scope for S04 MVP (single shipment per order).**
- **Shipment data import/export uses JSON format for API operations; CSV format supported for bulk import with column mapping to shipment attributes (S05 logistics integration will extend formats).**
- **Data volume assumption: 100-500 shipments/day, supporting <10,000 active shipments with ~20% monthly growth (aligned with S03 Order Management capacity).**
- **Reliability target: 99.9% uptime for core shipment operations; structured JSON logging for all state transitions and critical API errors (aligned with BSS-Core constitution Section 11).**

## Dependencies

- **S03 Order Management**: Must be fully implemented and tested; shipments reference orders from the S03 module; shipment creation requires order to be in confirmed status.
- **S01 Identity & Access**: JWT authentication and permission checks must be available for shipment API endpoints; shipment endpoints use `customer:manage` for write and `customer:view` for read operations.

## Notes

- This specification focuses on the business problem and requirements. Implementation details will be addressed in technical planning and development tasks.
- The order-shipment eligibility check (FR-007) draws from the S03 order status port and does not duplicate business rules.
- Status transition boundaries are designed to be strict; the system enforces these boundaries without exposing internal implementation details.
- Shipment history tracking (S04-09, S04-13) records status changes for audit purposes.
