# Research: Customer Management (S02)

**Date**: 2026-11-09

All Technical Context items are resolved from the constitution, the existing codebase, and the five clarifications recorded in `spec.md`. No blocking `NEEDS CLARIFICATION` items remain.

## Decisions

### D1. Customer identity and type-specific uniqueness

- **Decision**: Each customer receives a system-generated UUID. Individual customers must have a unique email address; business customers must have a unique registration/tax identifier. Uniqueness is scoped by customer type.
- **Rationale**: Matches clarification Q1 and the business need to distinguish consumers from organizations. Type-scoped uniqueness lets a business and an individual legitimately share an email without creating a false duplicate.
- **Alternatives considered**: Global email uniqueness (rejected: blocks legitimate business/individual overlap); display-name uniqueness (rejected: names are not reliable identifiers); no uniqueness (rejected: allows duplicates).

### D2. Type-specific uniqueness enforcement in SQLite

- **Decision**: Enforce with two partial unique indexes: `(email)` where `customer_type = 'INDIVIDUAL'`, and `(registration_number)` where `customer_type = 'BUSINESS'`. Application-level checks provide friendly errors; the database indexes provide the hard guarantee.
- **Rationale**: SQLite supports partial indexes, and they express the type-scoped rule directly. Application checks alone risk race-condition duplicates.
- **Alternatives considered**: A single normalized `unique_key` column (rejected: obscures intent and complicates nullable business/individual fields); full unique constraints on nullable columns (rejected: NULL semantics differ and cross-type collisions remain possible).

### D3. Aggregate boundaries

- **Decision**: `Customer` is the aggregate root; `Contact` and `Address` are child entities owned by the customer. All mutations go through the customer aggregate/use cases in one transaction.
- **Rationale**: Eligibility depends on the customer plus its contacts and addresses, so they must be consistent within one boundary. Matches constitution Section 2.2.
- **Alternatives considered**: Separate Contact/Address aggregates (rejected: cross-aggregate invariants for eligibility become eventually consistent); embedding contacts/addresses as JSON (rejected: poor querying and validation).

### D4. Soft deactivation and reactivation

- **Decision**: A `status` field with `ACTIVE` and `INACTIVE`. Deactivation sets `INACTIVE` and preserves all children and history; reactivation sets `ACTIVE`. No hard delete endpoint.
- **Rationale**: Clarification Q3 and FR-005/FR-017. Downstream documents need stable historical references.
- **Alternatives considered**: Hard delete (rejected: breaks historical references and auditability); archived state (deferred: adds a third lifecycle state without a current requirement).

### D5. Eligibility rule

- **Decision**: A customer is eligible for new business activity only when `status = ACTIVE`, it has at least one contact, and it has at least one address. Ineligibility does not block registration or maintenance.
- **Rationale**: Clarification Q5 and FR-012. Downstream modules must not transact with unreachable or undeliverable customers.
- **Alternatives considered**: Require contacts/addresses at registration (rejected: slows data entry); no minimum (rejected: permits unusable customer records).

### D6. Optimistic concurrency

- **Decision**: Each customer carries an integer `version`. Updates submit the expected version; the repository performs a conditional update and raises a conflict when the version no longer matches. The API returns `409 Conflict` with the current version.
- **Rationale**: Clarification Q4 and FR-016. SQLite lacks reliable row-level locking across processes; version checks prevent silent lost updates.
- **Alternatives considered**: Last-write-wins (rejected: silent data loss); pessimistic locking (rejected: poor fit for SQLite and web request lifetimes); field-level merge (rejected: unnecessary complexity for this scope).

### D7. Authorization model

- **Decision**: Two permissions consumed from the Identity & Access module: `customer:view` for retrieval/search/list/eligibility and `customer:manage` for create/update/deactivate/reactivate/contact/address mutations. Enforced by FastAPI dependencies at the API boundary.
- **Rationale**: Clarification Q2 and FR-013; constitution Section 9 requires backend enforcement and least privilege.
- **Alternatives considered**: A single access permission (rejected: violates least privilege); role-name checks (rejected: couples the module to specific roles and is brittle).

### D8. Cross-module interface

