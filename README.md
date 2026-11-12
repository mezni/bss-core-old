# BSS Core — S07 Integration & MVP Release

## Overview

**BSS Core** is a modular business management system. S01 delivers authenticated
access control, role-based permissions, and module-based authorization. S02 adds
**Customer Management**: customer identity, lifecycle, contacts, addresses,
search, and a downstream eligibility contract. S03–S05 add orders, shipments,
and billing; S07 wires them into four end-to-end workflows on a single FastAPI
application.

- **JWT bearer authentication** with permission claims (`user:view`,
  `user:billing`, `user:admin`, plus module permissions such as
  `customer:view`/`customer:manage`)
- **Argon2id dependency available** for future credential storage (the MVP
  validates externally minted JWTs; it does not expose login/password routes)
- **Customer registry** for individuals and businesses with type-scoped uniqueness
- **Optimistic concurrency** on every customer aggregate mutation
- **Contacts and addresses** with single-primary rules
- **Search, filtering, and pagination** over customer data
- **Eligibility port** for Order, Shipment, and Billing without cross-module ORM access
- **Two-application architecture**: FastAPI backend + Streamlit frontend over HTTP

## Architecture

The system follows a **modular monolith** with Clean Architecture layers:

```
src/
├── domain/                  # Database engine, auth primitives
├── application/             # Cross-cutting application layer
├── infrastructure/          # Cross-cutting infrastructure layer
├── presentation/            # Presentation layer
├── api/                     # FastAPI composition root (src/api/health.py)
├── frontend/                # Streamlit UI (HTTP only)
│   └── customer/            # Customer API client and pages
└── models/
    └── customer_management/
        ├── domain/          # Entities, value objects, repository port
        ├── application/     # DTOs, commands, queries, use cases, eligibility port
        ├── infrastructure/  # SQLAlchemy ORM, repository, logging
        ├── api/             # Schemas, router, dependencies, error envelope
        └── presentation/    # Module presentation boundary
```

## Technology Stack

- **Language**: Python 3.12+
- **Backend**: FastAPI, SQLAlchemy 2.x, Alembic, Argon2id, PyJWT
- **Frontend**: Streamlit, httpx
- **Package Manager**: uv
- **Testing**: pytest (unit, application, integration, contract)
- **Linting**: Ruff
- **Database**: SQLite (initial, designed for evolution)

## Quickstart

### Prerequisites

- Python 3.12+
- `uv` package manager
- Git

### Installation

```bash
git clone <repository-url>
cd bss-core
uv sync
uv run alembic upgrade head
```

### Running the Applications

**Backend (FastAPI)**:

```bash
uv run uvicorn src.api.health:app --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit)**:

```bash
BSS_API_URL=http://localhost:8000 BSS_API_TOKEN=<jwt> \
  uv run streamlit run src/frontend/app.py
```

Set `BSS_JWT_SECRET` to the secret used by the identity service to sign tokens.
The development fallback is not suitable for production.

### Synthetic data

```bash
# Deterministic seed and configurable volumes (customers -> orders -> shipments
# -> invoices -> payments); writes db/datagen-manifest.json
uv run bss-datagen --seed 42 --customers 50 --orders 100
```

### Tests and linting

```bash
uv run pytest
uv run ruff check src tests
```

The end-to-end workflow evidence lives in `tests/integration/e2e/`
(`test_customer_to_order.py`, `test_order_to_shipment.py`,
`test_order_to_invoice.py`, `test_invoice_to_payment.py`,
`test_clean_database_migrations.py`).

## Customer API

Base path: `/api/v1/customers`

| Method | Path | Permission |
|---|---|---|
| `POST` | `/` | `customer:manage` |
| `GET` | `/` | `customer:view` |
| `GET` | `/{id}` | `customer:view` |
| `PATCH` | `/{id}` | `customer:manage` |
| `POST` | `/{id}/deactivate` | `customer:manage` |
| `POST` | `/{id}/reactivate` | `customer:manage` |
| `GET` | `/{id}/eligibility` | `customer:view` |
| `POST` | `/{id}/contacts` | `customer:manage` |
| `PATCH` | `/{id}/contacts/{contact_id}` | `customer:manage` |
| `DELETE` | `/{id}/contacts/{contact_id}` | `customer:manage` |
| `POST` | `/{id}/addresses` | `customer:manage` |
| `PATCH` | `/{id}/addresses/{address_id}` | `customer:manage` |
| `DELETE` | `/{id}/addresses/{address_id}` | `customer:manage` |

Every mutation increments the customer aggregate `version`. See
`docs/customer-management.md` and `specs/003-customer-management/contracts/`
for the full contract and consumer port.

## Workflow APIs

| Workflow | Endpoint | Permission |
|---|---|---|
| Customer → Order | `POST /api/v1/orders`, `PATCH /api/v1/orders/{id}/transitions/confirm` | `user:view` |
| Order → Shipment | `POST /api/v1/shipments`, `PATCH /api/v1/shipments/{shipment_id}` | `user:admin` |
| Order → Invoice | `POST /api/v1/invoices`, `GET /api/v1/invoices` | `user:billing` (write), `user:view` (read) |
| Invoice → Payment | `POST /api/v1/payments` | `user:billing` |

All errors use the standardized envelope
`{"error": "<slug>", "message": "<human-readable>", "code": "<CODE>"}`.

## Implementation Status

| Sprint | Scope | Status |
|---|---|---|
| S01 | Identity & Access foundation | Complete (JWT + RBAC) |
| S02 | Customer Management | Complete (67 tasks) |
| S03 | Order Management | Complete for MVP workflows |
| S04 | Shipment Management | Complete for MVP workflows (create + status/lifecycle updates; list/UI deferred) |
| S05 | Billing Management | Complete for MVP workflows (invoice + payment; update/UI deferred) |
| S06 | Dashboard & Reporting | Partial (stored metrics and reporting periods) |
| S07 | Integration & MVP Release | Complete for MVP workflows |

S02 includes unit, application, integration, contract, migration, and
performance coverage. Run `uv run pytest` for the current suite.

S07 Integration & MVP Release delivers four end-to-end workflows (customer-to-order,
order-to-shipment, order-to-invoice, invoice-to-payment) with consolidated runtime,
single FastAPI app (`src/api/health.py`), centralized PyJWT authorization
(`user:view`/`user:billing`/`user:admin`), standardized error envelope
`{"error", "message", "code"}`, deterministic data generator (`bss-datagen`), and
E2E journey tests. Requirements quality checklist: `specs/008-integration-mvp/checklists/integration.md`.

## Key Decisions

- **Two-application architecture**: backend API + Streamlit frontend with strict HTTP separation
- **Modular monolith**: customer code isolated under `src/models/customer_management/`
- **Type-scoped uniqueness**: individual email and business registration/tax ID
- **Optimistic concurrency**: stale aggregate versions return `409 STALE_UPDATE`
- **Partial unique indexes**: enforce uniqueness at the database boundary
- **Application port**: downstream modules use `CustomerEligibilityPort`, never the repository
- **Structured logging without PII**: lifecycle events log IDs, actions, status, and versions only

## Sprints

The system is delivered across 7 sprints (S00–S07):

- **S00** — Project Foundation
- **S01** — Identity & Access
- **S02** — Customer Management
- **S03** — Order Management
- **S04** — Shipment Management
- **S05** — Billing Management
- **S06** — Dashboard & Reporting
- **S07** — Integration & MVP Release *(current)*

## License

MIT License — see LICENSE file for details.
