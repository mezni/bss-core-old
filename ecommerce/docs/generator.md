# Fake-Data Generator — Fake E-Commerce Server

> **Status:** Draft — highest-priority feature (`specs/008-fake-data-generator`).
> **Authority:** `.specify/memory/constitution.md` v1.1.0

The generator is a **first-class project capability**, not an ad-hoc collection of SQL statements.
It is part of the standard developer workflow: nobody should ever need to hand-insert rows to get a
useful environment.

---

## 1. What It Does

Generates realistic, synthetic, internally consistent e-commerce data:

```text
Generator
├── Categories
├── Products
├── Inventory
├── Customers
├── Carts
├── Cart Items
├── Orders
├── Order Items
└── Payments
```

It MUST NOT create accidental orphan records, MUST respect application business rules, and MUST
behave deterministically for a given seed.

**Never generated:** real customer information, real payment credentials, real personal
information, real authentication secrets. All identities use reserved domains (e.g.
`example.invalid`) and synthetic tokens.

---

## 2. Running It

The generator MUST be executable independently of the FastAPI server. The HTTP server does not
need to be running.

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
```

```bash
uv run python -m ecommerce.seed --reset
```

Equivalent via Make:

```bash
make seed          # default profile
make seed-test     # small, fast profile
make reset         # wipe + regenerate
```

---

## 3. CLI Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `--seed` | int | `RANDOM_SEED` env, else `42` | Seeds the explicit RNG |
| `--profile` | choice | *(none)* | `test`, `development`, `large` |
| `--customers` | int | profile default | Number of customers |
| `--products` | int | profile default | Number of products |
| `--categories` | int | profile default | Number of categories |
| `--orders` | int | profile default | Number of orders |
| `--reset` | flag | off | Remove generated records first |
| `--validate/--no-validate` | flag | validate on | Post-generation validation (§7) |
| `--quiet` | flag | off | Suppress the summary |
| `--output` | choice | `text` | `text` or `json` for the summary |

Explicit flags override profile values. The effective configuration is always printed in the
summary so a dataset is reproducible from the command line alone.

Precedence: **explicit flag > profile > documented default**.

---

## 4. Profiles

| Profile | Categories | Products | Customers | Orders | Use case |
|---|---|---|---|---|---|
| `test` | 5 | 20 | 10 | 25 | Fast unit/API fixtures |
| `development` | 12 | 200 | 50 | 300 | Normal local development (**default**) |
| `large` | 40 | 5,000 | 2,000 | 20,000 | Performance / load testing |

A minimal fixture is also expressible without a profile:

```text
1 customer, 1 product, 1 order
```

and a small realistic one:

```text
10 customers, 50 products, 100 orders
```

> Defaults documented here are normative. If they change, this table and `CHANGELOG.md` MUST be
> updated in the same commit.

---

## 5. Determinism

* All randomness flows through **one explicitly seeded RNG instance** (`random.Random(seed)`).
  No module-level `random.*` calls, no `uuid4()`, no `datetime.now()` in generation code.
* The same **seed + configuration + application version + database state** produces equivalent
  data.
* Time values are drawn relative to a configurable anchor instant, not the wall clock, so a
  dataset generated today and tomorrow is identical.
* IDs are drawn from a seeded sequence, not random UUIDs, so fixtures are stable across runs.
* Tests MUST NOT depend on uncontrolled randomness.

```bash
uv run python -m ecommerce.seed --seed 42 --output json > a.json
uv run python -m ecommerce.seed --seed 42 --output json > b.json
diff a.json b.json   # must be identical
```

Because the generator version participates in reproducibility, a summary records the application
version. Regenerating with a different version MAY legitimately differ.

---

## 6. Generation Order

Entities are generated in dependency order. Foreign-key dependencies MUST be satisfied before
dependents are created.

```text
1. Categories      no dependencies
2. Products        -> categories
3. Inventory       -> products
4. Customers       no dependencies
5. Carts           -> customers
6. Cart Items      -> carts, products
7. Orders          -> customers
8. Order Items     -> orders, products
9. Payments        -> orders
```

```text
Customer
   │
   ├── Cart
   │     └── CartItem ──> Product
   │
   └── Order
         ├── OrderItem ──> Product
         └── Payment

Product
   └── Inventory
```

The sequence MAY change when domain dependencies require it, but the invariant is fixed: **no
record is created before everything it references exists.**

---

## 7. Validation

After generation the system SHOULD validate, and by default does:

```text
Fake E-Commerce Data Generator

Seed:       42
Profile:    development
Customers:  50
Products:   200
Orders:     300
Payments:   300

Validation:
✓ Record counts
✓ Foreign keys
✓ Inventory consistency
✓ Order totals
✓ Payment relationships
✓ Entity states

