# Fake E-Commerce Server

A realistic, deterministic, extensible **fake** e-commerce backend built with FastAPI and SQLite.
It behaves like a real e-commerce system while using only synthetic data — no real customers, no
real payments, no real credentials.

Built for local development, API integration testing, client development, agent/tool-calling
experiments, failure and resilience testing, and learning modern Python backend architecture.

> **Status:** Early — documentation and specification complete, implementation not yet started.
> Feature roadmap: [`specs/README.md`](specs/README.md).
> Engineering rules: [`.specify/memory/constitution.md`](.specify/memory/constitution.md).

---

## What This Is

The hard part of building a client or a backend is not the happy path — it is declines, timeouts,
insufficient stock, retries, and partial failure. This server makes all of that reproducible on
demand:

* **Realistic** — proper layered architecture, explicit domain invariants, HTTP-correct responses.
* **Deterministic** — the same seed always produces the same data. The same failure request always
  produces the same failure.
* **Populated** — a first-class fake-data generator means you never insert a row by hand.
* **Breakable on demand** — deterministic failure injection for declines, timeouts, conflicts, and
  5xx errors.

---

## Features

| Area | Capability |
|---|---|
| **Product Catalog** | Categories, products, search, filtering, pagination, admin CRUD |
| **Customers** | Registration, profile, status lifecycle, ownership boundaries |
| **Carts** | Add/update/remove items, quantity rules, server-computed totals |
| **Inventory** | Stock levels, reservation, release, availability checks |
| **Orders** | Explicit lifecycle, state-transition guards, totals derived from items |
| **Payments** | Synthetic provider, explicit payment states, authorize/capture/refund |
| **Checkout** | Full workflow: validate → reserve → order → authorize → confirm, with compensation |
| **Fake Data** | Deterministic, configurable, relationship-safe generator with a CLI |
| **Failure Simulation** | Deterministic (`X-Fake-Failure`) and randomized failure injection, latency, timeouts |
| **Authentication** | Fake auth with `customer` / `admin` / `service` roles |
| **Observability** | Request IDs, structured logging, `GET /health` |
| **Testing** | `unit` / `integration` / `api` tiers, isolated, deterministic |

---

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.12+ |
| API | FastAPI |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x |
| Database | SQLite |
| Migrations | Alembic |
| Package management | uv |
| Testing | pytest |
| HTTP testing | HTTPX |
| Fake data | Faker |
| Server | Uvicorn |

Modular monolith. No microservices, message brokers, event sourcing, or CQRS.

---

## Installation

```bash
git clone <repo>
cd ecommerce

make install          # uv sync
cp .env.example .env  # optional — sensible defaults apply without it
```

Or without make:

```bash
uv sync
```

---

## Quick Start

```bash
make bootstrap        # install + migrate + seed
make run              # start on http://127.0.0.1:8000
```

Explicitly:

```bash
uv sync
uv run alembic upgrade head
uv run python -m ecommerce.seed
uv run uvicorn ecommerce.main:app --reload
```

| URL | Purpose |
|---|---|
| <http://127.0.0.1:8000/health> | Liveness |
| <http://127.0.0.1:8000/docs> | Interactive OpenAPI docs |
| <http://127.0.0.1:8000/openapi.json> | Machine-readable schema |
| <http://127.0.0.1:8000/api/v1/...> | Versioned API |

---

## Running Migrations

SQLite is the default database; the dev database lives at `data/ecommerce.db`. The schema is
managed **exclusively** by Alembic.

```bash
make migrate                              # uv run alembic upgrade head
make migrate-new m="create products"      # autogenerate a revision
make migration-status
make db-reset                             # drop file + migrate + seed
```

Autogenerate output must be reviewed before applying. The application never creates or alters
schema at startup.

---

## Generating Fake Data

The generator is a first-class capability and runs **without the HTTP server**.

```bash
uv run python -m ecommerce.seed
```

```bash
uv run python -m ecommerce.seed \
    --customers 100 \
    --products 500 \
    --orders 1000 \
    --seed 42
```

```bash
uv run python -m ecommerce.seed --profile development
uv run python -m ecommerce.seed --reset
```

| Option | Default | Notes |
|---|---|---|
| `--seed` | `RANDOM_SEED` (else `42`) | Same seed → same data |
| `--profile` | *(none)* | `test`, `development`, `large` |
| `--categories` | profile | Number of categories |
| `--products` | profile | Number of products |
| `--customers` | profile | Number of customers |
| `--carts` | derived | Number of carts; omitted derives a realistic subset of customers |
| `--orders` | profile | Number of orders |
| `--reset` | off | Clear generated rows first |
| `--validate` / `--no-validate` | on | Post-generation validation |
| `--quiet` | off | Suppress progress output |
| `--output` | `text` | `text` or `json` for the summary |

Full option reference, including the precedence rules between flags, `RANDOM_SEED`, and
`.env`: [`docs/generator.md` §44](docs/generator.md).

| Profile | Categories | Products | Customers | Orders |
|---|---|---|---|---|
| `test` | 5 | 20 | 10 | 25 |
| `development` *(default)* | 12 | 200 | 50 | 300 |
| `large` | 40 | 5,000 | 2,000 | 20,000 |

```text
Fake E-Commerce Data Generator

Seed:       42
Profile:    development
Customers:  50
Products:   200
Orders:     300

Validation:
✓ Record counts      ✓ Foreign keys       ✓ Inventory consistency
✓ Order totals       ✓ Payment relations  ✓ Entity states

Generation completed successfully.
```

Full contract: [`docs/generator.md`](docs/generator.md).

---

## Running Tests

```bash
make test           # full suite
make test-unit      # fast inner loop, no database
uv run pytest -k "inventory" -v
```

```text
tests/
├── unit/          # domain + application, no database
├── integration/   # repositories, SQLite, transactions, migrations
└── api/           # HTTP contract, workflows, failures, auth
```

Tests are isolated, order-independent, and use a dedicated test database. Development data is never
touched. Full strategy: [`docs/testing.md`](docs/testing.md).

---

## Example API Requests

```bash
BASE=http://127.0.0.1:8000
TOKEN=<fake token>
```

**Health**

```bash
curl -s $BASE/health
```

**Browse the catalog**

```bash
curl -s "$BASE/api/v1/products?is_active=true&page=1&page_size=5"
```

**Register a customer** (synthetic data only)

```bash
curl -s -X POST $BASE/api/v1/customers \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev1@example.invalid","full_name":"Dev One"}'
```

**Create a cart and add a product**

```bash
PRODUCT_ID=$(curl -s "$BASE/api/v1/products?is_active=true&page_size=1" | jq -r '.items[0].id')
CART=$(curl -s -X POST $BASE/api/v1/carts -H "Authorization: Bearer $TOKEN" | jq -r '.id')

curl -s -X POST $BASE/api/v1/carts/$CART/items \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"product_id":"'"$PRODUCT_ID"'","quantity":2}'
```

**Checkout**

```bash
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
```

**Deterministic failure** — the point of the whole project

```bash
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -H 'X-Fake-Failure: payment_declined' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
```

```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Payment was declined by the issuer",
    "details": [],
    "request_id": "7d3f4a2e-..."
  }
}
```

The order is marked `failed` and the reserved inventory is released — the compensation path is real
production code, not a test-only branch.

Scenarios: `payment_declined`, `payment_timeout`, `payment_provider_error`,
`inventory_unavailable`, `service_timeout`, `internal_server_error`. See
[`docs/failure-simulation.md`](docs/failure-simulation.md).

---

## Configuration

