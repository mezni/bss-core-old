# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version history

| Version | Feature Domain | Key Objectives |
|---------|----------------|----------------|
| 0.0.3   | Foundation | Database pool creation, WAL + foreign keys, health endpoint with DB verification |
| 0.0.2   | Foundation | Dependencies, Actix Web server, health endpoint |
| 0.0.1   | Foundation | Project scaffold, DDD structure, dependencies, config, entry point |
| 0.0.4   | Subscriber  | Repository port + SQLite persistence, subscribers table migration, domain reconstitution |

### Legend

- Feature Domain: bounded context (or set of contexts) delivered by the version.
- Key Objectives: main deliverables scoped to that version.

## [Unreleased]

### Added

- `src/domain/` — Domain layer bootstrap (Phase 2, Subscriber context, part 1):
  - `src/domain/mod.rs` — domain root module re-exporting the subscriber context.
  - `src/domain/subscriber/mod.rs` — module wiring and public re-exports
    (`Subscriber`, `SubscriberError`, `AccountNumber`, `Money`, `SubscriberId`,
    `SubscriberStatus`).
  - `src/domain/subscriber/error.rs` — `SubscriberError` (`thiserror`) with
    variants covering the state machine: `AlreadySuspended`, `AlreadyActive`,
    `Terminated`, `InvalidTermination`, `NegativeBalance`, `InvalidAccountNumber`.
  - `src/domain/subscriber/value_objects.rs` — `SubscriberStatus` enum,
    `SubscriberId` (UUID v4), `AccountNumber` (non-empty validation),
    `Money` with `zero()` / `from_cents()` (returns `Result` and rejects negative
    amounts via `NegativeBalance`) / `cents()` / `add()`.
  - `src/domain/subscriber/entity.rs` — `Subscriber` aggregate: `new()`
    (starts Active, zero balance), `suspend()` / `activate()` / `terminate()`
    transitions enforcing the state machine, and getters.
  - `src/domain/subscriber/entity.rs` — `Subscriber::reconstitute()` builds an
    aggregate from persisted values (bypasses `new()` invariants for reads).
  - `src/domain/subscriber/value_objects.rs` — `SubscriberId::from_uuid()` for
    reconstructing IDs from the database.
- Unit tests for the Subscriber state machine and value-object invariants
  (15 tests: entity transitions + account-number/money validation).

### Added

- `src/application/` — Application layer bootstrap (Phase 2, Subscriber context, part 2):
  - `src/application/mod.rs` and `src/application/subscriber/mod.rs` — module wiring.
  - `src/application/subscriber/repository.rs` — `SubscriberRepository` port
    (`async_trait`, `Send + Sync`): `create()`, `find_by_id()`,
    `find_by_account_number()`, `update()`.
  - `src/application/subscriber/service.rs` — `SubscriberService<R>` use-case
    layer over `SubscriberRepository`:
    - `new()` constructor taking the repository.
    - `create()` — validates `AccountNumber`, rejects duplicate account numbers,
      and persists a new Active subscriber.
    - `get()` — retrieves a subscriber by `Uuid`.
    - `suspend()` / `activate()` / `terminate()` — load, apply the state
      transition (mapping domain errors to `anyhow`), and persist via `update()`.
  - `src/application/subscriber/mod.rs` — re-exports `SubscriberRepository` and
    `SubscriberService`.
- `src/infrastructure/` — Infrastructure layer bootstrap:
  - `src/infrastructure/mod.rs` and `src/infrastructure/persistence/mod.rs` — module wiring.
  - `src/infrastructure/persistence/subscriber_repository.rs` —
    `SqliteSubscriberRepository` implementing the `SubscriberRepository` port on
    SQLx: `SubscriberRow` (`FromRow`) mapped to/from the domain aggregate via
    `into_domain()` and `reconstitute()`, with status string mapping
    (`active` / `suspended` / `terminated`) and field validation on reads.
- `migrations/20260920183725_create_subscribers.sql` — `subscribers` table
  (UUID id, unique account_number, status with CHECK constraint,
  non-negative balance_cents, nullable plan_id, timestamps) plus an index on
  `status`.
- `src/main.rs` — runs `sqlx::migrate!` on startup before the pool
  verification.