Generation completed successfully.
```

Checks performed:

| Check | Assertion |
|---|---|
| Record counts | Actual rows match requested configuration |
| Foreign keys | Every FK resolves to an existing row |
| Orphans | No record points at a missing parent |
| Inventory | `quantity_available >= 0`, `quantity_reserved >= 0` |
| Order totals | `orders.total_amount == SUM(order_items.line_total)` for every order |
| Order contents | Every order has ≥ 1 item |
| Payments | Every payment references an existing order; amounts match order totals |
| State coherence | Completed orders have valid payment states; cancelled orders follow valid transitions |
| Prices | No negative prices or amounts |

If a relationship cannot be established, the generator **fails clearly** rather than writing a
partial record.

---

## 8. Realistic Data

Records SHOULD resemble plausible e-commerce data, with a **realistic distribution of states**
rather than every record being identical.

### Products

* Synthetic names and descriptions composed from adjective + material + noun patterns
* SKU: `<CATEGORY-PREFIX>-<NNNN>` (e.g. `AUD-0001`)
* Category assignment (some categories heavier than others)
* Prices drawn from a category-appropriate range, in integer minor units
* Active/inactive status — a minority inactive

### Customers

* Synthetic names
* Synthetic emails on a reserved domain: `customer<N>@example.invalid`
* Synthetic addresses where required
* Status distribution: mostly `active`, some `inactive`/`suspended`

### Orders

* 1–5 items per order
* Statuses spread across the lifecycle, weighted toward recent `confirmed`/`shipped`
* Order dates spread over a configurable window, consistent with status
* Totals computed from the actual order items
* Customers and products drawn from the already-generated sets

### Payments

* Status consistent with the parent order
* Amount equal to the order total
* Payment method from a synthetic set
* Transaction ID: `faketxn_<NNNN>`

### Carts

* A realistic minority of customers have an active cart
* Cart items reference real products with positive quantities

---

## 9. Reset

Reset MUST be explicit and MUST NOT delete unrelated data.

```bash
uv run python -m ecommerce.seed --reset
```

A development reset MAY:

1. Remove generated records.
2. **Preserve the database schema.**
3. Recreate the synthetic dataset.
4. Validate generated relationships.

Implementation notes:

* Deletion follows FK dependency order (children before parents), or is scoped to generated rows
  only.
* Reset does **not** run `alembic downgrade` and does **not** drop the schema.
* To rebuild the schema itself, use `make reset` (drop file + migrate + seed) — a separate,
  explicit action.
* Rows that the generator did not create are left alone. A marker column or a dedicated schema
  scope identifies generated data when partial reset is requested.

---

## 10. Transactions

Generation occurs inside an appropriate transaction:

```text
Begin transaction
       ↓
Generate data
       ↓
Validate data
       ↓
Commit
```

On failure:

```text
Rollback
```

The generator MUST NOT intentionally leave a partially populated database after a failed run,
unless explicitly configured to. Validation happens **inside** the transaction, before commit, so
an invariant violation rolls the whole dataset back rather than committing a broken one.

---

## 11. Test Data Generation

The generator is reusable by automated tests and MUST remain deterministic.

```python
# tests/conftest.py — illustrative shape, not implemented yet
generate_dataset(session, customers=1, products=1, orders=1, seed=42)
generate_dataset(session, customers=10, products=50, orders=100, seed=42)
```

Guarantees for test use:

* Small, controlled datasets (as small as 1/1/1).
* Fixed seed → identical dataset every run.
* No network access, no wall-clock dependence, no reliance on the dev database.
* Invalid datasets MAY be generated **only** when a test explicitly requests them (for validation
  testing). Invalid data MUST never be produced by default.

See `docs/testing.md` for fixture wiring.

---

## 12. Architecture

```text
src/ecommerce/seed/
├── __init__.py
├── __main__.py        # enables `python -m ecommerce.seed`
├── cli.py             # argument parsing, summary output
├── config.py          # GeneratorConfig + profiles
├── generator.py       # orchestration, transactions, validation
├── rng.py             # seeded RNG + id/time sources
├── factories/         # one per entity
│   ├── category.py
│   ├── product.py
│   ├── inventory.py
│   ├── customer.py
│   ├── cart.py
│   ├── order.py
│   └── payment.py
└── profiles/
    ├── test.py
    ├── development.py
    └── large.py
```

**Reuse domain and application services when doing so preserves business invariants.** Where a
generated record must satisfy a rule the domain already enforces (order totals, inventory
non-negativity, valid state transitions), the generator calls the same code path the API calls
rather than reimplementing the rule. Duplicated rules drift, and the generator would then be able
to produce data the API itself would reject.

Fast, purely synthetic fields (names, descriptions, emails) MAY be produced directly, since no
business rule governs them.

---

## 13. Failure Behavior

| Situation | Behavior |
|---|---|
| Requested relationship cannot be satisfied | Fail with a clear message naming the entity and the missing reference |
| Invariant violated during generation | Roll back, report which invariant and which records |
| Config invalid (e.g. negative counts) | Reject before touching the database |
| Database missing / not migrated | Fail with a pointer to `make migrate` |
| Unknown profile | List valid profiles and exit non-zero |
| Already-seeded database without `--reset` | Refuse, and tell the user to pass `--reset` |

Exit code `0` on success, non-zero on any failure — so it is usable in CI and shell pipelines.

---

## 14. Related

* `docs/database.md` — tables and constraints the generator must satisfy
* `docs/testing.md` — how tests consume the generator
* `docs/configuration.md` — `RANDOM_SEED` and friends
* `docs/development.md` — `make seed` and the daily loop
* `specs/008-fake-data-generator` — the feature specification
