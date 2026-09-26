# Architecture — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.0, *Speckit Development Process* principle
> (modular monolith, no unnecessary infrastructure).

This document describes **how** the system is structured. For **what** it does, see `docs/PRD.md`.

---

## 1. Layering

```text
FastAPI
   │
   ▼
API Layer
   │
   ▼
Application Layer
   │
   ▼
Domain Layer
   ▲
   │
Infrastructure Layer
   │
   ▼
SQLite / External Systems
```

Dependencies point **inward**. The domain sits at the center and depends on nothing.

```text
API
 │
 ▼
Application
 │
 ▼
Domain
 ▲
 │
Infrastructure
```

The Domain Layer MUST NOT import or depend on FastAPI, SQLAlchemy, HTTPX, Alembic, or any other
infrastructure or framework library. This is what makes the domain unit-testable with no database,
no HTTP client, and no event loop.

---

## 2. Layer Responsibilities

### 2.1 API Layer

Owns:

* HTTP routing and the `/api/v1` prefix
* Request parsing and response serialization
* HTTP status codes
* Dependency injection wiring
* Authentication boundaries (extracting the caller, not deciding policy)
* API-level validation via Pydantic v2 schemas

MUST NOT contain core business rules. A route that computes a total, validates stock, or decides
an order transition is in the wrong layer.

### 2.2 Application Layer

Owns:

* Use cases (one per meaningful business operation)
* Application workflows such as checkout
* Transaction boundaries
* Coordination between domain objects
* Repository interaction
* Application-level policies

Application services SHOULD represent meaningful business operations rather than merely wrapping
database operations. Expected use cases:

```text
CreateProduct
AddProductToCart
CheckoutCart
ReserveInventory
AuthorizePayment
CancelOrder
GenerateFakeData
```

The application layer coordinates domain behavior; it MUST NOT become a second domain model.

### 2.3 Domain Layer

Owns:

* Entities and value objects
* Business rules and invariants
* State transitions
* Domain exceptions
* Domain services where a rule spans entities

Framework-free. Pure Python plus the standard library. This is the most valuable part of the
codebase and the part most aggressively protected by unit tests.

### 2.4 Infrastructure Layer

Owns:

* SQLAlchemy models
* Database sessions and engine configuration
* Repository implementations
* External service simulations (fake payment provider, clock, ID generation)
* Persistence logic
* Infrastructure configuration

Infrastructure details MUST NOT leak into domain logic. A domain entity never sees a SQLAlchemy
`Session`, and never returns an ORM object.

---

## 3. Bounded Contexts

```text
Product Catalog  → Category, Product
Customer         → Customer
Cart             → Cart, CartItem
Order            → Order, OrderItem
Inventory        → Inventory
Payment          → Payment
```

Each context has clearly defined responsibilities:

| Context | Owns | Does not own |
|---|---|---|
| Product Catalog | Category, Product, pricing | Stock levels, cart contents |
| Customer | Customer identity, status, address | Orders' financial totals |
| Cart | Cart, CartItem, cart totals | Inventory reservation, order state |
| Order | Order, OrderItem, order lifecycle | Card data, stock levels |
| Inventory | Stock, reservations, releases | Pricing, payment |
| Payment | Payment, provider interaction | Order lifecycle decisions |

Cross-context collaboration happens in the **Application Layer** through explicit use cases — not
by reaching into another context's tables.

---

## 4. Module Layout

```text
src/ecommerce/
├── main.py                 # ASGI app factory
├── api/
│   ├── dependencies.py     # DI wiring: session, current user, services
│   ├── errors.py           # exception → error-envelope translation
│   └── v1/                 # routers grouped by bounded context
├── application/            # use cases, one package per context
├── domain/                 # entities, VOs, rules, exceptions (framework-free)
├── infrastructure/
│   ├── database/           # engine, session factory, base
│   ├── repositories/       # concrete repository implementations
│   └── external/           # fake payment provider, clock, IDs
├── config/
│   └── settings.py         # pydantic-settings
└── seed/                   # fake-data generator
    ├── __main__.py         # enables `python -m ecommerce.seed`
    ├── cli.py
    ├── generator.py
    ├── factories/
    └── profiles/
```

`tests/` mirrors the layering, split by test kind rather than by layer:

```text
tests/
├── unit/          # domain + application, no database
├── integration/   # repositories, SQLite, transactions, migrations
└── api/           # HTTP contract, workflows, failures, auth
```

