# Tasks: Customer Management (S02)

**Input**: Design documents from `/specs/003-customer-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required. S02-13 and the spec acceptance criteria require customer tests, and constitution Section 10 mandates unit, application, integration, and contract coverage.

**Organization**: Tasks are grouped by user story so each can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: `US1`–`US5`, mapped to the spec user stories
- Every task includes an exact file path

## Path Conventions

Single project at the repository root: `src/` and `tests/`. The customer module lives under `src/models/customer_management/`; the frontend under `src/frontend/`; migrations under `migrations/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Declare missing dependencies and create the package/test skeleton.

- [x] T001 Add `streamlit` and `httpx` (frontend HTTP client) to `pyproject.toml` and run `uv sync`
- [x] T002 [P] Create customer module packages with `__init__.py` under `src/models/customer_management/{domain,application,infrastructure,api,presentation}/`
- [x] T003 [P] Create frontend package `src/frontend/customer/__init__.py`
- [x] T004 [P] Create test packages with `__init__.py` under `tests/{unit,application,integration,contract}/customer_management/`
- [x] T005 Configure pytest test paths and Ruff per-file ignores for the new tiers in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain primitives, schema, error handling, and authorization that every story needs.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 [P] Create enums and value objects (`CustomerType`, `CustomerStatus`, `ContactType`, `Email`, `RegistrationNumber`) in `src/models/customer_management/domain/value_objects.py`
- [x] T007 [P] Create domain exceptions (`CustomerNotFound`, `DuplicateCustomer`, `StaleUpdate`, `InvalidCustomer`, `DuplicatePrimary`) in `src/models/customer_management/domain/exceptions.py`
- [x] T008 Create the `CustomerRepository` port interface in `src/models/customer_management/domain/repositories.py` (depends on T006, T007)
- [x] T009 Create the SQLAlchemy declarative `Base` and ORM models for `Customer`, `Contact`, and `Address` in `src/models/customer_management/infrastructure/orm.py` (depends on T006)
- [x] T010 Wire `target_metadata` in `migrations/env.py` and create one Alembic revision for all three tables, FKs, and partial unique indexes in `migrations/versions/` (depends on T009)
- [x] T011 [P] Implement the shared error envelope and exception handlers in `src/models/customer_management/api/errors.py` (depends on T007)
- [x] T012 [P] Implement `require_customer_view` and `require_customer_manage` dependencies in `src/models/customer_management/api/dependencies.py`
- [x] T013 [P] Create test fixtures: in-memory fake repository in `tests/application/customer_management/fakes.py`, temp-SQLite fixture in `tests/integration/customer_management/conftest.py`, and API client fixture in `tests/contract/customer_management/conftest.py` (depends on T008)
- [x] T014 Register the customer router and error handlers on the FastAPI app in `src/api/health.py` and create the router skeleton in `src/models/customer_management/api/router.py` (depends on T011, T012)

**Checkpoint**: Foundation ready — user stories can proceed in parallel.

---

## Phase 3: User Story 1 — Register and Maintain Customers (Priority: P1) 🎯 MVP

**Goal**: Create, retrieve, update, deactivate, and reactivate customers with optimistic concurrency.

**Independent Test**: Register a customer, retrieve it, update a field, deactivate it, then reactivate it; confirm each state change and version increment is observable.

### Tests for User Story 1

- [x] T015 [P] [US1] Unit tests for customer lifecycle invariants in `tests/unit/customer_management/test_customer_entity.py`
- [x] T016 [P] [US1] Application tests for create/get/update/deactivate/reactivate use cases in `tests/application/customer_management/test_customer_lifecycle.py`
- [x] T017 [P] [US1] Integration tests for repository persistence and stale-version rejection in `tests/integration/customer_management/test_customer_repository.py`
- [x] T018 [P] [US1] Contract tests for `POST/GET/PATCH /api/v1/customers` and deactivate/reactivate in `tests/contract/customer_management/test_customer_api.py`

### Implementation for User Story 1

