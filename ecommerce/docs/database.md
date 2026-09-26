# Database — Fake E-Commerce Server

> **Status:** Draft — the schema is specified but not yet migrated.
> **Engine:** SQLite (default) · **Dev file:** `data/ecommerce.db`
> **Authority:** `.specify/memory/constitution.md` v1.1.0

---

## 1. Schema Management

* The schema is managed **exclusively** by Alembic migrations.
* `Base.metadata.create_all()` MUST NOT be the primary schema mechanism.
* The application MUST NOT create, alter, or drop schema at startup.
* Every persistent schema change MUST arrive as a reviewed Alembic revision.
* `uv.lock` and migration files are committed. The dev database file is **not**.

```bash
uv run alembic revision --autogenerate -m "create products"
uv run alembic upgrade head
```

Autogenerate output MUST be reviewed before it is applied — autogenerate cannot see data
migrations, server defaults, or renames.

---

## 2. Tables

```text
categories
products
customers
inventory
carts
cart_items
orders
order_items
payments
```

### 2.1 `categories`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `name` | TEXT | NOT NULL |
| `slug` | TEXT | NOT NULL, UNIQUE |
| `parent_id` | TEXT | FK → `categories.id`, NULL (self-referencing tree) |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

### 2.2 `products`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `sku` | TEXT | NOT NULL, UNIQUE |
| `name` | TEXT | NOT NULL |
| `description` | TEXT | NULL |
| `category_id` | TEXT | FK → `categories.id`, NOT NULL |
| `price_amount` | INTEGER | NOT NULL, `CHECK (price_amount >= 0)` — minor units |
| `currency` | TEXT | NOT NULL, ISO-4217, `CHECK (length(currency) = 3)` |
| `is_active` | BOOLEAN | NOT NULL, default `1` |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

Money is stored as an **integer count of minor units**. Floating point is never used for money.

### 2.3 `customers`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `email` | TEXT | NOT NULL, UNIQUE |
| `full_name` | TEXT | NOT NULL |
| `status` | TEXT | NOT NULL — `active` / `inactive` / `suspended` |
| `address_line1` | TEXT | NULL |
| `address_city` | TEXT | NULL |
| `address_postal_code` | TEXT | NULL |
| `address_country_code` | TEXT | NULL |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

### 2.4 `inventory`

| Column | Type | Constraints |
|---|---|---|
| `product_id` | TEXT (UUID) | PK **and** FK → `products.id` (1:1) |
| `quantity_available` | INTEGER | NOT NULL, default `0`, `CHECK (>= 0)` |
| `quantity_reserved` | INTEGER | NOT NULL, default `0`, `CHECK (>= 0)` |
| `updated_at` | TEXT/TS | NOT NULL |

One inventory row per product. The `CHECK` constraints are a **backstop**; the real rule
("quantity MUST NOT become negative") lives in the domain, because a constraint can only reject a
write, not explain or compensate for it.

### 2.5 `carts`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `customer_id` | TEXT | FK → `customers.id`, NOT NULL |
| `status` | TEXT | NOT NULL — `active` / `checked_out` / `abandoned` |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

### 2.6 `cart_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `cart_id` | TEXT | FK → `carts.id` **ON DELETE CASCADE**, NOT NULL |
| `product_id` | TEXT | FK → `products.id`, NOT NULL |
| `quantity` | INTEGER | NOT NULL, `CHECK (quantity > 0)` |
| `unit_price_amount` | INTEGER | NOT NULL, `CHECK (>= 0)` — snapshot at add time |
| `currency` | TEXT | NOT NULL |
| `created_at` | TEXT/TS | NOT NULL |

`UNIQUE (cart_id, product_id)` — a product appears at most once per cart; adding again increments
quantity.

### 2.7 `orders`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `customer_id` | TEXT | FK → `customers.id`, NOT NULL |
| `status` | TEXT | NOT NULL — `pending`/`confirmed`/`processing`/`shipped`/`delivered`/`cancelled`/`failed` |
| `total_amount` | INTEGER | NOT NULL, `CHECK (>= 0)` — derived, denormalized for query convenience |
| `currency` | TEXT | NOT NULL |
| `failure_reason` | TEXT | NULL — populated when `status = 'failed'` |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