---

## 5. Repository Pattern

Repositories isolate persistence from application services and expose **domain-oriented**
operations, not raw SQLAlchemy escape hatches.

```text
ProductRepository
CustomerRepository
CartRepository
OrderRepository
InventoryRepository
PaymentRepository
```

Design rules:

* One repository per aggregate root, not a single generic repository for the whole system.
* Repository interfaces live where the application layer consumes them; implementations live in
  `infrastructure/repositories/`.
* Repositories return domain objects or plain projections, never live ORM instances.
* Filtering, sorting, and pagination are named, intention-revealing methods — not a generic
  `find(where=...)` escape hatch.
* Business rules (e.g. "stock may not go negative") are enforced in the domain. A `CHECK`
  constraint is a backstop, not the primary rule.

---

## 6. Transactions and Consistency

Operations that modify multiple related records MUST define an explicit transaction boundary.
The application layer owns the boundary; the domain is unaware of it.

Checkout is the canonical multi-record operation:

```text
Checkout
 ├── Create order
 ├── Reserve inventory
 └── Create payment
```

On failure the system MUST explicitly choose one of:

1. **Rollback** — the whole operation is undone.
2. **Compensate** — a committed partial state is corrected by a compensating action.
3. **Remain failed** — the failure is persisted as a terminal state.

Partial state MUST NOT occur accidentally. The concrete choice per step is specified in
`specs/005-orders` and `specs/008-fake-data-generator`.

Because the fake provider is in-process, the dominant pattern is: *persist the order and its
failed state inside the transaction, then compensate inventory in a second step* — so that the
failure itself remains observable to a test.

---

## 7. Database Architecture

* SQLite is the default; the dev database is `data/ecommerce.db`.
* Schema is managed **only** by Alembic migrations. `Base.metadata.create_all()` MUST NOT be the
  primary schema mechanism, and the application MUST NOT mutate schema at startup.
* SQLAlchemy 2.x typed `DeclarativeBase` and `Mapped[...]`/`mapped_column(...)` style.
* Relationships, constraints, and indexes: see `docs/database.md`.
* SQLite-specific behavior that changes application-visible semantics is documented there.

---

## 8. External Systems and Fake Providers

External dependencies sit behind **ports** defined for the consuming layer, with **adapters** in
infrastructure. The domain never imports an adapter.

| Port | Fake adapter | Real-world counterpart |
|---|---|---|
| Payment gateway | `FakePaymentProvider` | Stripe / Adyen SDK |
| Clock | `SystemClock` / `FixedClock` | — (enables deterministic time in tests) |
| ID generation | `SequentialIdGenerator` | UUID/ULID service |

```text
Fake Payment Provider
   ↓  (swap adapter only)
External Payment Provider Adapter
```

Domain logic MUST NOT require major changes when an infrastructure implementation changes. Failure
simulation is a property of the fake adapters plus a middleware concern, never of the domain.

---

## 9. Determinism Strategy

Determinism is an architectural property, not a test convenience:

* All generator randomness flows through one explicitly seeded RNG instance.
* Time is injected via a clock port so time-dependent logic is testable without sleeping.
* IDs are generated through a port so fixtures are stable.
* Failure injection is deterministic by default; randomized injection is opt-in and separately
  controlled.
* `APP_ENV=test` never reads ambient developer configuration.

---

## 10. Extensibility

The architecture is designed so infrastructure can be swapped without touching the domain:

| Swap | Blast radius |
|---|---|
| SQLite → PostgreSQL | `infrastructure/database`, `alembic` config, DSN handling |
| Fake payment provider → real SDK | `infrastructure/external` only |
| In-process checkout → queued checkout | Application layer use case boundary |

`pyproject.toml` MUST NOT grow a second framework when the current stack can reasonably meet the
need. Every dependency needs a clear technical purpose.

---

## 11. Architectural Constraints (Non-Negotiable)

* Domain MUST NOT import FastAPI, SQLAlchemy, HTTPX, or Alembic.
* Dependencies point inward only.
* No microservices, message brokers, distributed systems, event sourcing, or CQRS without a
  concrete, documented requirement. The system is a **modular monolith**.
* Business logic MUST NOT be duplicated across endpoints.
* New abstractions MUST have a demonstrated purpose.
* Simple over clever; explicit over implicit; tested over over-engineered.
