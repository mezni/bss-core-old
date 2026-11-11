# Feature Specification: Billing (S05)

**Feature Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "S05 is billing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Invoice (Priority: P1)
**Describe this user journey in plain language**:  
An authenticated user can generate an invoice for a completed order or shipment, capturing the billing details and initiating the payment process.

**Why this priority**:  
Invoice generation is the foundational billing operation — without the ability to create invoices, no subsequent payment processing or revenue recognition is possible. It delivers immediate business value by enabling the core financial operation.

**Independent Test**:  
Can be fully tested by generating an invoice for a completed order, verifying the invoice is assigned an ID, total amount is calculated correctly, and billing information is captured. The test succeeds even if no other billing flows are exercised.

**Acceptance Scenarios**:
1. **Given** a completed order or shipment exists, **When** an invoice is generated, **Then** the invoice is assigned a unique identifier, total amount is calculated from order/shipment totals, and billing information is captured. The test succeeds even if no other billing flows are exercised.
2. **Given** an order cannot be invoiced (e.g., not in a billable status), **When** an attempt is made to generate an invoice, **Then** the request is rejected with an appropriate error.

---

### User Story 2 - Process Payment (Priority: P2)
**Describe this user journey in plain language**:  
An authenticated user can process a payment against an invoice, recording payment details and updating the invoice status.

**Why this priority**:  
Payment processing is essential for completing the billing cycle — invoices must be paid to trigger revenue recognition and customer notifications. This flow ensures payment records are created and invoice status is updated.

**Independent Test**:  
Can be fully tested by processing a payment against an invoice, verifying the payment is assigned an ID, amount matches invoice total, and invoice status updates to paid. The test passes regardless of subsequent status changes.

**Acceptance Scenarios**:
1. **Given** an invoice in pending status, **When** payment details are provided and payment is processed, **Then** the invoice status updates to paid, payment is recorded with timestamp, and payment confirmation is provided.
2. **Given** an invoice already paid, **When** an attempt is made to process payment again, **Then** the request is rejected with a clear error indicating payment already processed.

---

### User Story 3 - View Billing History (Priority: P3)
**Describe this user journey in plain language**:  
An authenticated user can view billing history for their account, seeing all invoices and payments associated with their orders or shipments.

**Why this priority**:  
Business operations need to track billing history for reconciliation, reporting, and customer inquiries. Clear billing history enables downstream processes (e.g., financial reporting, audit, customer support).

**Independent Test**:  
Can be fully tested by viewing billing history for a customer, verifying all invoices and payments are listed with correct amounts and statuses. The test validates the boundary rules without requiring the full accounting workflow.

**Acceptance Scenarios**:
1. **Given** a customer has multiple invoices and payments, **When** billing history is requested, **Then** all invoices and payments are listed with correct amounts, dates, and statuses, ordered by date (most recent first).
2. **Given** a billing history request with no invoices, **When** the request is made, **Then** an empty history is returned with no error.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an authenticated user to generate an invoice for a completed order or shipment
- **FR-002**: System MUST require an order or shipment to be in a billable status before an invoice can be created
- **FR-003**: System MUST calculate the invoice total from associated order/shipment amounts
- **FR-004**: System MUST allow processing a payment against an invoice
- **FR-005**: System MUST enforce valid status transitions: pending → paid (terminal)
- **FR-006**: System MUST reject invalid status transitions with a clear error message
- **FR-007**: System MUST associate every invoice with a valid, confirmed order or shipment and ensure invoices belong only to billable orders or shipments
- **FR-008**: System MUST expose invoice creation and management through REST API endpoints under `/api/v1/invoices`:
  - `POST /api/v1/invoices` (create)
  - `GET /api/v1/invoices` (list with pagination and filtering)
  - `GET /api/v1/invoices/{invoice_id}` (retrieve)
  - `PATCH /api/v1/invoices/{invoice_id}` (update)

### Edge Cases

- What happens when an invoice is generated for an order not in billable status? → System rejects with error indicating order must be in completed or billable status first
- How does system handle lost invoice information? → System allows updating invoice payment status; original invoice number is preserved in history
- What occurs when payment is processed for an already-paid invoice? → System rejects with error indicating invoice already paid

## Key Entities *(include if feature involves data)*

- **Invoice**: Represents a billing document for an order or shipment. Key attributes: unique identifier (UUID v4 format), invoice number, total amount, status (pending, paid, terminal), reference to order or shipment, billing date, payment date, due date.  
  *Responsibility*: Owns its business invariants (valid status transitions, amount calculation); enforces status transition preconditions in the domain layer; documents required checks (order/shipment billable status, sequence order); payment is terminal; invoice status progresses: pending → paid (terminal)

- **Payment**: Represents a payment record against an invoice. Key attributes: unique identifier, amount (must match invoice total), payment method, status, transaction ID, payment date, associated invoice.  
  *Responsibility*: Owns its business invariants (amount must match invoice, payment status tracking); enforces payment invariants in the domain layer

