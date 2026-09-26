# Testing — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.0, *Testability and Isolation*

Testing is mandatory. This document defines the strategy, layout, and guarantees.

---

## 1. Layout

```text
tests/
├── unit/          # domain + application logic, no database
├── integration/   # repositories, SQLite, transactions, migrations
└── api/           # HTTP contract, workflows, failures, auth
```

Plus shared fixtures:

```text
tests/
├── conftest.py        # session-wide fixtures, settings overrides
├── factories/         # test data builders (non-generator)
└── helpers/           # request helpers, assertions, clock control
```

Unit tests SHOULD avoid the database wherever practical. When a unit test needs persistence, it
has crossed into `integration/` — that is a signal, not a technicality.

---

## 2. Test Database

* Tests MUST use a **dedicated** SQLite database.
* Automated tests MUST NOT modify development data.
* Tests MUST NOT depend on execution order.

Recommended approaches:

| Approach | Trade-off |
|---|---|
| In-memory + `StaticPool` shared connection | Fastest; must share one connection so the schema survives |
| Temp file per test | Realistic file semantics; slower, needs cleanup |
| Temp file per session | Faster; requires truncating tables between tests |

```text
data/ecommerce.db      # development — never touched by tests
./.tmp/test.db         # tests — per run, git-ignored
```

The `APP_ENV=test` + dev-database-URL guard in `docs/configuration.md` §6 enforces this at
startup, so a misconfigured run fails loudly instead of damaging local data.

Each test starts from a known state — either a fresh schema or a truncate-and-reseed. Prefer
**function-scoped** isolation; fall back to explicit truncation when the setup cost dominates.

---

## 3. Fixtures

Typical fixture set:

| Fixture | Scope | Purpose |
|---|---|---|
| `settings` / `test_settings` | session | Settings with `APP_ENV=test`, fixed seed, failure sim off |
| `engine` / `session` | function | Engine + session bound to the test database |
| `db_schema` | session | Apply migrations (or create schema) once |
| `clean_tables` | function | Truncate all tables between tests |
| `customer_factory` | function | Build a synthetic customer |
| `product_factory` | function | Build a synthetic product + inventory |
| `cart_factory` | function | Build a cart with items |
| `order_factory` | function | Build an order in a chosen state |
| `api_client` | function | HTTPX/ASGI client wired to the test app |
| `auth_headers` | function | `Authorization` headers per role |
| `seeded_dataset` | function | Deterministic dataset from the fake-data generator |

Factories and the fake-data generator solve different problems: factories build the **one**
record a test needs; the generator builds a **realistic** dataset for integration and API tests.
Tests should prefer factories for precision.

---

## 4. Test Data Generator

The generator is reusable by tests and MUST remain deterministic.

```python
generate_dataset(session, customers=1, products=1, orders=1, seed=42)
generate_dataset(session, customers=10, products=50, orders=100, seed=42)
```

Guarantees:

* Small controlled datasets — as small as 1 customer / 1 product / 1 order.
* Fixed seed → identical dataset every run.
* No network access, no wall-clock dependence, no use of the dev database.
* Invalid datasets only when a test **explicitly** requests them for validation testing. Invalid
  data is never produced by default.

Generator test coverage (`integration/`):

```text
Deterministic output      same seed twice -> equal
Record counts             actual == requested
Foreign keys              every FK resolves
Orphans                   none
Inventory consistency     quantities never negative
Order totals              total == SUM(line_total)
Payment relationships     every payment -> existing order
Reset                     clears generated rows, keeps schema
Profiles                  test/development/large apply documented defaults
```

---

## 5. Deterministic Tests

Tests MUST NOT depend on uncontrolled randomness or on the wall clock.

| Source of nondeterminism | Control |
|---|---|
| Random data | Seeded RNG via the generator; factories for single records |
| Time | Injected `Clock` port; `FAKE_CLOCK` sets a fixed instant |
| IDs | Generator port (`SequentialIdGenerator`) or explicit fixtures |
| Dict/set ordering | Assert on sets, never on iteration order |
| Concurrency | Deterministic failure injection, not timing races |
| Test order | Isolation, not incidental ordering |

```python
def test_inventory_never_goes_negative():
    inv = Inventory(available=5, reserved=0)
    with pytest.raises(InsufficientInventory):
        inv.reserve(6)          # pure domain — no database, no clock, no randomness
```

If a unit test needs a database, a sleep, or an unseeded RNG, that is a design smell in the
production code, not a test problem.

---

## 6. Unit Tests (`tests/unit/`)

Cover:

```text
Domain rules            inventory non-negativity, cart quantity > 0
State transitions      order + payment transition tables (valid AND invalid)
Calculations           line totals, order totals, cart subtotals
Validation             value objects, money, quantities, enumerated states
Application services   use cases with faked repositories
```

