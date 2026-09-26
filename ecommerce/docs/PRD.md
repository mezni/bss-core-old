# Product Requirements Document — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.1
> **Scope:** What the system must do, and why. Implementation detail is out of scope here — see
> `docs/architecture.md`, `docs/API.md`, `docs/database.md`.

---

## 1. Purpose

The Fake E-Commerce Server is a realistic, deterministic, extensible e-commerce backend used only
with synthetic data. It exists to serve:

* Local development
* API integration testing
* Backend engineering practice
* Client application development
* Agent and tool-calling experiments
* Failure and resilience testing
* Learning modern Python backend architecture

The system MUST behave like a realistic e-commerce backend while never touching real customers,
real payment credentials, or real personal information.

The system prioritizes, in order:

1. Correct domain behavior
2. Explicit business rules
3. Deterministic and reproducible behavior
4. Testability
5. Clear architectural boundaries
6. Realistic API behavior
7. Simple local development
8. Extensibility

---

## 2. Users and Roles

The system models three roles. Roles MUST be introduced only where they add meaningful
functionality.

| Role | Purpose | Representative capabilities |
|---|---|---|
| `customer` | The shopper | Browse catalog, manage own cart, check out, view own orders |
| `admin` | Store operator | Manage products/categories/inventory, view all orders, inspect payments |
| `service` | Machine caller | Programmatic checkout, bulk reads, deterministic failure-driven tests |

A shopper identity MUST NOT be able to read or mutate another shopper's cart, orders, or profile.
Administrative access MUST be explicit, not implied by role inheritance.

---

## 3. Functional Requirements

### 3.1 Users

* A visitor can browse the product catalog without authenticating.
* A customer can register, view and update their own profile, and deactivate their account.
* A customer can view only their own orders, carts, and payments.
* An administrator can view and manage any customer record.

### 3.2 Products

* The system MUST support categories and products, where a product belongs to a category.
* A product MUST have a name, description, price, SKU, category, and active/inactive status.
* Product prices MUST NOT be negative.
* A shopper can list products with filtering, searching, and pagination.
* An administrator can create, update, and deactivate products.
* Deactivating a product MUST NOT delete history that already references it.

### 3.3 Carts

* A cart belongs to exactly one customer.
* A cart contains zero or more cart items; each item references one product and a quantity.
* Cart quantities MUST be greater than zero.
* Cart items MUST reference existing products.
* A cart's totals MUST be derived from valid product pricing.
* A customer can add a product, update a quantity, remove a product, and clear the cart.
* The server MUST recompute all totals; client-supplied totals MUST be ignored.

### 3.4 Inventory

* Every product has inventory with an available quantity and a reserved quantity.
* Inventory quantities MUST NOT become negative.
* Reserving stock MUST fail when insufficient stock is available.
* Releasing stock MUST NOT produce invalid quantities.
* Customers and administrators can check availability for a product.

### 3.5 Checkout

Checkout is the central workflow and MUST be implemented as an explicit use case, not a
collection of unrelated endpoint calls.

```text
Browse products
      ↓
Add product to cart
      ↓
Update cart
      ↓
Checkout
      ↓
Reserve inventory
      ↓
Create order
      ↓
Authorize payment
      ↓
Confirm order
```

Failure paths MUST also be modeled:

```text
Checkout
   ↓
Inventory unavailable
   ↓
Checkout rejected
```

```text
Checkout
   ↓
Inventory reserved
   ↓
Payment declined
   ↓
Inventory released
   ↓
Order marked failed
```

An order MUST contain at least one item. Order totals MUST be calculated from order items.
Partial state MUST NOT occur accidentally.

### 3.6 Orders

* An order belongs to exactly one customer and contains one or more order items.
* Each order item references a product and a positive quantity.
* Orders MUST have an explicit lifecycle: `pending`, `confirmed`, `processing`, `shipped`,
  `delivered`, `cancelled`, `failed`.
* Invalid state transitions MUST be rejected with a clear error.
* Cancelled orders MUST follow valid transitions only.

### 3.7 Payments