- [x] T019 [US1] Implement the `Customer` aggregate (identity, status, version, timestamps, update/deactivate/reactivate) in `src/models/customer_management/domain/entities.py` (depends on T006)
- [x] T020 [US1] Implement `CustomerRepository` create/get/update/deactivate/reactivate with version checks in `src/models/customer_management/infrastructure/repository.py` (depends on T009, T019)
- [x] T021 [P] [US1] Implement lifecycle DTOs in `src/models/customer_management/application/dto.py`
- [x] T022 [US1] Implement lifecycle commands and use cases in `src/models/customer_management/application/commands.py` and `application/use_cases.py` (depends on T019, T020, T021)
- [x] T023 [P] [US1] Implement lifecycle Pydantic schemas in `src/models/customer_management/api/schemas.py`
- [x] T024 [US1] Implement lifecycle endpoints in `src/models/customer_management/api/router.py` (depends on T022, T023)
- [x] T025 [US1] Implement the frontend HTTP client for customers in `src/frontend/customer/api_client.py`
- [x] T026 [US1] Implement the customer list and form pages (create/edit/deactivate/reactivate) in `src/frontend/customer/list_page.py` and `src/frontend/customer/form_page.py` (depends on T025)
- [x] T027 [US1] Wire customer pages into navigation in `src/frontend/app.py` (depends on T026)

**Checkpoint**: US1 is fully functional and testable on its own (customer registry MVP).

---

## Phase 4: User Story 2 — Manage Customer Contacts and Addresses (Priority: P1)

**Goal**: Add, update, and remove multiple contacts and addresses per customer; eligibility reflects their presence.

**Independent Test**: Add multiple contacts and addresses, edit one of each, remove one, and confirm persistence plus eligibility changes.

### Tests for User Story 2

- [x] T028
- [x] T029
- [x] T030
- [x] T031

### Implementation for User Story 2

- [x] T032
- [x] T033
- [x] T034
- [x] T035
- [x] T036
- [x] T037
- [x] T038
- [x] T039

**Checkpoint**: US1 and US2 both work independently; the P1 MVP is complete.

---

## Phase 5: User Story 3 — Support Individual and Business Customers (Priority: P2)

**Goal**: Enforce type-specific required fields, type-scoped uniqueness, and safe type changes.

**Independent Test**: Register one individual and one business with the correct details, attempt each with missing/duplicate identity, and change a customer's type.

### Tests for User Story 3

- [x] T040
- [x] T041

### Implementation for User Story 3

- [x] T042
- [x] T043
- [x] T044
- [x] T045

**Checkpoint**: Individual/business behavior is correct and independently testable.

---

## Phase 6: User Story 4 — Search and Filter Customers (Priority: P2)

**Goal**: Search by identifying information and filter by type/status with pagination.

**Independent Test**: Create 25+ mixed customers; verify search terms, type/status filters, pagination totals, and empty results.

### Tests for User Story 4

- [x] T046 [P] [US4] Application tests for search/filter/pagination in `tests/application/customer_management/test_search.py`
- [x] T047 [P] [US4] Integration tests for search/filter over 10,000 rows in `tests/integration/customer_management/test_customer_search_repository.py`
- [x] T048 [P] [US4] Contract tests for `GET /api/v1/customers` query parameters in `tests/contract/customer_management/test_customer_search_api.py`

### Implementation for User Story 4

- [x] T049 [US4] Implement search/filter/pagination queries in `src/models/customer_management/infrastructure/repository.py`
- [x] T050 [US4] Implement the search query use case and result DTO in `src/models/customer_management/application/queries.py`
- [x] T051 [US4] Implement list/search request parameters and response schema in `src/models/customer_management/api/schemas.py` and `api/router.py`
- [x] T052 [US4] Add search and filter controls to the list page in `src/frontend/customer/list_page.py`

**Checkpoint**: Search and filtering are independently functional.

---

## Phase 7: User Story 5 — Consume Customer Data from Other Modules (Priority: P2)

**Goal**: Provide a stable application port and eligibility endpoint so downstream modules read current customer data without duplication.

**Independent Test**: Resolve the port, check an eligible and an ineligible customer, and confirm reasons and current data; confirm no ORM objects cross the boundary.

### Tests for User Story 5

