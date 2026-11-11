# Tasks: Shipment Management (S04)

**Feature Branch**: `005-shipment-management`

**Input**: Feature specification from `specs/005-shipment-management/spec.md`; design documents from `plan.md`, `research.md`, `data-model.md`, `contracts/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

---

## Sample Tasks (replace with actual implementation tasks)

> **NOTE**: The following are sample tasks illustrating the required format. They must be replaced with actual implementation tasks based on the user stories, requirements, and contracts from the feature specification.

### Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Initialize Python project structure with package configuration
- [ ] T002 [P] Configure linting (Ruff) and formatting (Black) tools
- [ ] T003 [P] Set up UTF-8 encoding and locale configuration

### Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] [US1] Setup SQLAlchemy 2.x engine and session configuration (per constitution Section 7)
- [ ] T005 [P] [US1] Configure Alembic migration framework with initial migration scaffold
- [ ] T006 [P] [US1] Define Shipment domain model in SQLAlchemy ORM (per data-model.md entities)
- [ ] T007 [P] [US1] Define Order domain model in SQLAlchemy ORM (per data-model.md entities)
- [ ] T008 [P] [US1] Create database migration for shipment table (per constitution Section 7)
- [ ] T009 [P] [US1] Create database migration for order table (per constitution Section 7)
- [ ] T009a [P] Define relationship: Order.shipments one-to-many (Shipment.order_id foreign key)
- [ ] T009b [P] Define relationship: Shipment.order many-to-one (Order.shipments backref)

### Phase 3: User Story 1 - Create Shipment (Priority: P1) 🎯 MVP

**Goal**: An authenticated user can create a new shipment for a confirmed order, initiating the delivery process. The shipment starts in pending status with a tracking reference.

**Independent Test**: Can be fully tested by creating a shipment with a valid confirmed order ID and carrier name, verifying the shipment is assigned an ID, status is set to pending, and tracking reference is generated. The test succeeds even if no other shipment flows are exercised.

- [ ] T010 [P] [US1] Implement shipment creation API endpoint POST /api/v1/shipments
- [ ] T011 [P] [US1] Implement order eligibility validation (order must be confirmed status) per FR-002
- [ ] T012 [P] [US1] Implement tracking reference generation (SHIP-[UUID v4 substring]) per FR-003
- [ ] T013 [P] [US1] Implement carrier name storage and validation per FR-004
- [ ] T014 [US1] Implement shipment status: pending (default) per FR-005 and SC-004
- [ ] T015 [US1] Implement response model: id, status, tracking_reference, carrier_name, order_id, version per shipment_create_api_contract.md
- [ ] T015a [US1] Write contract test for POST /api/v1/shipments per shipment_create_api_contract.md
- [ ] T016 [US1] Implement JSON request validation (order_id, optional carrier_name) per contract
- [ ] T017 [US1] Implement error handling: 400 for non-confirmed order, 401 auth, 403 permission
- [ ] T018 [US1] Implement JWT authentication middleware (per S01 Identity & Access dependency)
- [ ] T018a [US1] Implement customer:manage permission check for shipment creation
- [ ] T019 [US1] Add logging for shipment creation events (per constitution Section 11 structured JSON logging)
- [ ] T020 [US1] Write unit test for shipment creation with valid confirmed order
- [ ] T021 [US1] Write unit test for shipment creation rejection with non-confirmed order

### Phase 4: User Story 2 - Update Shipment (Priority: P2)

**Goal**: An authenticated user can update shipment information such as carrier, tracking number, or status while in pending status. This allows the logistics team to correct or update shipment details as needed.

**Independent Test**: Can be fully tested by creating a shipment, updating its carrier and tracking number, and verifying the updated information is reflected in the shipment response. The test passes regardless of subsequent status changes.

- [ ] T022 [P] [US2] Implement shipment update API endpoint PATCH /api/v1/shipments/{shipment_id}
- [ ] T023 [P] [US2] Implement version tracking and stale update detection (409 Conflict STALE_UPDATE) per contract
- [ ] T024 [P] [US2] Implement carrier name update while shipment in pending status per FR-004
- [ ] T025 [P] [US2] Implement status transition: pending → in-transit per FR-005
- [ ] T026 [US2] Implement response model: id, new_status, updated_at, version per shipment_update_api_contract.md
- [ ] T027 [US2] Write contract test for PATCH /api/v1/shipments/{shipment_id} per shipment_update_api_contract.md
- [ ] T028 [US2] Implement error handling: 400 invalid version, 409 stale update, 409 invalid transition, 401 auth, 403 permission
- [ ] T029 [US2] Implement status transition: in-transit → delivered per FR-005 (confirmation only)
- [ ] T030 [US2] Implement 409 Conflict INVALID_TRANSITION error for delivered→in-transit
- [ ] T031 [US2] Implement JWT authentication middleware for update operations
- [ ] T031a [US2] Implement customer:manage permission check for shipment updates
- [ ] T032 [US2] Add logging for shipment update events (per constitution Section 11)
- [ ] T033 [US2] Write unit test for shipment carrier update in pending status
- [ ] T034 [US2] Write unit test for invalid status transition rejection

### Phase 5: User Story 3 - Confirm Delivery (Priority: P3)

**Goal**: An authenticated user can confirm that an order has been delivered, updating the shipment status to delivered and closing the delivery lifecycle.

**Independent Test**: Can be fully tested by creating a shipment, updating its status to in-transit, confirming delivery, and verifying the shipment status changes to delivered. The test validates the boundary rules without requiring the full billing workflow.

- [ ] T035 [P] [US3] Implement delivery confirmation API endpoint PATCH /api/v1/shipments/{shipment_id} with status: delivered
- [ ] T036 [P] [US3] Implement delivered_at timestamp setting on delivery confirmation
- [ ] T037 [P] [US3] Implement delivery confirmation is terminal: shipments in delivered status cannot be modified per FR-005
- [ ] T038 [US3] Implement response model: id, status, version, delivered_at per contract
- [ ] T039 [US3] Write contract test for delivery confirmation per scenario 4 in quickstart.md
- [ ] T040 [US3] Implement error handling: 400 delivered already confirmed, 401 auth, 403 permission
- [ ] T033a [US3] Implement customer:view/manage permission check for delivery confirmation
- [ ] T033b [US3] Add logging for delivery confirmation events (per constitution Section 11)
- [ ] T041 [US3] Write unit test for delivery confirmation with status change to delivered
- [ ] T042 [US3] Write unit test for rejected re-delivery confirmation attempt

### Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T043 [P] Run quickstart.md validation scenarios (all 6 scenarios) and fix any failures
- [ ] T044 [P] Implement structured JSON logging for all shipment state transitions and critical API errors (constitution Section 11)
- [ ] T045 [P] Performance optimization: ensure shipment API create/list operations respond in under 200ms (SC-007)
- [ ] T046 [P] Security hardening: implement rate limiting on shipment API endpoints
- [ ] T047 [P] [P] Add comprehensive unit tests for shipment domain logic (valid status transitions, tracking reference requirements)
- [ ] T048 [P] [P] Add integration test suite covering end-to-end shipment lifecycle (create → update → confirm delivery)
- [ ] T049 [P] Code review and constitution compliance check across all implemented modules
- [ ] T050 [P] Update documentation: API endpoints, data models, and task traceability
- [ ] T051 [P] Run Ruff linting and formatting checks across entire shipment module
- [ ] T052 [P] [P] Deploy development environment and validate end-to-end workflow