- **Decision**: Expose an application-level `CustomerEligibilityPort` and read DTOs that return current customer data and eligibility. Order/Shipment/Billing modules depend on this port, never on the customer repository or ORM.
- **Rationale**: Constitution Sections 2.1 and 5 prohibit cross-module repository access. A port keeps the module boundary explicit.
- **Alternatives considered**: Direct ORM imports (rejected: violates module boundaries); shared database views (rejected: couples modules at the schema level).

### D9. API pagination and filtering

- **Decision**: Collection endpoints use `page` and `page_size` (default 20, max 100) and return `items`, `page`, `page_size`, and `total`. Filters: `customer_type`, `status`, and `q` (search across name, email, registration number).
- **Rationale**: Constitution Section 8 requires pagination; SC-003 requires efficient search over 10k records.
- **Alternatives considered**: Cursor pagination (deferred: offset pagination is simpler and adequate at this scale); no pagination (rejected: violates constitution).

### D10. Identifier strategy

- **Decision**: UUIDv4 string primary keys for customers, contacts, and addresses.
- **Rationale**: Stable, non-enumerable identifiers that are safe to expose in URLs and across modules, and friendly to future PostgreSQL migration.
- **Alternatives considered**: Auto-increment integers (rejected: enumerable and harder to merge across environments); ULID (viable but adds a dependency for no current need).

### D11. Testing database strategy

- **Decision**: Unit tests use plain domain objects. Application tests use an in-memory fake repository. Integration tests use a temporary SQLite file with migrations applied. Contract tests use FastAPI's test client with a dependency-overridden session.
- **Rationale**: Fast, deterministic tests at each level while still exercising real SQL and migrations.
- **Alternatives considered**: Only end-to-end tests (rejected: slow and poor failure isolation); in-memory SQLite for integration (rejected: partial indexes and migration behavior are better validated against a file database).

### D12. Validation layering

- **Decision**: Pydantic validates transport shape at the API boundary; domain value objects and the aggregate enforce business rules. Use cases translate domain errors into application errors, and the API maps them to consistent HTTP responses.
- **Rationale**: Constitution Sections 2.3, 8, and 11; prevents business rules from leaking into schemas.
- **Alternatives considered**: All validation in Pydantic (rejected: domain rules become framework-coupled); all validation in the domain (rejected: poor error messages for malformed input).

### D13. Migration and metadata wiring

- **Decision**: Define a SQLAlchemy 2.x declarative `Base`, set `target_metadata` in `migrations/env.py`, and create a single Alembic revision for the three customer tables, indexes, and foreign keys.
- **Rationale**: Constitution Section 7 requires version-controlled migrations; current `env.py` has `target_metadata = None`, which must be wired for autogeneration.
- **Alternatives considered**: `create_all` at startup (rejected: violates migration standards); hand-written SQL outside Alembic (rejected: not version-controlled).

### D14. Frontend dependencies

- **Decision**: Add `streamlit` and an HTTP client to project dependencies for the customer UI. The UI calls the backend API and renders results; it contains no business rules.
- **Rationale**: The existing `src/frontend/app.py` imports Streamlit and `requests`, but neither is declared in `pyproject.toml`. This gap must be closed for the UI to run.
- **Alternatives considered**: Using `httpx` for the frontend client (viable; already a dependency) — prefer reusing the existing dependency if practical.

## Resolved Clarifications

| # | Question | Answer | Impact |
|---|---|---|---|
| Q1 | What uniquely identifies a customer? | Type-specific: email for individuals, registration/tax ID for businesses | Data model, indexes, duplicate handling |
| Q2 | Permission level for operations? | Separate `view` and `manage` | Authorization dependencies and contract tests |
| Q3 | Deactivation behavior? | Preserve data, block new business, allow reactivation | Lifecycle, FR-005/FR-012/FR-017 |
| Q4 | Concurrent update conflicts? | Reject stale updates with conflict response | Version field, `409` handling |
| Q5 | Minimum contacts/addresses? | None at registration; at least one of each for eligibility | Validation vs eligibility split |

## Open Items

None blocking. Implementation-time choices such as exact Pydantic schema field names and Streamlit layout are deferred to tasks without affecting the plan's architecture.
