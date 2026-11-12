# Data Model: Integration & MVP Release (S07)

**Generated**: 2026-11-11
**Feature**: Integration & MVP Release (S07)
**Spec**: specs/008-integration-mvp/spec.md
**Research**: specs/008-integration-mvp/research.md

This feature primarily integrates existing module entities. Per the research (Decision 7), the spec's workflow constructs are validation constructs derived from module records — no new database tables for workflow tracking. The only newly persisted artifact is the data generator manifest (Synthetic Data Set). Existing module entities and their cross-module relationships are documented here because the clarified FK constraint chains are the core data contract of this feature.

---

## Cross-Module Relationship Map (existing entities, integrated)

```text
Customer (S02/S03)
    │ 1:N (every order references an existing customer)
    v
Order (S03)
    │ 1:N        │ 1:N                    │ 1:1
    v            v                        v
OrderItem    Shipment (S04)          Invoice (S05)
             (every shipment             (no duplicate invoice
              references an               per order; total matches
              existing order)             order total)
                                    │ 1:N
                                    v
                                Payment (S05)
                                (every payment references an
                                 existing invoice)
```

**Referential integrity chains (enforced at data generation time per clarification)**:
- Every order references an existing customer
- Every shipment references an existing order
- Every invoice references an existing order
- Every payment references an existing invoice

---

## Entity: Synthetic Data Set (data generator manifest — persisted artifact)

**Description**: Represents the manifest of one deterministic synthetic data generation run. Records the seed, requested volumes, actual created counts, and generation timestamp. Emitted as a JSON file by the `bss-datagen` CLI; consumed by integration tests to verify reproducibility (SC-003).

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `seed` | integer | Deterministic generation seed | Required; same seed + same volumes → identical data (100% reproducible, SC-003) |
| `generated_at` | datetime | Generation run timestamp | Required; ISO-8601 |
| `volumes` | object | Requested record counts per module | Required; keys: `customers`, `orders`, `order_items_per_order`, `shipments`, `invoices`, `payments`; all non-negative integers |
| `created` | object | Actual created counts per module | Required; same keys as `volumes`; must satisfy FK chain minimums |
| `fk_chains` | object | Referential integrity summary | Required; counts of orders→customers, shipments→orders, invoices→orders, payments→invoices links; every link references an existing record |
| `database_url` | string | Target database location | Required; defaults to canonical engine URL |
| `generator_version` | string | Generator version identifier | Required; enables manifest compatibility checks |

**Relationships**:
- The manifest describes records created in existing module tables (customers, orders, order_items, shipments, invoices, payments); it owns no business records itself.

**Business Invariants**:
- `created` counts never exceed `volumes` (generation stops on invalid FK reference rather than generating dangling records — per clarified constraint)
- Same `seed` and `volumes` always produce identical `created` counts and identical FK chains
- All generated records satisfy the target module's domain invariants (customer validation, order item rules, invoice numbering `INV-` format, payment amount rules)

**Responsibility**: Provides deterministic, reproducible interconnected test data across all modules; documents generation parameters; enables SC-003 verification; supports configurable record volumes for repeatable development environments.

---

## Entity: Integration Workflow (validation construct — not persisted)

**Description**: Represents one complete business workflow spanning multiple modules (customer-to-order, order-to-shipment, order-to-invoice, invoice-to-payment). Materialized as an ordered sequence of module API operations; its outcome is verified through the resulting business records.

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `workflow_name` | enum | Workflow identifier | Required; values: `customer_to_order`, `order_to_shipment`, `order_to_invoice`, `invoice_to_payment` |
| `participating_modules` | list | Modules involved in the sequence | Required; fixed per workflow (see contracts) |
| `required_permission` | enum | Minimum permission to initiate | Required; values: `user:view`, `user:billing`, `user:admin` (per clarified role mapping) |
| `steps` | list | Ordered module operations | Required; each step names a module endpoint and payload contract |
| `status` | enum | Workflow outcome | Required; values: `running`, `completed`, `failed` |
| `started_at` / `completed_at` | datetime | Execution window | Optional; ISO-8601; emitted as log events (FR-008) |

**Relationships**:
- Customer-to-order: identity (auth) + customer + order modules
- Order-to-shipment: identity + order + shipment modules
- Order-to-invoice: identity + order + billing modules
- Invoice-to-payment: identity + billing modules

**Business Invariants**:
- Each workflow's steps execute in dependency order (order must exist and be `confirmed` before shipment or invoice; invoice must exist and be `pending` before payment)
- Failure at any step leaves prior module records in their last valid state (e.g., failed shipment creation leaves order `confirmed`)
- Workflow completion is evidenced by the terminal business state (order `confirmed` / order `shipped` + shipment with tracking number / invoice `pending` with matching total / invoice `paid` + payment recorded)