- `src/database.rs` — pool built with `SqlitePoolOptions::max_connections(10)`.
- Dependency: `async-trait`.

### Added

- `src/interfaces/` — HTTP interface layer (Phase 2, Subscriber context, part 3):
  - `src/interfaces/mod.rs` and `src/interfaces/http/mod.rs` — module wiring.
  - `src/interfaces/http/dto.rs` — `CreateSubscriberRequest` (Deserialize) and
    `SubscriberResponse` (Serialize) with `From<Subscriber>` conversion.
  - `src/interfaces/http/subscriber.rs` — Actix Web handlers on the
    `/subscribers` scope:
    - `POST /subscribers` — create (201 on success, 400 on error).
    - `GET /subscribers/{id}` — get (200, 404 if not found, 500 on error).
    - `POST /subscribers/{id}/suspend` | `/activate` | `/terminate` — state
      transitions (200 on success, 400 on error).
    - `configure()` registering the scoped routes.
- `src/main.rs` — wires `SqliteSubscriberRepository` → `SubscriberService`,
  injects the service via `web::Data` (cloned per worker), and configures the
  subscriber routes alongside `/health`.
- `SubscriberService` now derives `Clone` (and `SqliteSubscriberRepository`
  derives `Clone` via `SqlitePool`) so it can be shared across Actix workers.

### Added

- `src/application/error.rs` — `ApplicationError` enum (`thiserror`) with typed
  variants: `SubscriberNotFound`, `AccountNumberAlreadyExists`,
  `InvalidRequest`, `InvalidSubscriberState`, `Infrastructure` (+ `ApplicationResult<T>` alias).
- `src/application/subscriber/service.rs` — use-case methods now return
  `ApplicationResult` instead of `anyhow::Result`, mapping validation /
  duplicates / missing rows / state-machine / repository failures to the
  respective `ApplicationError` variants.
- `src/interfaces/http/error.rs` — centralized `ResponseError` for
  `ApplicationError`:
  - 404 for `SubscriberNotFound`.
  - 409 for `AccountNumberAlreadyExists` and `InvalidSubscriberState`.
  - 400 for `InvalidRequest`.
  - 500 with a generic `"internal server error"` body (error logged) for
    `Infrastructure`.
- `src/interfaces/http/subscriber.rs` — handlers simplified to
  `Result<HttpResponse, ApplicationError>` using `?`; `get_subscriber`
  returns 404 via `SubscriberNotFound` when no row exists.

### Added

- `src/lib.rs` — exposes the application as a library crate
  (`application`, `config`, `database`, `domain`, `infrastructure`,
  `interfaces`) so integration tests can import the modules.
- `src/main.rs` — drops local `mod` declarations and imports from the
  `telco_si` library crate.
- `tests/subscriber_integration.rs` — integration tests on an in-memory
  SQLite database (`sqlite::memory:` with `max_connections(1)` so a single
  connection backs the test DB, plus migrations on setup):
  - `create_and_get_subscriber` — full service → repository → SQLite round trip.
  - `duplicate_account_number_is_rejected` — duplicates surface as
    `ApplicationError::AccountNumberAlreadyExists`.
  - `subscriber_lifecycle_is_persisted` — suspend → activate → terminate
    transitions are persisted and reloadable.
  - `create_subscriber_through_http` — `POST /subscribers` via the Actix test
    harness returns 201.

### Added

- `src/database.rs` — SQLite connection pool via SQLx 0.9 `SqliteConnectOptions`:
  - `create_if_missing(true)` — fixes sqlx 0.9's default (error code 14, `unable to open database file`) which no longer auto-creates the DB file.
  - WAL journal mode and foreign keys enabled at the options level.
- `src/config.rs` — `AppConfig` reading `APP_HOST`, `APP_PORT`, `DATABASE_URL` from env (returning `anyhow::Result`).
- `src/main.rs`:
  - Initializes `tracing_subscriber` with env-filter (fallback `telco_si=info`).
  - Loads config, creates the DB pool, verifies connectivity with `SELECT 1` before binding.
  - Health endpoint returns `{"status": "ok"}`.
- `.gitignore` for `/target` and local `*.db` files.