Rules:

* No database, no HTTP, no filesystem.
* Fast — the whole unit tier should run in seconds.
* Every state transition is tested in **both** directions: allowed proceeds, disallowed raises.
* Business rules are asserted through the domain API, never by inspecting storage.

---

## 7. Integration Tests (`tests/integration/`)

Cover:

```text
Repositories            CRUD, filtering, pagination, constraints
SQLite persistence      round-trips, types, NULL handling
Transactions            commit, rollback, multi-record atomicity
Database relationships  cascades, FK enforcement, RESTRICT behavior
Migrations              upgrade head on an empty DB; schema matches models
Checkout                happy path + compensation path
Generator               §4 above
```

Notes:

* Foreign-key enforcement tests must confirm `PRAGMA foreign_keys = ON` is actually applied
  (SQLite disables FKs by default — see `docs/database.md` §8).
* Concurrency-related inventory tests SHOULD use SQLite's real locking behavior rather than
  mocking it, since that is the behavior the application must survive.

---

## 8. API Tests (`tests/api/`)

Cover:

```text
Status codes            200/201/204/400/401/403/404/409/422/500
Request validation      missing fields, bad enums, bad quantities, bad money
Response schemas        shape and types match the documented contract
Authentication          missing/invalid/expired credentials
Authorization           cross-customer access denied; admin access allowed
Error responses         envelope shape, stable codes, no internal leakage
Workflows               browse -> cart -> checkout -> order
Failure scenarios       §9 below
```

Use an in-process ASGI client so tests exercise routing, DI, validation, and serialization without
a socket.

Minimum workflow test — the spine of the system:

```text
1. GET  /api/v1/products                -> 200, list shape correct
2. POST /api/v1/carts                   -> 201
3. POST /api/v1/carts/{id}/items        -> 201
4. POST /api/v1/checkout                -> 201, order created
5. GET  /api/v1/orders/{id}             -> 200, total == sum(items)
6. GET  /api/v1/orders/{id}/payment     -> 200, authorized
7. Verify inventory was reserved.
```

---

## 9. Failure Scenario Tests

Every deterministic failure scenario MUST have coverage asserting **both** the error response and
the resulting system state — a failure that leaves corrupt state is worse than no failure at all.

| Scenario | Assert response | Assert state |
|---|---|---|
| `payment_declined` | `402 PAYMENT_DECLINED` | Order `failed`; inventory released |
| `payment_timeout` | `504` / timeout | Order `failed`; inventory released |
| `payment_provider_error` | `502` | Order `failed`; inventory released |
| `inventory_unavailable` | `409 INSUFFICIENT_INVENTORY` | No order created; stock unchanged |
| `service_timeout` | `504` | No partial writes |
| `internal_server_error` | `500` | No internal detail leaked |

The `payment_declined` case is the important one: it proves compensation works. The test MUST assert
that reserved stock was returned to available, not merely that an error was raised.

See `docs/failure-simulation.md`.

---

## 10. Running Tests

```bash
uv run pytest                      # everything
uv run pytest tests/unit           # unit only (fast loop)
uv run pytest tests/integration    # database layer
uv run pytest tests/api            # HTTP layer
uv run pytest -k "inventory"       # by keyword
uv run pytest -x -q                # stop at first failure, quiet
uv run pytest --lf                 # last failures only
```

Recommended inner loop: `tests/unit` on every save, the full suite before committing.

```bash
make test           # full suite
make test-unit      # fast loop
make coverage       # with coverage report
```

---

## 11. Coverage Expectations

There is no numeric coverage target — a number encourages gaming it. What is required:

* Every significant business rule SHOULD have automated coverage.
* Every state transition MUST be tested in both directions.
* Every deterministic failure scenario MUST be tested.
* Every documented error code SHOULD be reachable from at least one test.

Coverage is evidence, not the goal. An uncovered *invariant* is a defect; an uncovered trivial
getter is not.

---

## 12. Isolation Rules

| Rule | Reason |
|---|---|
| No shared mutable state between tests | Order independence |
| Dedicated test database | Protects development data |
| Fixed seed everywhere | Reproducibility |
| Injected clock, never `datetime.now()` | Determinism |
| Fresh transaction or truncation per test | No leakage |
| No reliance on test execution order | Parallelizable, debuggable |

A test that passes only when run in a particular order is a broken test, not a fragile suite.

---

## 13. Related

* `docs/generator.md` — generator contract used by fixtures
* `docs/database.md` — schema and SQLite caveats that affect tests
* `docs/failure-simulation.md` — scenario definitions
* `docs/architecture.md` — what each layer is responsible for, and therefore what to test
* `docs/development.md` — the daily test loop
