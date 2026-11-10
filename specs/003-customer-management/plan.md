# Implementation Plan: Customer Management

**Branch**: `003-customer-management` | **Date**: 2026-11-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-customer-management/spec.md`

## Summary

Implement the Customer Management bounded context as a complete vertical slice: a framework-agnostic domain model for individual and business customers with contacts and addresses, application use cases for registration, retrieval, update, deactivation, reactivation, search, and eligibility checks, SQLAlchemy persistence with Alembic migrations, versioned REST endpoints protected by `view`/`manage` permissions, a Streamlit management UI that talks to the backend over HTTP, and unit/application/integration/contract tests.

The design centralizes customer data so Order, Shipment, and Billing modules consume a stable application-level port instead of duplicating records. Type-specific uniqueness (individual email, business registration/tax ID), soft deactivation with reactivation, eligibility gating (active + at least one contact + at least one address), and optimistic concurrency control are the core business rules.

## Technical Context

**Language/Version**: Python 3.12+ (constitution Section 4)

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, pytest, Ruff, uv; Streamlit and an HTTP client for the frontend UI (constitution Sections 3-4). Authentication/permission primitives are consumed from the Identity & Access module delivered in S01.

**Storage**: SQLite via SQLAlchemy 2.x, schema managed by Alembic (constitution Section 7). Tables: `customers`, `customer_contacts`, `customer_addresses`. Designed for later PostgreSQL migration.

**Testing**: pytest across unit (domain rules), application (use cases with in-memory fakes), integration (repository + SQLite + migrations), and contract (HTTP endpoints) levels (constitution Section 10).

**Target Platform**: Linux development environment; single-deployment modular monolith.

**Project Type**: Modular monolith with two independent applications — FastAPI backend and Streamlit frontend communicating only over HTTP (constitution Sections 2-3).

**Performance Goals**: Customer search/filter over 10,000 records returns within 30 seconds (SC-003); list/search endpoints target p95 under 500 ms at that scale; single-customer create/read/update operations complete well under 2 seconds.

**Constraints**: No business logic in the frontend; backend enforces authorization; domain layer independent of FastAPI/SQLAlchemy/Streamlit; modules access customer data only through the application port; no hard deletes; type-specific uniqueness; optimistic concurrency; consistent error format; versioned endpoints under `/api/v1` (constitution Sections 2-9).

**Scale/Scope**: One organization, single deployment, 10,000+ customer records, up to 5+ contacts and 5+ addresses per customer (SC-005). S02 scope only; downstream order/shipment/billing integration is delivered in later sprints against the port defined here.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gate Status**: PASSED

| Constitution Requirement | Plan Compliance |
|---|---|
| 2.1 Modular monolith; no cross-module repository access | Customer module owns its repositories; other modules use an application port |
| 2.2 DDD: entities protect invariants, value objects validate | `Customer` aggregate enforces eligibility, uniqueness, and lifecycle rules; `CustomerType`, `Email`, `RegistrationNumber` value objects |
| 2.3 Clean Architecture; inward dependencies | Domain has no framework imports; application depends on domain ports; infrastructure implements ports; presentation depends inward |
| 3 Two applications; frontend via HTTP only | Streamlit UI uses an API client; no DB or business logic in frontend |
| 4 Technology standards | Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, pytest, Ruff, uv |
| 5 Module standards | Domain, application, persistence, API, tests, UI, and documented rules all included |
| 6 Vertical-slice delivery | Plan covers domain → application → infrastructure → API → UI → tests → docs |
| 7 Database and persistence | Alembic migration; repositories in infrastructure; explicit transaction boundaries; referential integrity via FKs |
| 8 API standards | REST under `/api/v1`, Pydantic validation, consistent errors, pagination, no sensitive leakage |
| 9 Security standards | Backend-enforced `view`/`manage` permissions; no PII in logs; audit-worthy lifecycle logging |
| 10 Testing standards | Unit, application, integration, and contract tests; business rules covered |
| 11 Code quality | Typed interfaces, focused responsibilities, Ruff enforcement |
| 13-14 Documentation and DoD | Plan, research, data model, contracts, quickstart, and task traceability |

**Violations**: None. No complexity exemptions are required.

**Post-Design Re-check (after Phase 1)**: PASSED. The data model, contracts, and quickstart keep the domain framework-free, enforce type-specific uniqueness and eligibility in the domain, expose only DTOs across module boundaries, and enforce authorization at the API boundary.

## Project Structure

### Documentation (this feature)

```text
specs/003-customer-management/
├── plan.md              # This file
├── research.md          # Phase 0 decisions
├── data-model.md        # Phase 1 entities, rules, transitions
├── quickstart.md        # Phase 1 validation guide
├── contracts/
│   ├── customer-api.md            # REST contract for the customer API
│   └── customer-eligibility-port.md # Cross-module application port
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── customer_management/
│       ├── domain/
│       │   ├── entities.py          # Customer aggregate, Contact, Address
│       │   ├── value_objects.py     # CustomerType, Email, RegistrationNumber, Status
│       │   ├── exceptions.py        # Domain errors (duplicate, ineligible, stale)
│       │   └── repositories.py      # CustomerRepository port
│       ├── application/
│       │   ├── commands.py          # Create/Update/Deactivate/Reactivate + contact/address ops
│       │   ├── queries.py           # Get/Search/Eligibility
│       │   ├── use_cases.py         # Command/query handlers
│       │   ├── dto.py               # Application DTOs
│       │   └── ports.py             # CustomerEligibilityPort for other modules
│       ├── infrastructure/
│       │   ├── orm.py               # SQLAlchemy models
│       │   └── repository.py        # CustomerRepository implementation
│       ├── api/                     # Presentation layer (HTTP)
│       │   ├── router.py            # /api/v1/customers routes
│       │   ├── schemas.py           # Pydantic request/response models
│       │   └── dependencies.py      # view/manage permission dependencies
│       └── presentation/
│           └── __init__.py          # Reserved for UI-facing helpers (unused in S02)
├── frontend/
│   ├── app.py                       # Navigation entry point
│   └── customer/
│       ├── api_client.py            # HTTP client for customer endpoints
│       ├── list_page.py             # List, search, filter, deactivate/reactivate
│       └── form_page.py             # Create/edit customer, contacts, addresses
├── api/
│   └── health.py                    # Existing FastAPI app; register customer router
└── domain/
    └── database.py                  # Existing engine/session; add Base metadata wiring

migrations/
└── versions/
    └── <rev>_create_customer_tables.py

tests/
├── unit/
│   └── customer_management/
│       ├── test_customer_entity.py
│       └── test_value_objects.py
├── application/
│   └── customer_management/
│       └── test_use_cases.py
├── integration/
│   └── customer_management/
│       └── test_customer_repository.py
└── contract/
    └── customer_management/
        └── test_customer_api.py
```

**Structure Decision**: Reuse the existing modular-monolith layout under `src/models/customer_management/` with the four Clean Architecture layers plus a `presentation` placeholder for UI-facing helpers. The FastAPI app in `src/api/health.py` gains the customer router; the Streamlit app in `src/frontend/` gains a `customer/` page package. Tests follow the existing `tests/{unit,integration,contract}` convention, with an added `tests/application/` tier for use-case tests.

## Complexity Tracking

No constitutional violations. The repository pattern and application port are required by constitution Sections 2.1, 2.3, and 7, not optional complexity.