**Responsibility**: Defines the end-to-end validation sequence; coordinates module interactions through their APIs; reports success/failure status via business records and structured log events; enforces role-restricted initiation.

---

## Entity: Workflow State (validation construct — not persisted)

**Description**: Represents the current state of a workflow execution, derived from the participating module records at any point in time.

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `workflow_name` | enum | Owning workflow | Required |
| `current_step` | string | Last completed module operation | Required |
| `order_status` | enum | Order lifecycle position | Derived; values: `draft`, `confirmed`, `shipped`, `delivered`, `cancelled` (S03 transitions) |
| `shipment_status` | enum | Shipment lifecycle position | Derived; per specs/005 shipment states |
| `invoice_status` | enum | Invoice lifecycle position | Derived; values: `pending`, `paid` (`paid` is terminal — S05) |
| `completion_status` | enum | Overall workflow outcome | Required; values: `in_progress`, `completed`, `failed` |

**Relationships**: Derived by querying existing module records (order, shipment, invoice, payment) for a given business identifier.

**Business Invariants**:
- `invoice_status` `paid` is terminal: no further payment accepted (spec User Story 4)
- One invoice per order maximum: repeated invoice generation is rejected (spec User Story 3)
- Shipment failure does not regress order status below `confirmed` (spec User Story 2)

**Responsibility**: Tracks workflow progress across module boundaries without owning state; enables rollback-safe failure semantics; provides visibility into workflow status for tests and logs.

---

## Entity: Cross-Module Authorization Check (enforcement + log events — not persisted)

**Description**: Represents an authorization validation spanning module boundaries, enforced at workflow entry points via shared permission dependencies and recorded as structured log events.

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `workflow_name` | enum | Workflow being initiated | Required |
| `required_permission` | enum | Minimum permission | Required; values: `user:view`, `user:billing`, `user:admin` |
| `granted_permissions` | list | Permissions in the JWT claim | Required; from token `permissions` claim |
| `result` | enum | Check outcome | Required; values: `granted`, `denied` |
| `timestamp` | datetime | Check time | Required; ISO-8601; emitted in log event |

**Relationships**:
- `user:view` → customer-to-order only
- `user:billing` → order-to-invoice, invoice-to-payment
- `user:admin` → all four workflows (full access)

**Business Invariants**:
- Missing/invalid token → HTTP 401 (`UNAUTHENTICATED`)
- Valid token lacking the workflow permission → HTTP 403 (`FORBIDDEN`)
- Denials are logged as structured events with required permission (FR-005, FR-008); no secrets logged

**Responsibility**: Validates that the requesting user holds the workflow's permission; logs authorization events; returns standardized access-control errors per the error contract.

---

## State Transitions (existing entities, exercised by workflows)

**Order (S03)**: `draft` → `confirmed` → `shipped` → `delivered`; `cancelled` from non-terminal states. Customer-to-order completes at `confirmed`; order-to-shipment moves `confirmed` → `shipped`.

**Invoice (S05)**: `pending` → `paid` (terminal). Order-to-invoice creates at `pending`; invoice-to-payment completes at `paid`. Invoice number format `INV-` per specs/006.

**Shipment (S04)**: created with unique tracking number per specs/005; delivery tracking states per that spec.

## Validation Rules (from Requirements)

- **FR-005**: role-restricted workflow access per the clarified mapping (user:view / user:billing / user:admin); 401 unauthenticated, 403 under-privileged
- **FR-006 / clarification**: synthetic data enforces FK chains at generation time — orders→customers, shipments→orders, invoices→orders, payments→invoices; invalid seeds fail generation rather than producing dangling references
- **FR-007**: standardized error envelope `{"error": "<type>", "message": "<human-readable>", "code": "<error-code>"}` on HTTP 400/401/403/404/500 across all integration endpoints
- **FR-008**: `workflow.started` / `workflow.completed` / `workflow.failed` structured log events with no missing entries (SC-006)
- **FR-009 / SC-007**: migrations from a completely clean database establish all module schema; seed data for integration testing comes from the generator manifest
- **Spec User Story 1**: order without items is rejected (empty-cart mapping); order created with status `confirmed` and correct customer/item association
- **Spec User Story 3**: invoice total must match the associated order total; no duplicate invoice per order
- **Spec User Story 4**: payment on a `paid` invoice is rejected; payment records amount and timestamp
