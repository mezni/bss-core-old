---
description: "Task list template for feature implementation"
---

# Tasks: Dashboard & Reporting (S06)

**Input**: Design documents from `/specs/007-dashboard-reporting/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Python project with FastAPI and dependencies
- [x] T003 [P] Configure linting and formatting tools with Ruff

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Setup database schema and migrations framework with Alembic
- [x] T005 [P] Implement authentication/authorization framework with JWT (RBAC: operator, manager, admin)
- [x] T006 [P] Setup API routing and middleware structure with FastAPI
- [x] T007 Create base models/entities that all stories depend on: Dashboard Metric, Reporting Period
- [x] T008 Configure error handling and logging infrastructure with structured JSON logging
- [x] T009 Setup environment configuration management
- [x] T035 [P] Configure WebSocket support for real-time metric broadcasting (per scope decision)
- [x] T036 [P] Configure background task infrastructure (APScheduler/Celery beat) for 5-minute metric refresh

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Dashboard API (Priority: P1) 🎯 MVP

**Goal**: An authenticated operator can retrieve aggregated operational metrics from the dashboard API, including customer, order, shipment, and billing statistics.

**Independent Test**: Can be fully tested by calling the dashboard API endpoints and verifying the returned metrics match expected values and aggregation rules. The test succeeds even if no other dashboard flows are exercised.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Contract test for GET /api/v1/dashboard/metrics in tests/contract/test_dashboard_metrics.py
- [x] T011 [P] [US1] Integration test for dashboard API metric retrieval user journey in tests/integration/test_dashboard_api.py

### Implementation for User Story 1

- [x] T012 [P] [US1] Create Dashboard Metric model in src/models/dashboard_metric.py
- [x] T013 [P] [US1] Create Reporting Period model in src/models/reporting_period.py
- [x] T014 [US1] Implement Dashboard Metric Service in src/services/dashboard_service.py (depends on T012, T013)
- [x] T015 [US1] Implement dashboard API endpoint GET /api/v1/dashboard/metrics in src/presentation/api/dashboard_endpoints.py
- [x] T016 [US1] Add validation and error handling for FR-001, FR-002, FR-003, FR-006
- [x] T017 [US1] Add logging for dashboard API operations
- [x] T037 [P] [US1] Implement pagination parameters for dashboard metrics GET endpoint

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Billing Metrics (Priority: P2)

**Goal**: An authenticated manager can view billing statistics including invoice counts, payment totals, outstanding balances, and payment success rates.

**Independent Test**: Can be fully tested by calling the billing metrics endpoint and verifying the returned statistics are correct, calculable from existing invoice/payment data. The test passes regardless of subsequent status changes.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T018 [P] [US2] Contract test for GET /api/v1/dashboard/metrics?category=billing in tests/contract/test_dashboard_billing.py
- [x] T019 [P] [US2] Integration test for billing metrics user journey in tests/integration/test_dashboard_billing.py

### Implementation for User Story 2

- [x] T020 [P] [US2] Implement billing metrics filtering in src/services/dashboard_service.py
- [x] T021 [US2] Add role-based metric visibility checks (manager: `user:billing` tier)
- [x] T022 [US2] Integrate with User Story 1 components (dashboard service, metric models)
- [x] T023 [US2] Add outstanding balance calculation logic

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Dashboard UI (Priority: P3)

**Goal**: An authenticated user can access the Streamlit dashboard UI to visualize operational metrics through date-filtered charts and tables.

**Independent Test**: Can be fully tested by loading the Streamlit dashboard, applying date filters, and verifying the displayed metrics are consistent with API responses and correctly filtered by the selected date range. The test validates the boundary rules without requiring the full accounting workflow.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US3] Contract test for dashboard UI endpoint in tests/contract/test_dashboard_ui.py
- [x] T025 [P] [US3] Integration test for dashboard UI user journey in tests/integration/test_dashboard_ui_journey.py

### Implementation for User Story 3

- [x] T026 [P] [US3] Implement dashboard UI in src/frontend/streamlit_dashboard.py
- [x] T027 [US3] Add date range filtering UI widgets (period picker, custom start/end dates)
- [x] T028 [US3] Add role tier display and metric visibility filtering (operator/manager/admin)
- [x] T029 [US3] Integrate with Dashboard API (fetch metrics, apply filters)
- [x] T030 [US3] Add "last updated" timestamp display
- [x] T031 [P] [US3] Add manual refresh button and auto-refresh every 5 minutes

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T032 [P] Documentation updates in docs/ referencing dashboard API and UI contracts
- [x] T033 Code cleanup and refactoring across dashboard service, models, and endpoints
- [x] T034 [P] Performance optimization across all stories (target: sub-500ms API, sub-2s UI load)
- [x] T035 [P] Security hardening: JWT validation, permission checks, input validation (role tiers)
- [x] T036 [P] Run quickstart.md validation all validation scenarios pass
- [x] T037 [P] Additional unit tests in tests/unit/ for dashboard domain logic

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (MVP first)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for GET /api/v1/dashboard/metrics in tests/contract/test_dashboard_metrics.py"
Task: "Integration test for dashboard API metric retrieval user journey in tests/integration/test_dashboard_api.py"

# Launch all models for User Story 1 together:
Task: "Create Dashboard Metric model in src/models/dashboard_metric.py"
Task: "Create Reporting Period model in src/models/reporting_period.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence