# Development Workflow — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.0, *Simple Local Development*

A developer goes from a clean checkout to a working populated server with a small number of
commands. Nobody inserts database rows by hand.

---

## 1. The Loop

```text
Install
   ↓
Migrate
   ↓
Generate data
   ↓
Run server
   ↓
Call API
   ↓
Run tests
```

```bash
uv sync
uv run alembic upgrade head
uv run python -m ecommerce.seed
uv run uvicorn ecommerce.main:app --reload
uv run pytest
```

Or via Make:

```bash
make install
make migrate
make seed
make run
make test
```

`make bootstrap` runs install → migrate → seed in one step.

---

## 2. Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12+ | Managed by `uv` |
| `uv` | latest | Package management, lockfile, venv |
| make | any | Convenience targets (optional — every target maps to a plain command) |

Verify:

```bash
uv --version
python --version
```

---

## 3. Setup

```bash
git clone <repo>
cd ecommerce
make install          # uv sync
cp .env.example .env  # optional; sensible defaults apply without it
```

`uv sync` creates the virtual environment and installs exactly what `uv.lock` pins. The lockfile is
committed and MUST be updated deliberately:

```bash
uv add <package>        # add a runtime dependency
uv add --dev <package>  # add a dev dependency
uv sync                 # re-sync after editing pyproject.toml
```

---

## 4. Database

```bash
make migrate           # uv run alembic upgrade head
make migrate-new m="create products"
make migration-status
make db-reset          # drop file + migrate + seed
```

| Task | Command |
|---|---|
| Apply migrations | `uv run alembic upgrade head` |
| Autogenerate a revision | `uv run alembic revision --autogenerate -m "message"` |
| Current revision | `uv run alembic current` |
| History | `uv run alembic history` |
| Reset everything | `make db-reset` |

Autogenerate output MUST be reviewed before applying — it cannot detect data migrations, server
defaults, or renames. Schema is never created by `Base.metadata.create_all()`.

The dev database is disposable: `data/ecommerce.db` is git-ignored and can be deleted at any time.

---

## 5. Fake Data

```bash
make seed                      # development profile
make seed-test                 # small, fast
make seed-large                # performance dataset
make seed-args SEED=42         # explicit seed
make reset                     # wipe generated rows + regenerate
```

```bash
uv run python -m ecommerce.seed --profile development --seed 42
uv run python -m ecommerce.seed --customers 10 --products 50 --orders 100 --seed 42
uv run python -m ecommerce.seed --reset
```

The generator does **not** require the HTTP server to be running. Full contract:
`docs/generator.md`.

---

## 6. Running the Server

```bash
make run           # uvicorn --reload
uv run uvicorn ecommerce.main:app --reload
```

| URL | Purpose |
|---|---|
| <http://127.0.0.1:8000/health> | Liveness |
| <http://127.0.0.1:8000/docs> | Interactive OpenAPI docs |
| <http://127.0.0.1:8000/openapi.json> | Machine-readable schema |
| <http://127.0.0.1:8000/api/v1/...> | Versioned API |

Useful variants:

```bash
uv run uvicorn ecommerce.main:app --reload --port 9000
uv run uvicorn ecommerce.main:app --log-level debug
```

---

## 7. Calling the API

```bash
BASE=http://127.0.0.1:8000

curl -s $BASE/health

curl -s "$BASE/api/v1/products?is_active=true&page=1&page_size=5"

curl -s -X POST $BASE/api/v1/customers \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev1@example.invalid","full_name":"Dev One"}'
```

End-to-end purchase:

```bash
BASE=http://127.0.0.1:8000
TOKEN=<fake token>

# 1. Pick a product
PRODUCT_ID=$(curl -s "$BASE/api/v1/products?is_active=true&page_size=1" | jq -r '.items[0].id')

# 2. Create a cart
CART=$(curl -s -X POST $BASE/api/v1/carts \
  -H "Authorization: Bearer $TOKEN" | jq -r '.id')

# 3. Add an item
curl -s -X POST $BASE/api/v1/carts/$CART/items \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"product_id":"'"$PRODUCT_ID"'","quantity":2}'

# 4. Checkout
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
```

Failure path:

```bash
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -H 'X-Fake-Failure: payment_declined' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
# {"error":{"code":"PAYMENT_DECLINED", ...}}   -> order failed, stock released
```

---

## 8. Tests

```bash
make test           # full suite
make test-unit      # fast inner loop, no database
uv run pytest tests/unit -q
uv run pytest -k "inventory" -v
```

Inner loop: `tests/unit` on every save; full suite before committing. See `docs/testing.md`.

---

## 9. Makefile Targets

| Target | Does |
|---|---|
| `make install` | `uv sync` |
| `make bootstrap` | install → migrate → seed |
| `make migrate` | `alembic upgrade head` |
| `make migrate-new m="..."` | autogenerate a revision |
| `make seed` | seed with the development profile |
| `make seed-test` | seed with the test profile |
| `make seed-large` | seed with the large profile |
| `make reset` | clear generated rows and regenerate |
| `make db-reset` | drop the DB file, migrate, seed |
| `make run` | `uvicorn --reload` |
| `make test` | full pytest suite |
| `make test-unit` | unit tests only |
| `make coverage` | tests with a coverage report |
| `make lint` | linter (if configured) |
| `make format` | formatter (if configured) |
| `make clean` | remove caches and the dev database |

Every target wraps a plain command, so the Makefile is a convenience, never a dependency.

---

## 10. Working on a Feature

```text
/speckit.specify  -> specs/NNN-slug/spec.md    (observable behavior)
/speckit.plan     -> specs/NNN-slug/plan.md    (design, layers, tradeoffs)
/speckit.tasks    -> specs/NNN-slug/tasks.md   (ordered work items)
   ... implement, test, validate ...
   ... update docs/ and CHANGELOG.md ...
```

All Speckit output lives under `specs/` — the single canonical location (constitution
*Speckit Development Process*; tooling resolves `SPECS_DIR` to it).

Definition of done — an endpoint returning `200 OK` is **not** sufficient:

```text
[ ] Specification exists
[ ] Architecture is defined
[ ] Domain rules are defined
[ ] Database changes have migrations
[ ] Implementation is complete
[ ] Unit tests exist
[ ] Integration tests exist where needed
[ ] API tests exist where needed
[ ] Error behavior is defined
[ ] Documentation is updated
```

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `no such table: products` | Migrations not applied | `make migrate` |
| Server starts, all lists empty | Database not seeded | `make seed` |
| `database is locked` | SQLite single-writer contention | Close other processes; shorten transactions; enable WAL |
| Foreign keys seem ignored | `PRAGMA foreign_keys` off by default | Set it on every connection |
| Generator output differs between runs | Unseeded randomness or wall-clock time | Use `--seed`; check for `datetime.now()` |
| Tests fail only in some order | Shared state between tests | Fix isolation, do not reorder |
| Tests modified my dev data | Test DB not separated | `APP_ENV=test` + dedicated `DATABASE_URL` |
| Simulated failure when not requested | `FAKE_FAILURE_*` misconfigured | Reset to defaults (`docs/configuration.md`) |
| `uv sync` fails on lockfile | `pyproject.toml` changed without re-lock | `uv sync` and commit `uv.lock` |
| 500 with an empty body | Unhandled exception | Check server logs for the real trace and request ID |

---

## 12. Conventions

* Type hints on all public functions and methods.
* Small, focused functions with a single responsibility.
* Explicit dependency injection; no service locators or global state.
* Business logic lives in the domain/application layers — **never** duplicated across endpoints.
* No magic values; named constants.
* Comments explain *why*, not *what*.
* Formatting/linting via configured tools (`make format`, `make lint`).

See `.specify/memory/constitution.md` for the binding rules.

---

## 13. Documentation Map

| Document | Contents |
|---|---|
| `README.md` | Entry point — quick start |
| `CHANGELOG.md` | Notable changes by version |
| `docs/PRD.md` | What the system does and why |
| `docs/plan.md` | Implementation plan, phases, open conflicts |
| `docs/architecture.md` | Layering, contexts, patterns |
| `docs/API.md` | HTTP contract |
| `docs/database.md` | Schema, constraints, SQLite caveats |
| `docs/generator.md` | Fake-data generator |
| `docs/configuration.md` | Environment variables |
| `docs/testing.md` | Test strategy |
| `docs/failure-simulation.md` | Failure scenarios |
| `docs/development.md` | This document |
| `specs/README.md` | Feature roadmap |
| `.specify/memory/constitution.md` | Binding engineering rules |
