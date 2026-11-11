---
description: "Task list template for feature implementation"
---

# Tasks: Billing (S05)

**Input**: Design documents from `/specs/006-billing/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Paths shown below assume single project** - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

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
- [x] T005 [P] Implement authentication/authorization framework with JWT (RBAC)
- [x] T006 [P] Setup API routing and middleware structure with FastAPI
- [x] T007 Create base models/entities that all stories depend on: Invoice, Payment, Order models
- [x] T008 Configure error handling and logging infrastructure with structured JSON logging
- [x] T009 Setup environment configuration management
- [ ] T036 [P] [US1] Implement API response time validation for invoice creation endpoint (target: ≤200ms per SC-007)
- [ ] T037 [P] [US1] Implement API response time validation for invoice list endpoint (target: ≤200ms per SC-007)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Invoice (Priority: P1) 🎯 MVP

**Goal**: An authenticated user can generate an invoice for a completed order or shipment, initiating the billing process.

**Independent Test**: Can be fully tested by generating an invoice for a completed order, verifying the invoice is assigned an ID, total amount is calculated correctly, and billing information is captured. The test succeeds even if no other billing flows are exercised.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for create invoice endpoint in tests/contract/test_invoice_create.py
- [ ] T011 [P] [US1] Integration test for generate invoice user journey in tests/integration/test_invoice_create.py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create Invoice model in src/models/invoice.py
- [ ] T013 [P] [US1] Create Payment model in src/models/payment.py
- [ ] T014 [US1] Implement InvoiceService in src/services/invoice_service.py (depends on T012, T013)
- [ ] T015 [US1] Implement invoice creation endpoint in src/presentation/api/invoice_endpoints.py
- [ ] T016 [US1] Add validation and error handling for FR-001, FR-002, FR-003
- [ ] T017 [US1] Add logging for invoice creation operations
- [ ] T035 [P] [US1] Implement pagination parameters (page, page_size) for list invoices GET /api/v1/invoices in src/presentation/api/invoice_endpoints.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Process Payment (Priority: P2)

**Goal**: An authenticated user can process a payment against an invoice, recording payment details and updating the invoice status.

**Independent Test**: Can be fully tested by processing a payment against an invoice, verifying the payment is assigned an ID, amount matches invoice total, and invoice status updates to paid. The test passes regardless of subsequent status changes.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US2] Contract test for process payment endpoint in tests/contract/test_invoice_process_payment.py
- [ ] T019 [P] [US2] Integration test for process payment user journey in tests/integration/test_invoice_process_payment.py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Implement process payment endpoint in src/presentation/api/invoice_endpoints.py
- [ ] T021 [US2] Implement process payment service in src/services/invoice_service.py
- [ ] T022 [US2] Add validation and error handling for FR-004, FR-005, FR-006
- [ ] T023 [US2] Integrate with User Story 1 components (invoice model, service layer)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Billing History (Priority: P3)

**Goal**: An authenticated user can view billing history for their account, seeing all invoices and payments associated with their orders or shipments.

**Independent Test**: Can be fully tested by viewing billing history for a customer, verifying all invoices and payments are listed with correct amounts and statuses. The test validates the boundary rules without requiring the full accounting workflow.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US3] Contract test for view billing history endpoint in tests/contract/test_invoice_billing_history.py
- [ ] T025 [P] [US3] Integration test for view billing history user journey in tests/integration/test_invoice_billing_history.py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Implement view billing history endpoint in src/presentation/api/invoice_endpoints.py
- [ ] T027 [US3] Implement billing history service in src/services/invoice_service.py
- [ ] T028 [US3] Add status transition validation and completed_at timestamp handling

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Documentation updates in docs/ referencing invoice API contracts
- [ ] T030 Code cleanup and refactoring across invoice service, models, and endpoints
- [ ] T031 [P] Performance optimization across all stories (target: sub-200ms create/list operations)
- [ ] T032 [P] Additional unit tests in tests/unit/ for domain logic
- [ ] T033 Security hardening: JWT validation, permission checks, input validation
- [ ] T034 Run quickstart.md validation all validation scenarios pass

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

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
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

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for create invoice endpoint in tests/contract/test_invoice_create.py"
Task: "Integration test for generate invoice user journey in tests/integration/test_invoice_create.py"

# Launch all models for User Story 1 together:
Task: "Create Invoice model in src/models/invoice.py"
Task: "Create Payment model in src/models/payment.py"
```

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

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence