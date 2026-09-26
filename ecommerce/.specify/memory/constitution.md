<!--
Sync Impact Report — Constitution Update

Version change: (placeholder scaffold, no real version) -> 1.1.0
Bump rationale: MINOR. v1.0.0 replaced all template placeholders with the Fake
E-Commerce Server governance baseline. v1.1.0 materially expands the Spec Kit
development-process guidance by mandating that all Speckit-generated artifacts
live under `specs/` and by enumerating the feature roadmap layout.

Modified principles:
  - [PRINCIPLE_1_NAME]   (template placeholder) -> I. Domain Independence
  - [PRINCIPLE_2_NAME]   (template placeholder) -> II. Determinism and Reproducibility
  - [PRINCIPLE_3_NAME]   (template placeholder) -> III. Explicit Business Rules
  - [PRINCIPLE_4_NAME]   (template placeholder) -> IV. Testability and Isolation
  - [PRINCIPLE_5_NAME]   (template placeholder) -> V. Simple Local Development

Added sections:
  - Speckit Development Process (new; governs `specs/` layout and lifecycle)
  - Technology Stack and API Design (was [SECTION_2_NAME]/[SECTION_2_CONTENT])
  - Development Workflow (was [SECTION_3_NAME]/[SECTION_3_CONTENT])
  - Project Documentation Layout (new; governs README/CHANGELOG/docs/)

Removed sections:
  - [SECTION_2_NAME], [SECTION_3_NAME], [GOVERNANCE_RULES] placeholders resolved
    to concrete, non-placeholder sections.

Deferred items / follow-up TODOs:
  - None. RATIFICATION_DATE set to 2026-09-25 (this is the first substantive
    ratification; the prior file contained only unresolved template tokens).
  - The 11 feature directories under `specs/` are tracked as empty scaffolding;
    their `spec.md` content is produced by `/speckit.specify` and is NOT
    pre-authored by this constitution update.
-->

# Fake E-Commerce Server Constitution

## Core Principles

### I. Domain Independence
The domain layer MUST remain free of framework dependencies. Entities, value
objects, business rules, state transitions, and domain exceptions MUST NOT
import or depend on FastAPI, SQLAlchemy, HTTPX, Alembic, or any other
infrastructure or framework library. Dependencies MUST point inward: API ->
Application -> Domain <- Infrastructure. The domain MUST be unit-testable
without a database, HTTP client, or event loop.

Rationale: A deterministic, portable domain core is what makes the fake server
a trustworthy test target; framework coupling would leak into every downstream
feature spec.

### II. Determinism and Reproducibility
The system MUST behave deterministically given the same inputs. Specifically:

- The fake-data generator MUST derive all randomness from an explicit,
  configurable, seedable random-number generator (`--seed`).
- The same seed, generator configuration, and application version MUST produce
  equivalent generated data.
- Automated tests MUST NOT depend on uncontrolled randomness.
- Failure simulation MUST offer deterministic, explicitly requested scenarios
  (e.g. `X-Fake-Failure: payment_declined`); randomized failure injection MAY
  exist for resilience testing but MUST be independently controllable and MUST
  default to off.

Rationale: Determinism is the difference between a reproducible bug report and
a mystery. This principle is what makes Principle IV achievable.

### III. Explicit Business Rules
Business invariants MUST be enforced by domain and application logic, not
relying exclusively on database constraints. The system MUST model, at minimum:

- Inventory: quantity MUST NOT become negative; reservation MUST fail when stock
  is insufficient; release MUST NOT create invalid quantities.
- Cart: items MUST reference existing products; quantities MUST be positive;
  totals MUST be derived from valid product pricing.
- Orders: MUST contain at least one item; totals MUST be calculated from order
  items; lifecycle MUST be explicit; invalid state transitions MUST be rejected.
- Payments: MUST reference an order; state transitions MUST be explicit; a
  failed payment MUST NOT silently become successful.

Business state transitions MUST be explicit and modeled as such, not inferred
from ad-hoc status writes.

Rationale: Explicit rules are the specification the tests assert against; they
are the contract the API and generator both depend on.

### IV. Testability and Isolation
Testing is mandatory and MUST be isolated. The test suite MUST be organized as:

```text
tests/
├── unit/
├── integration/
└── api/
```

