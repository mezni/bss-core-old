# Session Handoff

_Last updated: 2026-09-20_

## Project

**telco_si** — Production-oriented Rust BSS/OSS platform.
Stack: Actix Web + Tokio + SQLx + SQLite, organized with Domain-Driven Design in a
monorepo (`/home/dali/WORK/utils`, remote `git@github.com:mezni/utils.git`).
`telco_si/` is a subdirectory of that monorepo (NOT its own git repo).

## Goal / working agreement

Build the platform **incrementally**. The user dictates each step and writes the
code themselves in a step-by-step fashion. The assistant:
- Does **not** write application code proactively.
- Explains *why* / DDD concepts when asked.
- Can review code, run builds/tests, and verify.

## Current state (this session)

- **Runtime/API (0.0.x)** — implemented and working:
  - Actix Web server + `GET /health` returning `{"status": "ok"}`.
  - Config loader (`AppConfig` from `APP_HOST` / `APP_PORT` / `DATABASE_URL`).
  - SQLx 0.9 + SQLite pool with `create_if_missing(true)`, WAL, foreign keys,
    `max_connections(10)`; `SELECT 1` verification before binding; migrations
    run on startup. Deps: actix-web, tokio, sqlx, anyhow, async-trait,
    thiserror, tracing, tracing-subscriber, uuid, chrono, serde.
- **Domain layer — Subscriber context** — implemented and tested:
  - `src/domain/subscriber/error.rs` — `SubscriberError` (thiserror):
    `AlreadySuspended`, `AlreadyActive`, `Terminated`, `InvalidTermination`,
    `NegativeBalance`, `InvalidAccountNumber`.
  - `src/domain/subscriber/value_objects.rs` — `SubscriberStatus`,
    `SubscriberId` (UUID v4, `new()` / `from_uuid()`), `AccountNumber`
    (non-empty validation), `Money` (`zero()` / `from_cents()` rejects
    negative via `NegativeBalance` / `cents()` / `add()`).
  - `src/domain/subscriber/entity.rs` — `Subscriber` aggregate: `new()`
    (starts Active, zero balance), `suspend()` / `activate()` / `terminate()`
    state transitions, `reconstitute()` for DB reads, getters.
- **Application layer — Subscriber context**:
  - `src/application/error.rs` — `ApplicationError` (`SubscriberNotFound`,
    `AccountNumberAlreadyExists`, `InvalidRequest`, `InvalidSubscriberState`,
    `Infrastructure`) + `ApplicationResult<T>`.
  - `src/application/subscriber/repository.rs` — `SubscriberRepository` port
    (`create`, `find_by_id`, `find_by_account_number`, `update`).
  - `src/application/subscriber/service.rs` — `SubscriberService<R>` use cases:
    `create` (validates account number, rejects duplicates), `get`,
    `suspend` / `activate` / `terminate` (load → transition → persist).
- **Infrastructure layer**:
  - `src/infrastructure/persistence/subscriber_repository.rs` —
    `SqliteSubscriberRepository` (SQLx) implementing the port; `#[derive(Clone)]`.
  - `migrations/` — `initial_schema.sql` + `create_subscribers.sql`
    (`subscribers` table with status/balance CHECKs, unique account_number,
    index on status).
- **Interfaces layer (HTTP)**:
  - `src/interfaces/http/dto.rs` — `CreateSubscriberRequest`, `SubscriberResponse`.
  - `src/interfaces/http/subscriber.rs` — handlers + `configure()`:
    `POST /subscribers`, `GET /subscribers/{id}`,
    `POST /subscribers/{id}/suspend|activate|terminate`.
  - `src/interfaces/http/error.rs` — `ResponseError for ApplicationError`
    (404 / 409 / 400 / 409 / 500 generic).
- **Library crate + tests**:
  - `src/lib.rs` exposes all modules so integration tests can import `telco_si`.
  - `tests/subscriber_integration.rs` — 4 tests on in-memory SQLite
    (`max_connections(1)` + migrations): create/get round trip, duplicate
    account rejected, persisted lifecycle, `POST /subscribers` through HTTP → 201.
- **Tests** — `cargo test`: domain unit tests (15) + integration tests (4).
- **Git** — repo root is the monorepo `/home/dali/WORK/utils`; `telco_si/target/`
  and local `*.db` are git-ignored. `CHANGELOG.md` follows Keep a Changelog.
  Code commits are pushed up to `Add subscribers tests` (f3522c6); the only
  pending change is the updated `CHANGELOG.md`.

## Decisions so far

- Layering: Interfaces → Application → Domain; infrastructure implements
  domain/application ports (SQLx, SQLite, event bus, payments, object storage).
- Bounded contexts: Subscriber, Inventory, Device, Usage, Rating, Roaming,
  Billing, Payment, Dunning, Document.
- `Money` invariant: balance can never be negative — `from_cents(<0)` is a
  hard error (`NegativeBalance`).
- Application errors are typed (`ApplicationError`) and mapped to HTTP status
  codes once, centrally, via `ResponseError`.
- Library crate (`src/lib.rs`) alongside the binary so integration tests can
  import application modules.

## Next steps (when user provides them)

1. Phase 2 — Subscriber context continues: more use cases/handlers as directed
   (e.g. balance operations), then remaining bounded contexts.
2. Phase 3 — Inventory (MSISDN, SIM/IMSI).
3. Phase 4 — Device (IMEI).
4. Phase 5 — Usage / CDR.
5. Phase 6 — Rating engine.
6. Phase 7 — Roaming.
7. Phase 8 — Billing.
8. Phase 9 — Payments.
9. Phase 10 — Dunning.
10. Phase 11 — Documents / PDF.
11. Phase 12 — Production architecture (events, outbox, observability, security, Docker, CI/CD).

## Reminders for the next session

- Wait for the user to give build steps; do not scaffold code unprompted.
- Update `CHANGELOG.md` versions and this handoff as phases complete.
- Push confidently: no oversized blobs remain; the next push is a normal
  fast-forward from `origin/main`.
- `cargo build`/`cargo test` may stall on first run (network fetch); use
  `--offline` if dependencies are already cached.
