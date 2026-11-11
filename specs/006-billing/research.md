# Research: Billing Feature (S05)

**Generated**: 2026-11-10
**Feature**: Billing (S05)
**Spec**: specs/005-billing/spec.md

## Clarification Research

### Question 1: Security and privacy model for billing data

**Decision:** JWT with role-based access control (RBAC)

**Rationale:** This decision aligns with BSS-Core constitution Section 9 (Security Standards), which mandates centralized authentication, role-based access control, and users restricted to permissions. The existing S02 Identity & Access module already uses JWT, making this the most consistent choice. RBAC provides clear authorization boundaries: `user:billing` for write operations (invoice creation, payment processing) and `user:view` for read operations (invoice listing, retrieval). This decision materially impacts API design, data modeling, and test design - defining explicit permission checks at the domain layer rather than duplicating logic in route handlers.

**Alternatives considered:**
- JWT only with project-level permissions (Option A): Simpler but less granular; does not distinguish between management and read permissions, requiring additional checks elsewhere in the codebase.
- API key authentication (Option C): Does not align with constitution Section 9 (centralized authentication requirement); would require authentication layer redesign.
- OAuth2 with project scopes (Option D): Over-engineered for S05 MVP; adds complexity without proportional benefit for internal billing use case.
- Session-based auth with JWT fallback (Option E): Hybrid approach increases implementation complexity; no clear advantage over pure JWT RBAC for this use case.

**Impact:** Security model clarification directly affects:
- API endpoint permission checks (FR-001, FR-008)
- Data model security fields and validation
- Test design for authorization boundary testing
- Constitution compliance (Section 9)

## Research Tasks Completed

All technical context items have been verified against the BSS-Core constitution and the feature specification. No additional research required.

### Constitution Cross-Reference

- **Section 2.1 Modular Monolith**: Billing module has clearly defined responsibility, owns domain logic, no direct repository access by other modules
- **Section 2.2 Domain-Driven Design**: Invoice aggregate protects business invariants (valid status transitions, amount calculation)
- **Section 2.3 Clean Architecture**: Dependency points inward; billing domain layer does not depend on FastAPI, SQLAlchemy, or database implementations
- **Section 4 Technology Standards**: Performance targets (200ms), reliability (99.9%), structured JSON logging, JSON data formats all aligned with constitution Section 4 technology stack
- **Section 6 Vertical-Slice Delivery**: Billing module progresses through all required layers
- **Section 7 Database and Persistence**: SQLAlchemy 2.x, Alembic for migrations, business logic no SQL, repositories through domain-facing interfaces; data volume assumptions support database design
- **Section 8 API Standards**: REST conventions, /api/v1 versioning, Pydantic validation, consistent HTTP errors, Pagination (pending for S05; will follow S02 pattern), no sensitive info exposure, OpenAPI docs
- **Section 9 Security Standards**: Centralized authentication (JWT), enforced authorization, RBAC, users restricted to permissions, secrets not in Git, auditable sensitive ops, input validation at boundaries - **directly validated by this clarification**
- **Section 10 Testing Standards**: Multiple testing levels (unit, application, integration, API), every important business rule has automated tests
- **Section 11 Code Quality**: Python code follows consistent typing conventions; public interfaces have clear documentation; Ruff enforces linting and formatting
- **Section 14 Definition of Done**: All DoD criteria satisfied per updated checklist (16/16 items passing)