- [x] T053 [P] [US5] Application tests for the eligibility port and DTOs in `tests/application/customer_management/test_eligibility_port.py`
- [x] T054 [P] [US5] Contract tests for `GET /api/v1/customers/{id}/eligibility` in `tests/contract/customer_management/test_customer_eligibility_api.py`

### Implementation for User Story 5

- [x] T055 [US5] Implement eligibility reasons and derived eligibility in `src/models/customer_management/domain/entities.py` and `domain/value_objects.py`
- [x] T056 [US5] Implement `CustomerEligibilityPort` and DTOs in `src/models/customer_management/application/ports.py` and `application/dto.py`
- [x] T057 [US5] Implement the port adapter over the repository in `src/models/customer_management/application/service.py`
- [x] T058 [US5] Implement the eligibility endpoint in `src/models/customer_management/api/router.py` and `api/schemas.py`
- [x] T059 [US5] Wire the port into the composition root in `src/api/health.py` (depends on T057)
- [x] T060 [P] [US5] Document the consumer contract for downstream modules in `docs/customer-management.md`

**Checkpoint**: All five user stories are independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, documentation, and end-to-end validation.

- [x] T061
- [x] T062
- [x] T063
- [x] T064
- [x] T065
- [x] T066
- [x] T067

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Stories (Phases 3–7)**: Depend on Foundational. US1 and US2 are P1; US3–US5 are P2.
- **Polish (Phase 8)**: Depends on the desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Needs Foundational only.
- **US2 (P1)**: Needs Foundational and the `Customer` aggregate from US1.
- **US3 (P2)**: Needs US1 (customer creation/update) and the US2 child entities for complete responses.
- **US4 (P2)**: Needs US1 records and US3 type fields for filtering.
- **US5 (P2)**: Needs US1 (lifecycle) and US2 (contact/address counts) to compute eligibility.

### Within Each User Story

- Tests are written first and must fail before implementation.
- Domain → repository → use cases → schemas → endpoints → UI.
- Story complete and validated before moving to the next priority.

### Parallel Opportunities

- Setup: T002, T003, T004 are parallel; T001 and T005 both touch `pyproject.toml` and must be sequential.
- Foundational: T006, T007, T011, T012, T013 are parallel once their inputs exist.
- Each story's test tasks marked [P] can be written together.
- Independent files (DTOs, schemas, frontend client) can be built in parallel within a story.
- US1 and US2 can be developed in parallel by different developers after Foundational; US3–US5 can start once their prerequisites land.

---

## Parallel Example: User Story 1

```bash
# Write all US1 tests together:
Task: "Unit tests for customer lifecycle invariants in tests/unit/customer_management/test_customer_entity.py"
Task: "Application tests for lifecycle use cases in tests/application/customer_management/test_customer_lifecycle.py"
Task: "Integration tests for repository persistence in tests/integration/customer_management/test_customer_repository.py"
Task: "Contract tests for lifecycle endpoints in tests/contract/customer_management/test_customer_api.py"

# Then build independent pieces:
Task: "Implement lifecycle DTOs in src/models/customer_management/application/dto.py"
Task: "Implement lifecycle Pydantic schemas in src/models/customer_management/api/schemas.py"
```

---

## Implementation Strategy

### MVP First (P1: US1 + US2)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete US1 (customer registry) — validate independently.
3. Complete US2 (contacts/addresses) — validate independently.
4. **STOP and VALIDATE**: run the quickstart scenarios for US1/US2; this is the P1 MVP.
5. Deploy/demo if ready.

US1 alone is a thin but usable slice; US2 completes the P1 requirement set.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. US1 → customer registry demo.
3. US2 → contacts/addresses + eligibility inputs.
4. US3 → individual/business correctness.
5. US4 → search/filter at scale.
6. US5 → downstream consumption port.
7. Polish → hardening and validation.

---

## Notes

- [P] tasks touch different files and have no incomplete dependency.
- Story labels provide traceability to `spec.md`.
- Tests are required by S02-13, the acceptance criteria, and constitution Section 10.
- Commit after each task or logical group; stop at checkpoints to validate independently.
- Do not introduce cross-module repository access; downstream modules use the US5 port only.
