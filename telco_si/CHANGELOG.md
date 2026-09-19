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

### Legend

- Feature Domain: bounded context (or set of contexts) delivered by the version.
- Key Objectives: main deliverables scoped to that version.

## [Unreleased]

## [0.0.3] - 2026-09-19

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