### Fixed

- Server startup failed with `unable to open database file` (SQLite code 14) because sqlx 0.9 defaults `create_if_missing` to `false`; the pool is now built with explicit connect options.

### Changed

- `src/application/state.rs` — new `AppState` aggregate holding
  `subscriber_service` (a `SubscriberService<SqliteSubscriberRepository>`),
  exported from `src/application/mod.rs` as `AppState`.
- `src/interfaces/http/subscriber.rs` — all handlers
  (`create_subscriber`, `get_subscriber`, `suspend_subscriber`,
  `activate_subscriber`, `terminate_subscriber`) now receive
  `web::Data<AppState>` and access `state.subscriber_service` instead of
  receiving the concrete service directly; the `SubscriberAppService` type
  alias was removed.
- `src/main.rs` — builds `AppState` from the subscriber service and injects it
  via `web::Data::new(app_state.clone())` per worker.
- `tests/subscriber_integration.rs` — `create_subscriber_through_http` builds
  an `AppState` and injects it with the same dependency structure as
  production.

### Added

- Dependency: `validator` 0.20 (with `derive`).
- `src/interfaces/http/dto.rs` — `CreateSubscriberRequest` validates
  `account_number` via `#[validate(length(min = 3, max = 50))]`;
  `SubscriberResponse` now derives `Deserialize` so API responses can be
  decoded directly in integration tests.
- `src/application/error.rs` — new `ApplicationError::Validation` variant
  (`"validation failed"`).
- `src/interfaces/http/subscriber.rs` — `create_subscriber` runs
  `request.validate()` before creating the subscriber.
- `src/interfaces/http/error.rs` — `Validation` maps to HTTP 400. The full
  error mapping is now: 404 `SubscriberNotFound`, 409
  `AccountNumberAlreadyExists` / `InvalidSubscriberState`, 400
  `Validation` / `InvalidRequest`, 500 `Infrastructure`.
- `tests/subscriber_integration.rs`:
  - `create_subscriber_through_http` now decodes the 201 response body and
    asserts `account_number` and `balance_cents`.
  - `create_subscriber_rejects_invalid_account_number` — `POST /subscribers`
    with a too-short account number returns 400.

## [0.0.2] - 2026-09-19

### Added

- Web/API dependencies: `actix-web`, `tokio` (macros, rt-multi-thread), `serde` (derive), `serde_json`.
- Observability and error-handling dependencies: `anyhow`, `thiserror`, `tracing`, `tracing-subscriber` (fmt, env-filter).
- Utility and model dependencies: `uuid` (v4, serde), `chrono` (serde).
- Database dependency: `sqlx` 0.9 with `runtime-tokio`, `sqlite`, `macros`, `migrate`, `chrono`, `uuid`.
- Actix Web entry point (`main.rs`) replacing the hello-world stub.
- `GET /health` endpoint returning `{"status": "ok"}`.

## [0.0.1] - 2026-09-19

### Added

- Initial Rust project scaffold for the telco_si BSS/OSS platform.
- Target architecture:
  - Interfaces → Application → Domain layering with strict dependency rules.
  - Infrastructure implements domain/application ports (SQLx, SQLite, event bus, payments, object storage).
  - Bounded contexts: Subscriber, Inventory, Device, Usage, Rating, Roaming, Billing, Payment, Dunning, Document.

### Planned roadmap

- Phase 1 — Foundation: Cargo config, Actix Web, Tokio, SQLx + SQLite (WAL + foreign keys), config loader, entry point, health endpoints, error-handling conventions, logging/tracing. (in progress)
- Phase 2 — Subscriber context.
- Phase 3 — Inventory (MSISDN, SIM/IMSI).
- Phase 4 — Device (IMEI).
- Phase 5 — Usage / CDR.
- Phase 6 — Rating engine.
- Phase 7 — Roaming.
- Phase 8 — Billing.
- Phase 9 — Payments.
- Phase 10 — Dunning.
- Phase 11 — Documents / PDF.
- Phase 12 — Production architecture (events, outbox, observability, security, Docker, CI/CD).

The src/ directory is intentionally kept empty (only the hello-world `main.rs`) until
implementation steps are provided incrementally.