`total_amount` is denormalized. It MUST always equal the sum of its `order_items.line_total`, and
that invariant is verified by integration tests and by the generator's post-generation validation.

### 2.8 `order_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `order_id` | TEXT | FK → `orders.id` **ON DELETE CASCADE**, NOT NULL |
| `product_id` | TEXT | FK → `products.id`, NOT NULL |
| `quantity` | INTEGER | NOT NULL, `CHECK (quantity > 0)` |
| `unit_price_amount` | INTEGER | NOT NULL, `CHECK (>= 0)` — **snapshot** |
| `line_total_amount` | INTEGER | NOT NULL, `CHECK (>= 0)` |
| `currency` | TEXT | NOT NULL |

Prices are snapshotted so later catalog price changes never rewrite order history.
`ON DELETE RESTRICT` (the default) applies to `products` — a product that appears in an order
cannot be hard-deleted.

### 2.9 `payments`

| Column | Type | Constraints |
|---|---|---|
| `id` | TEXT (UUID) | PK |
| `order_id` | TEXT | FK → `orders.id`, NOT NULL |
| `status` | TEXT | NOT NULL — `pending`/`authorized`/`captured`/`declined`/`failed`/`refunded` |
| `amount` | INTEGER | NOT NULL, `CHECK (>= 0)` |
| `currency` | TEXT | NOT NULL |
| `method` | TEXT | NOT NULL — synthetic only (e.g. `fake_card`) |
| `transaction_id` | TEXT | UNIQUE, synthetic (e.g. `faketxn_0001`) |
| `failure_reason` | TEXT | NULL |
| `created_at` | TEXT/TS | NOT NULL |
| `updated_at` | TEXT/TS | NOT NULL |

`UNIQUE (order_id)` — one payment per order, which keeps the order↔payment relation unambiguous.

---

## 3. Entity Relationships

```text
Customer
   │
   ├──< Cart
   │      └──< CartItem ──> Product
   │
   └──< Order
          ├──< OrderItem ──> Product
          └──1 Payment

Category
   └──< Product
              └──1 Inventory
```

Full foreign-key list:

```text
category.parent_id        -> categories.id
product.category_id       -> categories.id
inventory.product_id      -> products.id
cart.customer_id          -> customers.id
cart_item.cart_id         -> carts.id          (CASCADE)
cart_item.product_id      -> products.id
order.customer_id         -> customers.id
order_item.order_id       -> orders.id         (CASCADE)
order_item.product_id     -> products.id
payment.order_id          -> orders.id         (UNIQUE)
```

Every reference MUST point to an existing record. The generator MUST fail clearly rather than
silently create an orphan (constitution §16).

---

## 4. Constraints Strategy

| Rule | Enforced by | Backstop |
|---|---|---|
| Inventory never negative | Domain `Inventory.reserve/release` | `CHECK (quantity_*) >= 0` |
| Reservation fails when short | Domain | `409 INSUFFICIENT_INVENTORY` |
| Cart quantity > 0 | Domain | `CHECK (quantity > 0)` |
| Order has ≥ 1 item | Application (checkout) | Integration test |
| Order total = Σ line totals | Application + generator validation | Integration test |
| Valid state transitions | Domain transition table | `409 INVALID_*_TRANSITION` |
| Price never negative | Domain value object | `CHECK (price_amount >= 0)` |
| Payment ↔ order 1:1 | Application | `UNIQUE (order_id)` |

Business rules are enforced by **domain/application logic**. Constraints are a safety net, not the
primary mechanism. A `CHECK` can reject a write; it cannot explain, compensate, or be unit-tested
without a database.

---

## 5. Indexes

| Index | Table | Columns | Rationale |
|---|---|---|---|
| `ix_categories_slug` | categories | `slug` | Unique lookup; also serves the unique constraint |
| `ix_products_sku` | products | `sku` | Unique lookup |
| `ix_products_category_id` | products | `category_id` | Category listing/filtering |
| `ix_products_is_active` | products | `is_active` | Default catalog query filter |
| `ix_products_name` | products | `name` | Search / sort |
| `ix_customers_email` | customers | `email` | Unique lookup |
| `ix_carts_customer_id` | carts | `customer_id` | "My cart" lookup |
| `ix_cart_items_cart_id` | cart_items | `cart_id` | Item listing; also serves the unique constraint |
| `ix_orders_customer_id` | orders | `customer_id` | Customer order history |
| `ix_orders_status` | orders | `status` | Operational filtering by state |
| `ix_orders_created_at` | orders | `created_at` | Chronological paging |
| `ix_order_items_order_id` | order_items | `order_id` | Order detail; also serves cascade |
| `ix_payments_order_id` | payments | `order_id` | Order→payment lookup; also serves unique |
| `ix_payments_status` | payments | `status` | Reconciliation queries |