- Unit tests SHOULD cover domain rules, state transitions, calculations, and
  validation, and SHOULD avoid the database where practical.
- Integration tests MUST cover repositories, SQLite persistence, transactions,
  and database relationships.
- API tests MUST cover HTTP status codes, request validation, response schemas,
  error responses, major workflows, and failure scenarios.
- Tests MUST NOT depend on execution order and MUST use a dedicated SQLite test
  database; automated tests MUST NOT modify development data.

Every significant business rule SHOULD have automated coverage.

Rationale: The whole point of the project is to be exercised by tests and
clients; untestable code cannot serve either.

### V. Simple Local Development
The project MUST remain realistic without unnecessary complexity. Prefer:

```text
Simple over clever
Explicit over implicit
Tested over over-engineered
```

- The system MUST remain a modular monolith. It MUST NOT introduce microservices,
  message brokers, distributed systems, event sourcing, or CQRS without a
  concrete, documented requirement.
- A developer MUST be able to go from a clean checkout to a working populated
  server with a small number of commands (install -> migrate -> seed -> run).
- The fake-data generator MUST be part of the standard developer workflow; a new
  developer MUST NOT need to manually insert rows to get a useful environment.
- New abstractions MUST have a demonstrated purpose.

Rationale: Complexity that does not increase realism, determinism, testability,
or usefulness SHOULD be questioned before it is introduced.

## Technology Stack and API Design

The project MUST use the following technology baseline, and MUST NOT introduce a
second framework where this stack can reasonably meet the need:

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- SQLite (default; dev database at `data/ecommerce.db`)
- pytest, HTTPX
- uv (dependency management; `uv.lock` MUST be committed)

Each dependency MUST have a clear technical purpose.

API design requirements:

- All public routes MUST be versioned under `/api/v1/`.
- The API MUST follow HTTP semantics and use appropriate status codes
  (200, 201, 204, 400, 401, 403, 404, 409, 422, 500).
- API request/response models MUST use explicit Pydantic schemas; database
  models MUST NOT automatically become public API schemas.
- Pydantic v2 MUST perform validation at API boundaries, but business rules
  MUST NOT live entirely inside Pydantic schemas.
- Client-calculated totals MUST NOT be trusted; the server recomputes them.

## Database and Data Management

- SQLite MUST be the default database; the dev database SHOULD live at
  `data/ecommerce.db`.
- The schema MUST be managed through Alembic migrations. The application MUST NOT
  rely on `Base.metadata.create_all()` as its primary schema mechanism.
- All persistent schema changes MUST be represented by an Alembic migration.
- Repositories SHOULD isolate persistence concerns from application services.
- SQLite-specific behavior that affects application behavior MUST be documented
  in `docs/database.md`.

## Development Workflow

Development MUST proceed incrementally through specifications. The lifecycle is:

```text
Specification -> Design -> Implementation Plan -> Implementation
              -> Tests -> Validation -> Documentation
```

- Each significant feature SHOULD have a corresponding specification under
  `specs/`.
- Implementation MUST NOT introduce substantial undocumented functionality.
- A feature is complete only when behavior is specified, business rules are
  documented, implementation is complete, tests exist, API contracts are
  validated, migrations exist where required, error behavior is defined, and
  documentation is updated. An endpoint returning `200 OK` is NOT sufficient
  evidence of completion.

## Speckit Development Process

All Speckit-generated feature artifacts — and the feature directories
themselves — MUST live under the top-level `specs/` directory. This is the
single canonical location for specifications; feature directories MUST NOT be
scattered under `docs/`, the repository root, or elsewhere.

```text
specs/
├── 001-foundation/
├── 002-product-catalog/
├── 003-customers/
├── 004-cart/
├── 005-orders/
├── 006-inventory/
├── 007-payments/
├── 008-fake-data-generator/
├── 009-failure-simulation/
├── 010-authentication/
└── 011-observability/
```

Rules:

- Each feature MUST be independently implementable and numbered sequentially
  (`NNN-slug/`).
- The active feature directory MUST be recorded in `.specify/feature.json`
  (`feature_directory`) and/or driven by the Speckit tooling, which resolves
  `SPECS_DIR` to the repository `specs/` directory.
- Specifications MUST describe observable behavior before implementation
  details.
