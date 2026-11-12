# Implementation Plan: Integration & MVP Release (S07)

**Branch**: `008-integration-mvp` | **Date**: 2026-11-11 | **Spec**: specs/008-integration-mvp/spec.md

**Input**: Feature specification from `/specs/008-integration-mvp/spec.md`

## Summary

Integration & MVP Release (S07) validates the complete business lifecycle across all modules through four end-to-end workflows (customer-to-order, order-to-shipment, order-to-invoice, invoice-to-payment), with cross-module role-based authorization (`user:view` / `user:billing` / `user:admin`), deterministic interconnected synthetic data generation, standardized API error responses, operational logging, clean-database migrations, and cross-module integration tests.

Primary user journeys:
- End-to-end customer-to-order workflow (order created from customer and items, status draft→confirmed)
- End-to-end order-to-shipment workflow (shipment with tracking number, order status→shipped)
- End-to-end order-to-invoice workflow (invoice with matching totals, status pending)
- End-to-end invoice-to-payment workflow (payment recorded, invoice status→paid)
- Cross-module authorization review (role-restricted workflow access)

Technical approach: consolidate the runtime onto a single FastAPI application (the existing `src/api/health.py` composition root) with a single SQLAlchemy engine and a single Alembic environment; complete prerequisite module functionality (shipment per `specs/005-shipment-management`, billing per `specs/006-billing`, identity permission dependencies per `specs/002-user-auth`); wire cross-module interactions through application-level ports (following the `CustomerEligibilityPort` precedent); standardize the API error envelope to the clarified format (`{"error", "message", "code"}`); add a Faker-based deterministic data generator under `src/devtools/datagen` (console script `bss-datagen`) that composes module application services; validate the four workflows with new `tests/integration/e2e` journey tests.

MVP sign-off gates (per spec clarification): SC-001 (all four workflows pass from a clean database), SC-007 (migrations succeed from a clean database), and security review confirmation (no critical authorization defects). All other success criteria are quality targets that do not block sign-off.

## Technical Context

**Language/Version**: Python 3.12+ (constitution Section 4)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, PyJWT, Argon2id, Streamlit, Faker, httpx, uv, pytest, Ruff (constitution Sections 4, 7)

**Storage**: SQLite, single canonical database via `src/domain/database.py` (`BSS_DATABASE_URL`, default `sqlite:///./db/bss_core.db`) (constitution Section 7)

**Testing**: pytest with four levels — unit, application, integration (incl. new `tests/integration/e2e`), contract (constitution Section 10)

**Target Platform**: Linux server (FastAPI backend) + browser (Streamlit frontend)

**Project Type**: web-service (FastAPI modular monolith) + web-app (Streamlit frontend over HTTP APIs)

**Performance Goals**: 500ms for API operations (quality target, not a sign-off gate); workflows complete reliably end-to-end; performance review is baseline measurement only (S07-07, Should priority)

**Constraints**: MVP sign-off gates are SC-001, SC-007, and security review (spec clarification); standardized error envelope `{"error": "<type>", "message": "<human-readable>", "code": "<error-code>"}` on HTTP 400/401/403/404/500 (FR-007, clarification); role-restricted workflow access (`user:view` → customer-to-order; `user:billing` → order-to-invoice, invoice-to-payment; `user:admin` → all four) (FR-005, clarification); synthetic data enforces FK chains at generation time (clarification); real-time WebSocket updates, performance optimization, non-SQLite migration, auth method changes, and module-specific metrics are out of scope (clarification)

**Scale/Scope**: 4 end-to-end workflows across 6 modules (identity, customer, order, shipment, billing, dashboard); synthetic data volumes configurable per module (default ~50 customers, ~100 orders, proportional shipments/invoices/payments); single application deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gates Status: PASSED (no violations introduced; existing codebase inconsistencies are remediated by this feature)**

