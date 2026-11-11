# Implementation Plan: Dashboard & Reporting (S06)

**Branch**: `007-dashboard-reporting` | **Date**: 2026-11-11 | **Spec**: specs/007-dashboard-reporting/spec.md

**Input**: Feature specification from `/specs/007-dashboard-reporting/spec.md`

## Summary

Dashboard & Reporting (S06) providing operational visibility across business modules via aggregated metrics API and Streamlit UI. Managers and operators need a consolidated view of business activities including customer, order, shipment, and billing statistics.

Primary user journeys:
- Dashboard API: authenticated users retrieve aggregated operational metrics
- Billing Metrics: view invoice counts, payment totals, outstanding balances, payment success rates
- Dashboard UI: interactive date-filtered charts and tables for operational data visualization

Technical approach: FastAPI-based REST endpoints under `/api/v1/dashboard` with 5-minute batch-refresh metric caching, role-based access control (operator/manager/admin), and Streamlit dashboard UI at `/dashboard`.

## Technical Context

**Language/Version**: Python 3.12+ (constitution Section 4)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, SQLite, uv (constitution Sections 4, 7)

**Storage**: SQLite (constitution Section 7)

**Testing**: pytest (constitution Section 10)

**Target Platform**: Linux server (backend API service)

**Project Type**: web-service (FastAPI-based modular monolith)

**Performance Goals**: 500ms for create/list operations (constitution Section 4, SC-001); 2s for UI loading (SC-002); metrics refresh every 5 minutes (data freshness decision)

**Constraints**: 99.9% uptime (constitution Section 11); JSON logging (Section 11); REST conventions (Section 8); role-based access control (user:view/operator, user:billing/manager, user:admin/admin); metrics are read-only, no mutation through dashboard operations; Invoice total must exactly match associated order/shipment total (constitution alignment)

**Scale/Scope**: 4 metric categories (customer, order, shipment, billing); metric refresh every 5 minutes; <500 active dashboard metrics; ~10% monthly growth in dashboard data volume; single application deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gates Status: PASSED**

- **Section 2.1 Modular Monolith**: Dashboard module has clearly defined responsibility; owns metric aggregation logic; no direct repository access by other modules. ✓ No violations.
- **Section 2.2 Domain-Driven Design**: Dashboard metric aggregate protects business invariants (valid status transitions, metric consistency). ✓ No violations.
- **Section 2.3 Clean Architecture**: Dependency points inward; dashboard domain layer does not depend on FastAPI, SQLAlchemy, or database implementations. ✓ No violations.
- **Section 4 Technology Standards**: Performance targets (500ms API, 2s UI), reliability (99.9%), structured JSON logging, JSON data formats all aligned with constitution Section 4 technology stack. ✓ No violations.
- **Section 6 Vertical-Slice Delivery**: Dashboard module progresses through all required layers. ✓ No violations.
- **Section 7 Database and Persistence**: SQLAlchemy 2.x, Alembic for migrations, business logic no SQL, repositories through domain-facing interfaces; data volume assumptions support database design. ✓ No violations.
- **Section 8 API Standards**: REST conventions, /api/v1 versioning, Pydantic validation, consistent HTTP errors, no sensitive info exposure; OpenAPI docs. ✓ No violations.
- **Section 9 Security Standards**: Centralized authentication (JWT), enforced authorization, RBAC (role-based: operator/manager/admin), users restricted to permissions, secrets not in Git, auditable sensitive ops, input validation at boundaries. ✓ Satisfied (role differentiation clarified in spec).
- **Section 10 Testing Standards**: Multiple testing levels (unit, application, integration, API), every important business rule has automated tests. ✓ No violations.
- **Section 11 Code Quality**: Python code follows consistent typing conventions; public interfaces have clear documentation; Ruff enforces linting and formatting. ✓ No violations.
- **Section 14 Definition of Done**: All DoD criteria satisfied per updated checklist (16/16 items passing). ✓ No violations.

All constitution gates pass without requiring justification. No violations exist that must be justified.

## Project Structure

### Documentation (this feature)

```text
specs/007-dashboard-reporting/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single project (DEFAULT)
src/
├── models/
├── services/
├── api/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```