Externalized via environment variables. Documented in [`.env.example`](.env.example) and
[`docs/configuration.md`](docs/configuration.md).

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/ecommerce.db` | SQLAlchemy DSN |
| `APP_ENV` | `development` | `development` \| `test` \| `production` |
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `RANDOM_SEED` | `42` | Default generator seed |
| `FAKE_FAILURE_ENABLED` | `false` | Master switch for failure simulation |
| `FAKE_FAILURE_RATE` | `0.0` | Randomized injection rate (`0.0` = off) |
| `FAKE_LATENCY_MS` | `0` | Artificial latency per request |
| `AUTH_ENABLED` | `true` | Enforce authentication and authorization |

Failure simulation is **off by default**. With it enabled and `FAKE_FAILURE_RATE=0.0`, only
deterministic `X-Fake-Failure` requests fail — so a functional test never loses a coin flip.

> ### The auth boundary is fake
>
> `AUTH_ENABLED=true` is the default everywhere, including development, and every route — including
> the administrative ones in `API.md` §44 — enforces it. The enforcement is real code on a real
> boundary, but the credentials are static fixtures in a local fake server, not a security control.
> Never point this at a network it does not own. Set `AUTH_ENABLED=false` only for tests that
> deliberately exercise the unauthenticated path.

---

## Project Structure

```text
ecommerce/
├── pyproject.toml
├── uv.lock
├── Makefile
├── alembic.ini
├── .env.example
├── README.md
├── CHANGELOG.md
│
├── .specify/memory/constitution.md    # binding engineering rules
│
├── specs/                             # all Spec Kit output
│   ├── 001-foundation/
│   ├── 002-product-catalog/
│   ├── 003-customers/
│   ├── 004-cart/
│   ├── 005-orders/
│   ├── 006-inventory/
│   ├── 007-payments/
│   ├── 008-fake-data-generator/      # high priority
│   ├── 009-failure-simulation/
│   ├── 010-authentication/
│   └── 011-observability/
│
├── docs/
├── data/ecommerce.db                  # dev database (git-ignored)
├── migrations/
├── src/ecommerce/                     # api / application / domain / infrastructure
├── scripts/
└── tests/{unit,integration,api}/
```

### Architecture

```text
API
 ↓
Application
 ↓
Domain          ← framework-free; no FastAPI, no SQLAlchemy
 ↑
Infrastructure
 ↓
SQLite / External Systems
```

Dependencies point inward. Bounded contexts: Product Catalog, Customer, Cart, Order, Inventory,
Payment. Full detail: [`docs/architecture.md`](docs/architecture.md).

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | What the system does and why |
| [`docs/plan.md`](docs/plan.md) | Implementation plan, phases, open conflicts |
| [`docs/architecture.md`](docs/architecture.md) | Layering, bounded contexts, repository pattern, transactions, fake providers |
| [`docs/API.md`](docs/API.md) | Endpoints, schemas, status codes, errors, pagination, auth |
| [`docs/database.md`](docs/database.md) | Tables, relationships, constraints, indexes, migrations, SQLite caveats |
| [`docs/generator.md`](docs/generator.md) | Fake-data generator: CLI, seed, profiles, reset, validation |
| [`docs/configuration.md`](docs/configuration.md) | Environment variables and per-environment behavior |
| [`docs/testing.md`](docs/testing.md) | Test layout, fixtures, determinism, failure tests |
| [`docs/failure-simulation.md`](docs/failure-simulation.md) | Failure scenarios and how to trigger them |
| [`docs/development.md`](docs/development.md) | Developer workflow and troubleshooting |
| [`specs/README.md`](specs/README.md) | Feature roadmap |
| [`CHANGELOG.md`](CHANGELOG.md) | Notable changes |
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | Binding engineering rules |

---

## Development Process

```text
Specification → Design → Implementation Plan → Implementation
              → Tests → Validation → Documentation
```

Each significant feature gets its own specification under `specs/`, produced with `/speckit.specify`,
`/speckit.plan`, and `/speckit.tasks`.

A feature is complete only when behavior is specified, business rules are documented, the
implementation is done, tests exist, API contracts are validated, migrations exist, error behavior
is defined, and documentation is updated. **An endpoint returning `200 OK` is not sufficient
evidence of completion.**

---

## Guiding Principle

> Does this make the fake e-commerce system more realistic, deterministic, testable, maintainable,
> or useful?

If not, the added complexity should be questioned before it is introduced.
