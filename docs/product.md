# BSS Core — Product Definition

## 1. Product Overview

### 1.1 Product Name

BSS Core

### 1.2 Product Description

BSS Core is a modular Business Support System designed to centralize and manage essential business operations through an integrated platform.

The system provides a unified environment for managing:

- Customers
- Orders
- Shipments
- Billing
- Users and access control

The platform exposes business capabilities through REST APIs and provides a web-based management interface using Streamlit.

BSS Core follows a modular monolith architecture, Domain-Driven Design (DDD), and Clean Architecture principles.

### 1.3 Product Vision

Build a maintainable, extensible and reliable business management platform that centralizes operational workflows and provides consistent access to business information.

The platform should support future business growth without requiring a complete architectural redesign.

## 2. Business Objectives

The primary objectives are:

| ID | Objective | Expected Outcome |
|---|---|---|
| OBJ-01 | Centralize customer information | Unified customer records |
| OBJ-02 | Manage business orders | Consistent order lifecycle |
| OBJ-03 | Track shipments | Shipment visibility and traceability |
| OBJ-04 | Manage billing operations | Accurate invoice and payment tracking |
| OBJ-05 | Centralize user management | Controlled access to business operations |
| OBJ-06 | Integrate business workflows | Consistent data across modules |
| OBJ-07 | Provide operational visibility | Management dashboards and reporting |
| OBJ-08 | Support extensibility | Ability to introduce new business capabilities |

## 3. Target Users

### 3.1 System Administrator

Responsibilities:

- Manage user accounts.
- Assign roles and permissions.
- Configure system access.
- Monitor system operations.

### 3.2 Customer Service Agent

Responsibilities:

- Register customers.
- Update customer information.
- View customer history.
- Review customer orders.
- Assist with customer requests.

### 3.3 Sales Operator

Responsibilities:

- Create orders.
- Manage order items.
- Monitor order status.
- Review customer order history.

### 3.4 Logistics Operator

Responsibilities:

- Create shipments.
- Assign shipment information.
- Update shipment status.
- Track deliveries.

### 3.5 Billing Operator

Responsibilities:

- Generate invoices.
- Record payments.
- Monitor outstanding balances.
- Review billing history.

### 3.6 Business Manager

Responsibilities:

- Monitor business operations.
- Review customer and order statistics.
- Monitor shipment performance.
- Review billing indicators.
- Access operational reports.

## 4. Product Scope

### 4.1 In-Scope Modules

| Module | Main Capabilities |
|---|---|
| Identity & Access Management | Authentication, users, roles, permissions |
| Customer Management | Customer registration, profiles, contacts, addresses |
| Order Management | Order creation, order items, order lifecycle |
| Shipment Management | Shipment creation, tracking, delivery status |
| Billing Management | Invoice management, payment recording, outstanding balances |

### 4.2 Supporting Capabilities

The following capabilities support the business modules:

- Dashboard and reporting.
- Search and filtering.
- Pagination and sorting.
- Audit logging.
- Data validation.
- Synthetic data generation.
- API error handling.
- Configuration management.

### 4.3 Out of Scope — Initial Release

The following are not part of the initial release:

- Payment gateway integration.
- Real-time carrier integrations.
- Automated accounting reconciliation.
- Tax filing and regulatory submission.
- Advanced business intelligence.
- Microservices deployment.
- Native mobile applications.
- AI-powered business automation.

These capabilities may be introduced in future releases through dedicated specifications.

## 5. Functional Requirements

### 5.1 Identity & Access Management

| ID | Requirement | Priority |
|---|---|---|
| FR-IAM-001 | Users can authenticate using credentials | Must |
| FR-IAM-002 | Administrators can create users | Must |
| FR-IAM-003 | Administrators can update users | Must |
| FR-IAM-004 | Administrators can deactivate users | Must |
| FR-IAM-005 | Administrators can assign roles | Must |
| FR-IAM-006 | The system enforces role-based permissions | Must |
| FR-IAM-007 | Users can change their passwords | Must |
| FR-IAM-008 | The system manages authentication sessions or tokens | Must |

### 5.2 Customer Management

| ID | Requirement | Priority |
|---|---|---|
| FR-CUS-001 | Create customer records | Must |
| FR-CUS-002 | View customer details | Must |
| FR-CUS-003 | Update customer information | Must |
| FR-CUS-004 | Deactivate customers | Must |
| FR-CUS-005 | Manage customer contacts | Must |
| FR-CUS-006 | Manage customer addresses | Must |
| FR-CUS-007 | Search and filter customers | Must |
| FR-CUS-008 | View customer order history | Should |

