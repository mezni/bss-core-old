# Tasks: Order Management (S03)

**Feature**: Order Management  
**Feature Directory**: `specs/004-order-management`  
**Priority Order**: P1 → P2 → P3  
**Status**: Draft - ready for implementation

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [US1] Create project structure per implementation plan (src/, tests/, contracts/, configs/)
- [ ] T002 Initialize Python project with FastAPI, SQLAlchemy 2.x, Alembic, Pydantic dependencies
- [ ] T003 [P] Configure linting and formatting tools (Ruff) with project-specific rules
- [ ] T004 Setup git hooks and pre-commit configuration for BSS-Core conformity
- [ ] T005 Create base directory structure: src/domain/, src/application/, src/infrastructure/, src/presentation/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] [US1] Setup SQLite database with Alembic migration framework for Order entity
- [ ] T006 [P] [US1] Configure SQLAlchemy 2.x ORDermapper with Order and Order Item models
- [ ] T007 [P] [US1] Define Order domain model with business invariants (status transitions, item prerequisites, cancellation terminal)
- [ ] T008 [P] [US1] Define Order Item model with description, quantity, unit price, line total
- [ ] T009 [P] [US2] Implement customer eligibility check from S02 (at least one contact + one address)
- [ ] T010 [P] [US1,US2] Configure JWT authentication (customer:view, customer:manage permissions)
- [ ] T011 [P] [US1,US2] Setup API routing structure under /api/v1/orders with versioning
- [ ] T012 [P] [US1,US2] Configure Pydantic request/response models for all Order endpoints
- [ ] T011 [P] [US1,US2] Setup error handling middleware with consistent error envelope format

---

## Phase 3: User Story 1 - Create Order (Priority: P1) 🎯 MVP

**Goal**: A registered customer can create a new order in draft status requiring at least one order item

**Independent Test**: Create an order with valid customer_id and at least one item → verify status=draft, version=1; repeat request returns appropriate error

- [ ] T012 [P] [US1] Create Order model (Pydantic) with customer_id, items (description, quantity, unit_price), status, version
- [ ] T013 [P] [US1] Implement Order creation use case with customer eligibility validation from S02
- [ ] T014 [US1] Implement POST /api/v1/orders endpoint (create order) with customer_id and items
- [ ] T015 [US1] Add validation: at least one order item required before order can be confirmed
- [ ] T016 [US1] Add response model for order creation (201 Created with id, status, subtotal, tax, total, version)
- [ ] T017 [US1] Write contract test for POST /api/v1/orders in tests/contract/test_order_api.py
- [ ] T018 [P] [US1] Write integration test for order creation flow in tests/integration/test_order_lifecycle.py

---

## Phase 4: User Story 2 - Manage Order Items (Priority: P2)

**Goal**: An authenticated user can add, modify, or remove individual items from an order. Order total updates automatically as items change.

**Independent Test**: Create an order with one item, add a second item, modify quantity of first item, remove second item, verify order total reflects only remaining item

- [ ] T019 [P] [US2] Implement PATCH /api/v1/orders/{{order_id}} endpoint for item modifications
- [ ] T020 [P] [US2] Add Order Item creation endpoint (POST /api/v1/orders/{{order_id}}/items)
- [ ] T021 [P] [US2] Add Order Item modification endpoint (PATCH /api/v1/orders/{{order_id}}/items/{{item_id}})
- [ ] T022 [P] [US2] Add Order Item removal endpoint (DELETE /api/v1/orders/{{order_id}}/items/{{item_id}})
- [ ] T022 [US1] Update order total recalculation on item changes
- [ ] T023 [US1] Write contract test for order item endpoints in tests/contract/test_order_items.py
- [ ] T024 [P] [US2] Write integration test for order item management flow

---

## Phase 5: User Story 3 - Order Lifecycle Transitions (Priority: P3)

**Goal**: An order progresses through well-defined status stages — draft → confirmed → shipped → delivered → cancelled. Each transition has preconditions and is irreversible or requires specific actions.

**Independent Test**: Create an order, confirm it (with items), ship it, deliver it; attempt invalid transitions (cancel confirmed) → verify 409 errors

- [ ] T025 [P] [US3] Implement status transition enforcement in domain layer (confirmed requires ≥1 item, cancelled only in draft, shipped requires confirmed, delivered requires shipped)
- [ ] T026 [P] [US3] Implement PATCH /api/v1/orders/{{order_id}} with status transition validation
- [ ] T027 [US3] Write contract test for order status transitions in tests/contract/test_order_transitions.py
- [ ] T028 [P] [US3] Write integration test for order lifecycle (draft → confirmed → shipped → delivered, draft → cancelled)

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Documentation updates in specs/004-order-management/ (spec.md updates, new contract additions)
- [ ] T030 Code cleanup and refactoring - ensure all order-related code follows BSS-Core conventions
- [ ] T031 [P] Performance optimization across all order stories (subtotal/total calculation O(n), listing performance)
- [ ] T032 [P] Security hardening - verify authorization on all order endpoints (customer:view for read, customer:manage for write)
- [ ] T033 [P] Run quickstart.md validation end-to-end
- [ ] T034 [P] Additional unit tests in tests/unit/ for order domain logic
- [ ] T035 [P] Run ruff check src tests --fix

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (MVP)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 items but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 transitions but should be independently testable

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

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tasks in parallel:
Task: "Setup SQLite database with Alembic migration framework"
Task: "Configure SQLAlchemy 2.x ORM mapper with Order and Order Item models"
Task: "Define Order domain model with business invariants"
Task: "Define Order Item model with description, quantity, unit price"
Task: "Implement customer eligibility check from S02"
Task: "Configure JWT authentication (customer:view, customer:manage)"
Task: "Setup API routing structure under /api/v1/orders"
Task: "Configure Pydantic request/response models"
Task: "Setup error handling middleware"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Order) ✓
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready (MVP!)

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
   - Developer A: User Story 1 (Create Order)
   - Developer B: User Story 2 (Manage Order Items)
   - Developer C: User Story 3 (Order Lifecycle Transitions)
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