- **Section 2.1 Modular Monolith**: Cross-module workflow interactions use explicit application interfaces/ports (order→shipment status update, order→invoice linking, customer eligibility for orders) — never direct repository access across modules. ✓ The plan follows the existing `CustomerEligibilityPort` precedent.
- **Section 2.2 Domain-Driven Design**: Each module's aggregates protect their invariants (order status transitions, invoice pending→paid terminal state, no duplicate invoice per order). Domain events are not required for MVP; workflow state is derived from module records. ✓ No violations.
- **Section 2.3 Clean Architecture**: Dependency direction points inward; new integration/validation code (data generator, e2e tests) consumes application services and never bypasses layers. ✓ No violations.
- **Section 3 Application Separation**: FastAPI owns business operations and authorization; Streamlit communicates via HTTP only. Workflow validation happens at the API level. ✓ No violations.
- **Section 4 Technology Standards**: Python 3.12+, uv, FastAPI, SQLAlchemy 2.x, SQLite, Alembic, Pydantic, Streamlit, JWT, Argon2id, pytest, Ruff — and **Faker** for test data (explicitly listed in constitution Section 4 and required by Section 12). No new dependencies beyond Faker (already sanctioned). ✓ No violations.
- **Section 5 Business Module Standards**: Shipment and billing modules are completed per their existing specifications (`specs/005`, `specs/006`) as prerequisite work; each module keeps domain/application/infrastructure/api layers. ✓ No violations.
- **Section 6 Vertical-Slice Delivery**: Prerequisite modules progress through all required layers per their specs; the integration feature itself is validated through complete vertical workflows (API → application → domain → persistence). ✓ No violations.
- **Section 7 Database and Persistence**: **Remediation** — the codebase currently has two parallel Alembic environments and two database engines; this plan consolidates to a single Alembic environment (`migrations/`, covering all module metadata) and a single engine (`src/domain/database.py`). Migrations version-controlled; referential integrity enforced; explicit transactions. ✓ Plan remediates existing inconsistency.
- **Section 8 API Standards**: **Remediation** — consolidate the two parallel FastAPI apps into one composition root (`src/api/health.py:app`), mounting all module routers including dashboard; REST conventions, `/api/v1` versioning, Pydantic validation, pagination, no sensitive info exposure, OpenAPI docs. ✓ Plan remediates existing inconsistency.
- **Section 9 Security Standards**: **Remediation** — the codebase has three parallel auth implementations (PyJWT permissions-claim, jose user lookup, base64 stub); this plan centralizes on the working PyJWT permission-claim pattern, promoted into the identity module's API dependencies (`user:view`, `user:billing`, `user:admin`), enforced by the backend on all workflow entry points. Authorization review (S07-05) verifies no critical defects remain — a sign-off gate. ✓ Plan remediates existing inconsistency.
- **Section 10 Testing Standards**: New cross-module e2e tests (workflow journeys), contract tests (error format, role enforcement), plus existing unit/application/integration levels. Every important business rule (FK chains, status transitions, role mapping) has automated tests. ✓ No violations.
- **Section 11 Code Quality**: Ruff linting/formatting, consistent typing, explicit error handling, structured JSON logging without secrets. ✓ No violations.
- **Section 12 Data Generation**: **Deliverable** — the dedicated data generator (`bss-datagen`) does not exist today; this feature delivers it: realistic data via Faker, related records across modules, FK relationships respected, deterministic seeds, configurable volumes, no production credentials. Uses application-supported persistence (module application services) without business logic duplication. ✓ Feature satisfies this section.
- **Section 13 Documentation Standards**: Documentation review (S07-12) updates all technical documents to match implementation, including the error format deviation from `docs/api-design.md` RFC 9457 (clarified format chosen; deviation recorded). ✓ No violations.
- **Section 14 Definition of Done**: Sign-off gates (SC-001, SC-007, security review) align with DoD; spec checklist 16/16 passing. ✓ No violations.
- **Section 15 Governance**: Error format deviates from `docs/api-design.md` (RFC 9457) per explicit spec clarification — deviation documented in `research.md` and reflected in updated docs. ✓ Governed deviation.

All constitution gates pass. No violations require the Complexity Tracking table. Existing codebase inconsistencies (parallel apps/engines/auth/alembic environments) are remediated by this feature rather than introduced by it.

## Project Structure

### Documentation (this feature)

```text
specs/008-integration-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── end_to_end_workflow_contracts.md
│   ├── error_response_contract.md
│   ├── authorization_contract.md
│   └── data_generator_contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── health.py                    # Composition root: single FastAPI app; mounts all module
│                                   # routers (customer, order, shipment, billing, dashboard);
│                                   # registers centralized error handlers + logging middleware
├── models/                          # Business modules (canonical pattern: 002/003 reference)
│   ├── identity_access/             # COMPLETE (prerequisite, per specs/002):
│   │   └── api/                     #   shared permission dependencies: get_permissions(),
│   │       ├── dependencies.py      #   require_user_view / require_user_billing /
│   │       └── permissions.py       #   require_user_admin (user:view, user:billing, user:admin)
│   ├── customer_management/         # existing (S02) — error envelope migrated to standard format
│   ├── order_management/            # existing (S03)
│   ├── shipment_management/         # COMPLETE (prerequisite, per specs/005):
│   │   ├── domain/                  #   shipment entity, tracking number, status transitions
│   │   ├── application/             #   create-shipment use case (updates order via port)
│   │   ├── infrastructure/         #   repository + ORM
│   │   └── api/                     #   /api/v1/shipments router
│   └── billing_management/          # COMPLETE (prerequisite, per specs/006):
│       ├── domain/                  #   invoice (INV- numbering, pending→paid), payment entities
│       ├── application/             #   invoice generation (order port), payment processing
│       ├── infrastructure/         #   repository + ORM
│       └── api/                     #   /api/v1/invoices, /api/v1/payments routers
├── devtools/
│   └── datagen/                     # NEW: synthetic data generator (constitution Section 12)
│       ├── __init__.py
│       ├── generator.py             # composes module application services; FK chains; seeds
│       ├── cli.py                   # bss-datagen console script (click/argparse)
│       └── manifest.py              # generation manifest (seed, volumes, counts) — Synthetic
│                                   #   Data Set entity
├── services/
│   └── dashboard_service.py         # existing (S06)
├── frontend/                         # Streamlit app (existing); workflow smoke pages optional
└── infrastructure/
    └── logging.py                   # extended: structured JSON workflow logging
                                    #   (start/completion/failure events, correlation id)

tests/
├── unit/                            # existing + datagen unit tests
├── application/                     # existing + workflow use-case tests
├── integration/
│   ├── e2e/                         # NEW: four end-to-end workflow journey tests
│   │   ├── test_customer_to_order.py
│   │   ├── test_order_to_shipment.py
│   │   ├── test_order_to_invoice.py
│   │   ├── test_invoice_to_payment.py
│   │   └── test_clean_database_migrations.py   # SC-007 gate
│   └── ...                          # existing integration tests
└── contract/
    ├── integration/                 # NEW: error format contract + role enforcement contract
    │   ├── test_error_format_contract.py
    │   └── test_workflow_authorization_contract.py
    └── ...                          # existing contract tests

migrations/                          # single canonical Alembic environment
├── env.py                           # imports ALL module ORM metadata (consolidated)
└── versions/                        # version-controlled migrations for all modules
```

**Structure Decision**: Existing single-project layout (`src/` + `tests/`) per repository convention (options 1). The canonical module pattern is `src/models/<module>/{domain,application,infrastructure,api}` with `customer_management` as reference implementation. New additions: `src/devtools/datagen` (development tooling sanctioned by constitution Section 12), `tests/integration/e2e`, and `tests/contract/integration`. Legacy parallel structures (`infrastructure/alembic/`, `src/infrastructure/db/config.py` engine, `src/presentation/api/dashboard_endpoints.py` standalone app, root `test.db`) are retired/consolidated during this feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations introduced by this plan. The one governed deviation — error envelope format (`{"error", "message", "code"}`) differing from `docs/api-design.md` RFC 9457 Problem Details — was explicitly chosen in the spec clarification session, is simpler and directly testable, and will be reflected in updated documentation per constitution Section 15 governance (recorded in `research.md`).