### 5.3 Order Management

| ID | Requirement | Priority |
|---|---|---|
| FR-ORD-001 | Create customer orders | Must |
| FR-ORD-002 | Add products or services to orders | Must |
| FR-ORD-003 | Calculate order totals | Must |
| FR-ORD-004 | Update order information | Must |
| FR-ORD-005 | Manage order statuses | Must |
| FR-ORD-006 | View order details | Must |
| FR-ORD-007 | Search and filter orders | Must |
| FR-ORD-008 | Associate orders with customers | Must |

### 5.4 Shipment Management

| ID | Requirement | Priority |
|---|---|---|
| FR-SHP-001 | Create shipments associated with orders | Must |
| FR-SHP-002 | Manage shipment details | Must |
| FR-SHP-003 | Assign tracking references | Must |
| FR-SHP-004 | Update shipment status | Must |
| FR-SHP-005 | Record shipment and delivery dates | Must |
| FR-SHP-006 | View shipment history | Should |
| FR-SHP-007 | Search and filter shipments | Must |

### 5.5 Billing Management

| ID | Requirement | Priority |
|---|---|---|
| FR-BIL-001 | Generate invoices for orders | Must |
| FR-BIL-002 | View invoice details | Must |
| FR-BIL-003 | Record payments | Must |
| FR-BIL-004 | Track invoice status | Must |
| FR-BIL-005 | Calculate outstanding balances | Must |
| FR-BIL-006 | View payment history | Must |
| FR-BIL-007 | Search and filter invoices | Must |

## 6. Business Workflows

### 6.1 Customer-to-Order Workflow

1. Customer is registered.
2. Customer information is validated.
3. An operator creates an order.
4. Order items are added.
5. Order totals are calculated.
6. Order is confirmed.
7. Order becomes available for shipment processing.

### 6.2 Order-to-Shipment Workflow

1. An eligible order is selected.
2. A shipment is created.
3. Shipment information is recorded.
4. Shipment is prepared.
5. Shipment status is updated during processing.
6. Delivery is confirmed.
7. Shipment is marked as delivered.

### 6.3 Order-to-Billing Workflow

1. An eligible order is selected.
2. An invoice is generated.
3. Invoice details are calculated.
4. Invoice is issued.
5. Payment is recorded.
6. Outstanding balance is recalculated.
7. Invoice is marked as paid when fully settled.

## 7. Business Rules

The following are initial business rules and must be refined in the relevant feature specifications.

### Customer Rules

- Every customer must have a unique business identifier.
- A customer may have multiple contacts.
- A customer may have multiple addresses.
- Deactivated customers cannot be used for new orders unless an explicit business exception is approved.

### Order Rules

- Every order belongs to one customer.
- An order must contain at least one item before confirmation.
- Order totals must be calculated by the backend.
- Confirmed orders must follow controlled status transitions.
- Historical order information must remain traceable.

### Shipment Rules

- A shipment must reference an eligible order.
- Shipment tracking references must be unique when provided.
- Shipment status transitions must follow defined business rules.
- Delivery confirmation must include a delivery date.

### Billing Rules

- An invoice must reference an eligible order.
- Invoice totals must be calculated by the backend.
- Payments cannot exceed the outstanding balance unless an explicit overpayment policy is defined.
- Fully paid invoices must have zero outstanding balance.
- Financial records must remain auditable.

### Identity Rules

- Users must authenticate before accessing protected functionality.
- Authorization must be enforced by the backend.
- Permissions must be checked for protected operations.
- Passwords must never be stored in plaintext.

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-001 | Security | Authentication and authorization for protected APIs |
| NFR-002 | Security | Secure password hashing |
| NFR-003 | Security | Input validation and protection against common API attacks |
| NFR-004 | Performance | Efficient database queries and pagination |
| NFR-005 | Reliability | Consistent transactions for business operations |
| NFR-006 | Maintainability | Modular architecture and separation of concerns |
| NFR-007 | Testability | Automated unit, integration and API tests |
| NFR-008 | Observability | Structured logging and meaningful error reporting |
| NFR-009 | Data Integrity | Database constraints and referential integrity |
| NFR-010 | Extensibility | New modules can be introduced without restructuring the entire application |
| NFR-011 | Usability | Consistent and understandable user interface |
| NFR-012 | Portability | Development environment reproducible using uv |