- `008-fake-data-generator` is a first-class, high-priority feature: the fake-data
  generator is a project capability in its own right, not an afterthought of
  other features.
- The generator MUST be executable independently of the FastAPI server
  (`uv run python -m ecommerce.seed`) and MUST NOT require the HTTP server to be
  running.
- After each feature spec is produced, the constitution MUST be checked for
  conflicts; conflicts MUST be explicitly identified rather than silently
  resolved.

## Project Documentation Layout

The repository MUST maintain the following documentation set, and MUST update it
whenever behavior changes materially:

```text
README.md          # Entry point: purpose, features, stack, install/run/migrate/seed/test
CHANGELOG.md       # Versioned history of notable changes
docs/
├── PRD.md                  # What the system does and why (requirements, not implementation)
├── architecture.md         # Layering, bounded contexts, modules, repository pattern, transactions
├── API.md                  # HTTP contract: endpoints, schemas, status codes, errors, auth
├── database.md             # SQLite model: tables, relationships, constraints, indexes, migrations
├── generator.md            # Fake-data generator: entities, CLI, seed, profiles, reset, validation
├── configuration.md        # Environment variables and per-environment behavior
├── testing.md              # Test layout, fixtures, generator use, deterministic & failure tests
├── failure-simulation.md   # Deterministic failure scenarios and how they are triggered
└── development.md          # Developer workflow and commands
```

`.env.example` MUST document configuration without containing real secrets, and
the repository MUST contain `.gitignore` and `README.md`. Real secrets, real
credentials, temporary files, and build artifacts MUST NOT be committed.

## Security and Observability

- The system MUST validate input, prevent SQL injection, avoid sensitive-data
  leakage, and never log secrets.
- Authentication and authorization boundaries MUST be realistic and MUST remain
  separate from business logic; roles (e.g. `customer`, `admin`, `service`) MUST
  be introduced only where they add meaningful functionality.
- The server MUST NOT process real payment credentials; all payment data MUST be
  synthetic.
- The application MUST provide useful logging including request ID, HTTP method,
  path, status code, duration, important domain events, and errors, without
  logging sensitive information.
- The server MUST expose `GET /health`. A readiness endpoint MAY be added later.
- Errors MUST distinguish domain, application, infrastructure, and HTTP errors.
  Internal exceptions MUST NOT be exposed directly; API errors MUST use a
  consistent structure with stable codes, e.g.:

```json
{
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Insufficient inventory for product"
  }
}
```

- Configuration MUST be externalized via environment variables (e.g.
  `DATABASE_URL`, `APP_ENV`, `LOG_LEVEL`, `FAKE_FAILURE_RATE`, `FAKE_LATENCY_MS`,
  `RANDOM_SEED`). Secrets MUST NOT be committed.

## Governance

This constitution is the highest-level engineering standard for the project. When
an implementation conflicts with the constitution, the conflict MUST be
explicitly identified rather than silently ignored.

Amendment procedure:

1. Changes to this constitution MUST be intentional, documented, and must explain
   the reason.
2. Each amendment MUST identify the affected project areas and MUST update the
   relevant specifications and documentation.
3. The constitution MUST evolve when project requirements or architectural
   constraints genuinely change.

Versioning policy (semantic versioning of the constitution itself):

- MAJOR: backward-incompatible governance/principle removals or redefinitions.
- MINOR: a new principle/section is added, or existing guidance is materially
  expanded.
- PATCH: clarifications, wording, typo fixes, and other non-semantic refinements.

Compliance expectations:

- Every pull request / review MUST verify compliance with this constitution.
- Complexity MUST be justified before it is introduced; if it does not make the
  system more realistic, deterministic, testable, maintainable, or useful, it
  SHOULD be questioned.
- A feature that cannot be reconciled with the constitution MUST either be
  amended here first or explicitly flagged as a deferred conflict.

Guiding principle: the Fake E-Commerce Server exists to provide a realistic but
controlled environment for building, testing, and learning backend systems. Every
significant decision SHOULD be able to answer "does this make the system more
realistic, deterministic, testable, maintainable, or useful?" If not, the added
complexity SHOULD be questioned before it is introduced.

**Version**: 1.1.0 | **Ratified**: 2026-09-25 | **Last Amended**: 2026-09-25