* A payment references exactly one order.
* Payment lifecycle: `pending`, `authorized`, `captured`, `declined`, `failed`, `refunded`.
* Payment state transitions MUST be explicit.
* A failed payment MUST NOT silently become successful.
* All payment data MUST be synthetic. The server MUST NOT process real payment credentials.
* Payment amounts MUST correspond to their order totals where applicable.

---

## 4. Fake-Data Generation

The generator is a first-class capability, not an ad-hoc collection of SQL statements.

* It MUST produce realistic, synthetic, internally consistent e-commerce data.
* It MUST support Categories, Products, Inventory, Customers, Carts, Cart Items, Orders, Order
  Items, and Payments.
* It MUST satisfy every foreign-key relationship and MUST NOT create orphan records.
* It MUST respect application business rules, reusing domain/application services where that
  preserves invariants.
* It MUST be configurable by seed, profile, and dataset size.
* It MUST be executable independently of the FastAPI server.
* It MUST be reusable by automated tests with small, deterministic datasets.
* Invalid datasets MAY be supported for validation testing, but MUST never be produced by
  default.

Full contract: `docs/generator.md`.

---

## 5. Failure Simulation

Failure simulation is a first-class capability, not a side effect.

The system MUST support simulated:

* HTTP 4xx failures
* HTTP 5xx failures
* Payment declines
* Inventory conflicts
* Artificial latency
* Timeouts
* External-service failures
* Temporary failures
* Configurable failure rates

Failure simulation MUST be controlled by configuration or explicit test mechanisms, MUST NOT
affect normal operation unexpectedly, and MUST be deterministically triggerable.

Initial scenarios: `payment_declined`, `payment_timeout`, `payment_provider_error`,
`inventory_unavailable`, `service_timeout`, `internal_server_error`.

Full contract: `docs/failure-simulation.md`.

---

## 6. Non-Functional Requirements

### 6.1 Determinism

* The same seed, generator configuration, and application version produce equivalent data.
* Tests MUST NOT depend on uncontrolled randomness.
* The same failure request produces the same failure behavior.

### 6.2 Testability

* The test suite is organized as `tests/unit`, `tests/integration`, `tests/api`.
* Tests are isolated, order-independent, and use a dedicated SQLite test database.
* Automated tests MUST NOT modify development data.
* Every significant business rule SHOULD have automated coverage.

### 6.3 API Behavior

* All public routes are versioned under `/api/v1/`.
* The API follows HTTP semantics and uses meaningful status codes.
* Request and response models use explicit Pydantic schemas; database models are not public
  schemas.
* Errors use one consistent envelope with stable codes.

### 6.4 Persistence

* SQLite is the default database; the dev database lives at `data/ecommerce.db`.
* Schema is managed through Alembic migrations, not `Base.metadata.create_all()`.
* Operations touching multiple records define explicit transaction boundaries.

### 6.5 Security

* All input is validated; database access is parameterized to prevent SQL injection.
* Authentication and authorization boundaries are realistic and separate from business logic.
* Sensitive data is never logged, and totals are never trusted from clients.
* No real payment credentials or personal data are ever processed.

### 6.6 Observability

* Logs include request ID, method, path, status, duration, domain events, and errors.
* `GET /health` is always available; a readiness endpoint may be added later.

### 6.7 Local Development

* A new developer reaches a populated, running server with a small number of commands.
* The generator is part of the standard workflow; manual row insertion is never required.

---

## 7. Out of Scope

The following are explicitly excluded until a concrete requirement justifies them:

* Real payment processing or any real financial data
* Real customer data of any kind
* Microservices, message brokers, distributed systems
* Event sourcing, CQRS
* Frontend / UI application
* Multi-tenant support
* Real email/SMS delivery

The system remains a modular monolith.

---

## 8. Open Questions

* Whether a readiness endpoint is required (constitution says it *may* be added).
* Whether basic metrics are justified (constitution says only "if justified").
* Whether `checkout` will eventually warrant its own feature spec, or stays folded into
  `005-orders`. Currently folded in — see `docs/plan.md` §30.

Resolved:

* Spec feature decomposition — **11 features, generator at `008`**. See `docs/plan.md` §30.
