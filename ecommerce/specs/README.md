# Feature Specifications

This directory is the **single canonical location for all Speckit-generated
feature specifications**, as mandated by the project constitution
(see `.specify/memory/constitution.md`, Principle *Speckit Development
Process*). Feature directories MUST NOT be created under `docs/` or the
repository root.

Each feature is numbered sequentially, named `NNN-slug/`, and MUST be
independently implementable. The active feature directory is resolved by the
Speckit tooling from `SPECS_DIR` (repository `specs/`) and/or
`.specify/feature.json`.

## Roadmap

| # | Feature | Purpose |
|---|---------|---------|
| 001 | `001-foundation` | Project scaffolding, config, logging, error envelope, health endpoint, Alembic baseline |
| 002 | `002-product-catalog` | Products, categories, listing/filtering/pagination, CRUD |
| 003 | `003-customers` | Customer registration, profile, status lifecycle |
| 004 | `004-cart` | Cart lifecycle, cart items, quantity rules, pricing |
| 005 | `005-orders` | Order lifecycle, order items, state transitions, checkout |
| 006 | `006-inventory` | Stock levels, reservation, release, conflict detection |
| 007 | `007-payments` | Payment authorization/capture, fake payment provider, payment states |
| 008 | `008-fake-data-generator` | **High priority.** Deterministic fake-data generator + CLI |
| 009 | `009-failure-simulation` | Deterministic + randomized failure injection |
| 010 | `010-authentication` | Fake auth (customer/admin/service roles) and authorization rules |
| 011 | `011-observability` | Request IDs, structured logging, domain events, metrics |

> `008-fake-data-generator` is a first-class, high-priority feature. The
> fake-data generator is a project capability in its own right — not an
> afterthought of the other features — and must be executable independently of
> the FastAPI server.

### Decisions deferred into a feature spec

Architecture divergence A6 was deliberately deferred (see `docs/CHANGELOG.md` and
`docs/architecture.md` §60.1). The author of the affected spec MUST resolve it.

| Spec | Deferred decision | Interim contract |
|------|-------------------|------------------|
| `005-orders` | **A6 — checkout route shape.** `POST /api/v1/checkout` with `cart_id` in the body, vs. `POST /api/v1/carts/{cart_id}/checkout`. | `POST /api/v1/checkout` remains published in `docs/API.md` §21, `README.md`, and `docs/failure-simulation.md` §46. If the spec diverges, all affected documents MUST be updated in the same commit. |

Money representation is **not** deferred: integer minor units are settled (divergence A5, resolved —
`docs/architecture.md` §20.1) and binding on every spec.

## Contents of a feature directory

Artifacts are produced by the Spec Kit commands, not authored by hand:

```text
NNN-slug/
├── spec.md        # /speckit.specify   — observable behavior (no implementation detail)
├── plan.md        # /speckit.plan      — design & technical approach
├── tasks.md       # /speckit.tasks     — implementation task breakdown
├── research.md    # (optional)         # open questions & decisions
├── data-model.md  # (optional)         # entities, value objects, schema sketch
├── quickstart.md  # (optional)         # integration guide
└── contracts/     # (optional)         — API/interface contracts
```

## How to work a feature

```text
/speckit.specify  -> write spec.md      (behavior, requirements)
/speckit.plan     -> write plan.md      (design, layers, tradeoffs)
/speckit.tasks    -> write tasks.md     (ordered, dependency-aware work items)
   ... implement, test, validate ...
   ... update docs/ and CHANGELOG.md ...
```

A feature is only complete when behavior is specified, business rules are
documented, implementation is complete, tests exist, API contracts are
validated, migrations exist where required, error behavior is defined, and
documentation is updated. An endpoint returning `200 OK` is **not** sufficient
evidence of completion.
