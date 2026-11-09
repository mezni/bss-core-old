<!-- Sync Impact Report:
Version change: N/A (scaffold) → 1.0.0
Modified principles:
  I. Library-First → Modular Monolith/DDD/Clean Architecture (compressed from user input principles 2.1-2.3, 3)
  II. CLI Interface → Technology/Module Standards (compressed from user input principles 4, 5, 6)
  III. Test-First → Testing/Data/Quality (compressed from user input principles 10, 11, 12)
  IV. Integration Testing → API/Db/Security Standards (compressed from user input principles 7, 8, 9)
  V. Observability → Documentation/Definition/Done/Governance (compressed from user input principles 13, 14, 15)
Added sections: Technology Standards (Section 4), Business Module Standards (Section 5), Vertical-Slice Delivery (Section 6), Database and Persistence (Section 7), API Standards (Section 8), Security Standards (Section 9), Testing Standards (Section 10), Code Quality (Section 11), Data Generation (Section 12), Documentation Standards (Section 13), Definition of Done (Section 14), Governance (Section 15)
Removed sections: Placeholder principle titles [PRINCIPLE_1_NAME] through [PRINCIPLE_5_NAME], example descriptions within principle bodies, [SECTION_2_NAME]/[SECTION_2_CONTENT], [SECTION_3_NAME]/[SECTION_3_CONTENT], [GOVERNANCE_RULES], [CONSTITUTION_VERSION], [RATIFICATION_DATE], [LAST_AMENDED_DATE]
Follow-up TODOs: None intentionally deferred
-->
# BSS-Core Constitution

**Project:** BSS-Core  
**Version:** 1.0.0  
**Status:** Active

## 1. Project Mission

BSS-Core is a modular business management system designed to manage customer relationships, products and services, orders, shipments, billing, users, and supporting business operations.

The system must provide:

- Reliable business transaction management.
- Consistent business rules across all modules.
- Secure user access and authorization.
- Traceable business operations.
- A maintainable and extensible architecture.
- A clean and practical user interface.

The system will initially target a single application deployment using SQLite, with the architecture designed to permit future database evolution.

## 2. Architectural Principles

### 2.1 Modular Monolith

The backend MUST follow a modular monolith architecture.

- Each business module MUST have a clearly defined responsibility.
- Each module MUST own its domain logic.
- Modules MUST NOT directly access another module's database repositories.
- Cross-module interactions MUST use explicit application interfaces or domain-level contracts.
- Business modules MUST remain independently understandable and testable.
- Microservices MUST NOT be introduced without an explicit architectural decision.

### 2.2 Domain-Driven Design

The system MUST apply DDD principles.

- Business capabilities MUST be organized into bounded contexts.
- Domain entities MUST protect their business invariants.
- Value Objects MUST represent concepts with domain-specific validation.
- Aggregates MUST enforce consistency boundaries.
- Domain Services MUST contain domain logic that does not naturally belong to one entity.
- Domain Events MAY communicate significant business state changes.
- Domain models MUST NOT depend on infrastructure frameworks.

### 2.3 Clean Architecture

Each business module MUST separate:

1. Domain — entities, value objects, domain services, business rules.
2. Application — use cases, commands, queries, ports, DTOs.
3. Infrastructure — database repositories and external integrations.
4. Presentation — API endpoints and HTTP-specific request/response handling.

Dependency direction MUST point inward.

The domain layer MUST NOT depend on FastAPI, SQLAlchemy, Streamlit, or database implementations.

## 3. Application Separation

The project MUST maintain two independent applications.

### Backend API

- FastAPI owns business operations.
- The API owns authentication and authorization.
- The API owns validation and business rules.
- The API owns persistence and transaction management.
- The API exposes versioned REST endpoints.
- The API MUST NOT depend on Streamlit.

### Frontend Application

- Streamlit provides the user interface.
- Streamlit MUST communicate with the backend through HTTP APIs.
- Streamlit MUST NOT access the database directly.
- Streamlit MUST NOT implement business rules.
- UI components MUST be separated from API communication logic.

## 4. Technology Standards

The initial technology stack MUST use:

| Concern | Technology |
|---|---|
| Language | Python 3.12+ |
| Package management | uv |
| Backend | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | SQLite |
| Schema migrations | Alembic |
| Data validation | Pydantic |
| Frontend | Streamlit |
| Authentication | JWT |
| Password hashing | Argon2id |
| Testing | pytest |
| Code quality | Ruff |
| Test data | Faker |

New dependencies MUST be justified by a concrete requirement.

## 5. Business Module Standards

The system MUST organize business capabilities into explicit modules:

- Identity and Access Management
- Customer Management
- Product and Service Catalog
- Order Management
- Shipment Management
- Billing Management
- Reference Data
- Notifications
- Audit and History
- Reporting

Each module MUST:

- Have a defined business responsibility.
- Define its domain model.
- Define its application use cases.
- Own its persistence implementation.
- Expose only intentional interfaces.
- Include unit and integration tests.
- Provide API endpoints when required.
- Be integrated into the Streamlit application when user-facing.
- Document important business rules.

## 6. Vertical-Slice Delivery

Features MUST be developed as complete vertical slices.

A module is not considered complete merely because its database tables or API endpoints exist.

Every module MUST progress through:

1. Business specification.
2. Requirements clarification.
3. Technical planning.
4. Task breakdown.
5. Domain implementation.
6. Application use-case implementation.
7. Infrastructure and persistence implementation.
8. API implementation.
9. API testing.
10. Streamlit integration.
11. End-to-end testing.
12. Documentation.
13. Acceptance review.

A module MUST NOT be marked complete until all required layers work together.

## 7. Database and Persistence

- SQLAlchemy 2.x MUST be used for persistence.
- Alembic MUST manage database schema changes.
- Database access MUST remain inside infrastructure implementations.
- Business logic MUST NOT contain SQL queries.
- Repositories MUST be defined through application or domain-facing interfaces.
- Database migrations MUST be version-controlled.
- Referential integrity MUST be enforced.
- Transaction boundaries MUST be explicit.
- SQLite is the initial database, not a permanent architectural constraint.

## 8. API Standards

- APIs MUST use REST conventions.
- Endpoints MUST be versioned under `/api/v1`.
- Pydantic MUST validate external request and response data.
- HTTP errors MUST follow a consistent format.
- Business logic MUST remain outside route handlers.
- Pagination MUST be supported for collection endpoints.
- Sensitive information MUST NOT be exposed in API responses.
- API documentation MUST be available through OpenAPI.

## 9. Security Standards

- Authentication MUST be centralized.
- Passwords MUST be hashed using Argon2id.
- Authorization MUST be enforced by the backend.
- Role-based access control MUST be implemented.
- Users MUST NOT access resources outside their permissions.
- Secrets MUST NOT be committed to Git.
- Sensitive operations MUST be auditable.
- Input validation MUST occur at application boundaries.
- Security tests MUST cover authentication and authorization.

## 10. Testing Standards

The project MUST maintain multiple testing levels:

- Unit tests for domain logic.
- Application tests for use cases.
- Integration tests for persistence.
- API tests for HTTP contracts.
- End-to-end tests for complete business workflows.

Tests MUST verify observable behavior and business requirements.

Every important business rule MUST have corresponding automated tests.

A feature MUST NOT be accepted when its required tests fail.

## 11. Code Quality

- Python code MUST follow consistent typing conventions.
- Public interfaces MUST have clear documentation.
- Ruff MUST enforce linting and formatting.
- Functions and classes MUST have focused responsibilities.
- Avoid unnecessary abstractions and premature optimization.
- Duplicate business logic MUST be avoided.
- Errors MUST be handled explicitly.
- Configuration MUST be externalized.
- Logging MUST be structured and must not expose secrets.

## 12. Data Generation

A dedicated data generator MUST support development and testing.

It MUST:

- Generate realistic business data.
- Generate related records across modules.
- Respect foreign-key relationships.
- Support deterministic generation using seeds.
- Support configurable record volumes.
- Support repeatable development environments.
- Avoid production credentials and real sensitive information.

The generator MUST use application-supported persistence mechanisms or dedicated development tooling without introducing business logic duplication.

## 13. Documentation Standards

Documentation MUST be maintained alongside implementation.

- Specifications MUST describe business requirements.
- Plans MUST describe technical implementation decisions.
- Tasks MUST be traceable to requirements.
- Business rules MUST be documented.
- API contracts MUST be documented.
- Architectural decisions MUST be recorded.
- Implementation MUST remain consistent with approved specifications.

## 14. Definition of Done

A feature is complete only when:

- Its specification is approved.
- Its implementation follows the approved architecture.
- Its business rules are implemented.
- Its database changes are migrated.
- Its API contracts are tested.
- Its Streamlit integration is complete when applicable.
- Its automated tests pass.
- Ruff checks pass.
- Its documentation is updated.
- Its end-to-end workflow is verified.
- Its acceptance criteria are satisfied.

## 15. Governance

This constitution is the project's architectural and engineering authority.

Any deviation MUST:

1. Identify the violated principle.
2. Explain why the deviation is necessary.
3. Describe its impact and trade-offs.
4. Be explicitly approved.
5. Be documented in the relevant architecture decision record.

Specifications, plans, tasks, and implementations MUST remain consistent with this constitution.