Specific numerical performance, availability and recovery targets will be defined when deployment requirements are established.

## 9. Product Architecture Context

BSS Core consists of two applications.

### Backend API

`bss_core_api`

Responsibilities:

- Expose REST APIs.
- Enforce authentication and authorization.
- Execute business use cases.
- Validate business rules.
- Manage database transactions.
- Persist business information.
- Coordinate module interactions.

### Frontend Application

`bss_core_app`

Responsibilities:

- Provide Streamlit user interfaces.
- Display operational dashboards.
- Manage user interactions.
- Consume backend REST APIs.
- Display validation errors and business results.

### Communication

```text
+--------------------------+
|     Streamlit App        |
|      bss_core_app        |
+------------+-------------+
             |
             | HTTP / REST
             |
+------------v-------------+
|       FastAPI API        |
|      bss_core_api        |
+------------+-------------+
             |
             v
+--------------------------+
|     Business Modules     |
|                          |
| IAM | Customer | Order   |
| Shipment | Billing       |
+------------+-------------+
             |
             v
+--------------------------+
|       SQLAlchemy         |
+------------+-------------+
             |
             v
+--------------------------+
|         SQLite           |
+--------------------------+
```

## 10. Data Management

The initial release uses SQLite.

The database must support:

- Customer records.
- Customer contacts and addresses.
- Orders and order items.
- Shipments and shipment information.
- Invoices and payments.
- Users, roles and permissions.
- Audit information where required.

Database schema evolution must be managed through Alembic migrations.

Synthetic data generation must support development and testing without relying on real customer information.

## 11. Success Criteria

The initial release will be considered successful when:

| ID | Success Criterion | Measurement |
|---|---|---|
| SC-001 | Customer operations work correctly | Customer CRUD and validation tests pass |
| SC-002 | Order lifecycle is supported | Order workflow tests pass |
| SC-003 | Shipment tracking is available | Shipment workflow tests pass |
| SC-004 | Billing lifecycle is supported | Invoice and payment tests pass |
| SC-005 | Access is controlled | Authentication and authorization tests pass |
| SC-006 | Modules are independently testable | Module-level test suites pass |
| SC-007 | Applications are separated | Streamlit uses REST APIs only |
| SC-008 | Data is reproducible | Synthetic data generation works with a fixed seed |
| SC-009 | Documentation is maintained | Architecture and feature documentation reflect implementation |

## 12. Release Strategy

### Release 1 — Core Foundation

- Project initialization.
- Backend and frontend application setup.
- Database configuration.
- Authentication and authorization foundation.
- Development and testing infrastructure.

### Release 2 — Customer Management

- Customer CRUD.
- Contacts and addresses.
- Search and filtering.

### Release 3 — Order Management

- Order creation.
- Order items.
- Order calculations.
- Order lifecycle.

### Release 4 — Shipment Management

- Shipment creation.
- Shipment tracking.
- Delivery lifecycle.

### Release 5 — Billing Management

- Invoice generation.
- Payment recording.
- Outstanding balance calculations.

### Release 6 — Operational Experience

- Dashboards.
- Reporting.
- Synthetic data scenarios.
- Cross-module workflow validation.

## 13. Product Constraints and Assumptions

### Confirmed Technical Decisions

| Item | Decision |
|---|---|
| Project name | BSS Core |
| Language | Python |
| Package management | uv |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Frontend | Streamlit |
| Initial database | SQLite |
| Architecture | DDD + Clean Architecture |
| Application structure | Separate API and frontend applications |
| Development methodology | Spec Kit |

### Assumptions Requiring Validation

- The platform initially supports one organization.
- Customer, order, shipment and billing operations are managed by internal users.
- External payment processing is not part of the initial release.
- External shipping provider integrations are not part of the initial release.
- Currency, tax rules and invoice numbering policies require explicit business decisions.
- Product or service catalog ownership requires further domain clarification.

These assumptions must not be treated as confirmed requirements until validated.

## 14. Future Evolution

Potential future capabilities include:

- Multi-tenant architecture.
- PostgreSQL migration.
- External payment integrations.
- Shipping provider integrations.
- Advanced reporting and analytics.
- Notification services.
- Background processing.
- Event-driven integrations.
- Audit and compliance enhancements.

Future capabilities must be introduced through documented requirements and architecture decisions.

---

**Document status:** Initial product definition  
**Project:** BSS Core  
**Architecture:** Modular Monolith, DDD and Clean Architecture  
**Development methodology:** Specification-Driven Development