Index selection is driven by the queries in `docs/API.md` §7, not by guesswork. SQLite ignores an
index whose leading column is not constrained by the query, so extra indexes cost writes without
earning reads.

---

## 6. Transactions

* The **application layer** owns transaction boundaries. The domain is unaware of them.
* Read-only flows MAY run without an explicit transaction.
* Multi-record writes MUST be atomic or explicitly compensated.

Checkout touches `orders`, `order_items`, `inventory`, and `payments`. Its failure semantics are
specified in `docs/architecture.md` §6 and exercised by integration tests in
`specs/005-orders` / `specs/009-failure-simulation`.

SQLite's write model (single writer) is why optimistic checks on `inventory` matter — see §8.

---

## 7. Migration Strategy

* One logical change per revision; the message states the change (`create products`,
  `add order failure_reason`).
* Schema migrations and data migrations are separate, clearly labelled revisions.
* Destructive changes (drop/rename a column) require: a documented migration strategy, updated
  tests, updated docs, and a deliberate decision recorded in `CHANGELOG.md`.
* Every migration is expected to be reversible where practical (`downgrade()` implemented).
* Target production-like state is `alembic upgrade head`; the dev database is disposable and
  recreated via `make reset`.

---

## 8. SQLite-Specific Considerations

These behaviors affect application-visible semantics and MUST be respected:

| Behavior | Consequence for the application |
|---|---|
| **Single writer** | One write transaction at a time; concurrent writers get `SQLITE_BUSY` / "database is locked". Long transactions block everything. |
| **No `SERIALIZABLE` row-level locking** | Read-modify-write on `inventory` can interleave. Use an explicit `BEGIN IMMEDIATE` or a conditional `UPDATE ... WHERE quantity_available >= :n` and check `rowcount`. |
| **Foreign keys OFF by default** | `PRAGMA foreign_keys = ON` MUST be set on every connection, otherwise `ON DELETE CASCADE` and FK enforcement silently do nothing. |
| **Weak `DATETIME` type** | Store timestamps as ISO-8601 TEXT (sortable) or INTEGER epoch seconds — never Python `datetime` objects. |
| **Boolean is INTEGER** | `0`/`1`, not `true`/`false` literals. |
| **No native `BOOLEAN`/`ENUM`** | Use INTEGER + `CHECK`, or TEXT + `CHECK (col IN (...))`. |
| **No `RETURNING` before 3.35** | Feature-detect before relying on it. |
| **WAL recommended** | `PRAGMA journal_mode = WAL` greatly improves read-during-write behavior for a dev/test server. |
| **Foreign keys are not indexed automatically** | Manually index every FK column (see §5). |
| **Whole-file locking on backup** | Copy the file only when no writer is active, or use `sqlite3 .backup`. |

Money stays `INTEGER` minor units — SQLite has no exact decimal type, and REAL would introduce
floating-point rounding into financial totals.

---

## 9. Test Database

* Tests MUST use a **dedicated** SQLite database, separate from `data/ecommerce.db`.
* Recommended: one in-memory database per test session with a connection shared via
  `StaticPool`, or a temp file per test.
* Tests MUST NOT modify development data.
* The fake-data generator can populate a test database with small deterministic datasets — see
  `docs/generator.md` and `docs/testing.md`.

```text
data/ecommerce.db        # development — disposable, git-ignored
<temp>/test.db           # tests — per run, never committed
```

---

## 10. Reserved / Not Yet Implemented

Deferred until a requirement justifies them, per the *Simplicity* principle:

* Audit log table
* Outbox / event table (a transactional outbox would only be added alongside a real broker)
* Soft-delete columns
* Multi-currency conversion tables
* Full-text search index (FTS5) — plain `LIKE` is sufficient at current scale
