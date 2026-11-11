# Implementation Plan: Billing (S05)

**Branch**: `005-billing` | **Date**: 2026-11-10 | **Spec**: specs/005-billing/spec.md

**Input**: Feature specification from `/specs/005-billing/spec.md`

## Summary

Billing feature for S05 enabling invoice generation, payment processing, and billing history tracking for completed orders and shipments.

## Technical Context

**Language/Version**: Python 3.12+ (constitution Section 4)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, SQLite, uv (constitution Sections 4, 7)

**Storage**: SQLite (constitution Section 7)

**Testing**: pytest (constitution Section 10)

**Target Platform**: Linux server (backend API service)

**Project Type**: web-service (FastAPI-based modular monolith)

**Performance Goals**: 200ms for create/list operations (constitution Section 4, research question 1)

**Constraints**: 99.9% uptime (constitution Section 11); JSON logging (Section 11); REST conventions (Section 8)

**Scale/Scope**: 10-100 invoices per month, <500 active invoices with ~10% monthly growth (spec assumptions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gates Status: PASSED**

- **Section 2.1 Modular Monolith**: Billing module has clearly defined responsibility; owns domain logic; no direct repository access by other modules. ✓ No violations.
- **Section 2.2 Domain-Driven Design**: Billing aggregate protects business invariants (valid status transitions, amount calculation). ✓ No violations.
- **Section 2.3 Clean Architecture**: Dependency points inward; billing domain layer does not depend on FastAPI, SQLAlchemy, or database implementations. ✓ No violations.
- **Section 4 Technology Standards**: Performance targets (200ms), reliability (99.9%), structured JSON logging, JSON data formats all aligned with constitution Section 4 technology stack. ✓ No violations.
- **Section 6 Vertical-Slice Delivery**: Billing module progresses through all required layers. ✓ No violations.
- **Section 7 Database and Persistence**: SQLAlchemy 2.x, Alembic for migrations, business logic no SQL, repositories through domain-facing interfaces; data volume assumptions support database design. ✓ No violations.
- **Section 8 API Standards**: REST conventions, /api/v1 versioning, Pydantic validation, consistent HTTP errors, Pagination pending for S05; will follow S02 pattern; no sensitive info exposure; OpenAPI docs. ✓ No violations.
- **Section 9 Security Standards**: Centralized authentication (JWT), enforced authorization, RBAC, users restricted to permissions, secrets not in Git, auditable sensitive ops, input validation at boundaries. ✓ Satisfied (security model clarified in spec assumptions).
- **Section 10 Testing Standards**: Multiple testing levels (unit, application, integration, API), every important business rule has automated tests. ✓ No violations.
- **Section 11 Code Quality**: Python code follows consistent typing conventions; public interfaces have clear documentation; Ruff enforces linting and formatting. ✓ No violations.
- **Section 14 Definition of Done**: All DoD criteria satisfied per updated checklist (16/16 items passing). ✓ No violations.

All constitution gates pass without requiring justification. No violations exist that must be justified.

## Project Structure

### Documentation (this feature)

```text
specs/005-billing/
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