- **Order/Shipment**: Represents a customer's purchase or delivery request. Each order/shipment can have associated invoices that track billing progress. One order/shipment can have multiple invoices; each invoice belongs to exactly one order or shipment.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A customer can generate an invoice for a completed order in under 2 minutes from the order management interface.
- **SC-002**: An invoice cannot be generated for an order that is not in billable status; the system rejects the generation request with a clear error.
- **SC-003**: Invoice unique identifier is generated on creation and follows format: INV-550e8400-e29b-41d4-a716-446655440000.
- **SC-004**: Invoice total matches the associated order/shipment total amount exactly.
- **SC-005**: Payment can be processed for an invoice in pending status; paid invoices cannot be re-processed.
- **SC-006**: Invoice payment status transitions follow the defined sequence: pending → paid (terminal); invalid transitions are rejected at least 95% of the time in automated testing.
- **SC-007**: Invoice API create and list operations respond in under 200ms (aligned with financial API performance goals).
- **SC-008**: Invoice payment properly closes the billing lifecycle; further modifications are rejected with appropriate error.

### Qualitative Measures

- Users can understand invoice status at a glance without needing to interpret internal codes.
- Error messages for invalid operations are descriptive and actionable.
- The billing lifecycle is consistent across API and frontend interface.
- Invoice generation properly finalizes the revenue recognition process.

## Assumptions

- **Existing order management (S03) provides completed orders for invoice generation.**
- **Customers must have at least one completed order to be eligible for invoice generation.**
- **Invoice number is generated optionally on creation; payment date can be provided or set to current timestamp.**
- **Invoice status transitions are strict; the system enforces these boundaries without exposing internal implementation details.**
- **Payment method validation is handled by payment processor integration; S05 MVP supports basic card and bank transfer methods.**
- **Data volume assumption: 10-100 invoices per month, supporting <500 active invoices with ~10% monthly growth.**
- **Reliability target: 99.9% uptime for core billing operations; structured JSON logging for all state transitions and critical API errors.**
- **Security model: JWT authentication with role-based access control; user:billing for write operations, user:view for read operations.**

## Dependencies

- **S03 Order Management**: Must be fully implemented and tested; invoices reference orders from the S03 module; invoice generation requires order to be in completed status.
- **S01 Identity & Access**: JWT authentication and permission checks must be available for invoice API endpoints; invoice endpoints use `user:billing` for write and `user:view` for read operations.
- **S02 Payment Integration**: Payment gateway integration (e.g., Stripe, PayPal) for processing payments; S05 MVP supports basic card and bank transfer methods.

## Notes

- This specification focuses on the business problem and requirements. Implementation details will be addressed in technical planning and development tasks.
- The invoice-eligible check (FR-007) draws from the S03 order status port and does not duplicate business rules.
- Status transition boundaries are designed to be strict; the system enforces these boundaries without exposing internal implementation details.
- Payment is terminal; invoices in paid status cannot be modified.
- Split shipments are out of scope for S05 MVP (single invoice per order).
- Invoice history tracking (S05-09, S05-13) records status changes for audit purposes.

### Constitution Cross-Reference

- **Section 2.1 Modular Monolith**: Billing module has clearly defined responsibility, owns domain logic, no direct repository access by other modules
- **Section 2.2 Domain-Driven Design**: Invoice aggregate protects business invariants (valid status transitions, amount calculation)
- **Section 2.3 Clean Architecture**: Dependency points inward; billing domain layer does not depend on FastAPI, SQLAlchemy, or database implementations
- **Section 4 Technology Standards**: Performance targets (200ms), reliability (99.9%), structured JSON logging, JSON data formats all aligned with constitution Section 4 technology stack
- **Section 6 Vertical-Slice Delivery**: Billing module progresses through all required layers: business specification → requirements clarification → technical planning → task breakdown → domain implementation → application use-case implementation → infrastructure and persistence implementation → API implementation → API testing → documentation → acceptance review
- **Section 7 Database and Persistence**: SQLAlchemy 2.x, Alembic for migrations, business logic no SQL, repositories through domain-facing interfaces; data volume assumptions support database design
- **Section 8 API Standards**: REST conventions, /api/v1 versioning, Pydantic validation, consistent HTTP errors, Pagination (pending for S05; will follow S02 pattern), no sensitive info exposure, OpenAPI docs
- **Section 9 Security Standards**: Centralized authentication (JWT), enforced authorization, RBAC, users restricted to permissions, secrets not in Git, auditable sensitive ops, input validation at boundaries - **directly validated by this specification**
- **Section 10 Testing Standards**: Multiple testing levels (unit, application, integration, API), every important business rule has automated tests
- **Section 11 Code Quality**: Python code follows consistent typing conventions; public interfaces have clear documentation; Ruff enforces linting and formatting
- **Section 14 Definition of Done**: All DoD criteria satisfied per updated checklist (16/16 items passing)