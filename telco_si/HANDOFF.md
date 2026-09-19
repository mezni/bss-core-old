# Session Handoff

_Last updated: 2026-09-19_

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
  - SQLx 0.9 + SQLite pool with `create_if_missing(true)`, WAL, foreign keys;
    `SELECT 1` verification before binding. Deps: actix-web, tokio, sqlx, anyhow,
    thiserror, tracing, tracing-subscriber, uuid, chrono, serde.
  - `src/database.rs`, `src/config.rs`, `src/main.rs`.
- **Domain layer — Subscriber context (part 1)** — implemented and tested:
  - `src/domain/mod.rs` → `pub mod subscriber;`
  - `src/domain/subscriber/mod.rs` — module wiring + public re-exports.
  - `src/domain/subscriber/error.rs` — `SubscriberError` (thiserror):
    `AlreadySuspended`, `AlreadyActive`, `Terminated`, `InvalidTermination`,
    `NegativeBalance`, `InvalidAccountNumber`.
  - `src/domain/subscriber/value_objects.rs` — `SubscriberStatus`,
    `SubscriberId` (UUID v4), `AccountNumber` (non-empty validation),
    `Money` with `zero()` / `from_cents()` — returns `Result` and rejects
    negative via `NegativeBalance` — / `cents()` / `add()`.
  - `src/domain/subscriber/entity.rs` — `Subscriber` aggregate: `new()`
    (starts Active, zero balance), `suspend()` / `activate()` / `terminate()`
    state transitions enforcing the lifecycle, getters.
  - `mod domain;` wired into `src/main.rs`.
- **Tests** — `cargo test` → 15 passing (subscriber entity state machine +
  value-object invariants).
- **Git** — repo root is the monorepo `/home/dali/WORK/utils`; `telco_si/target/`
  and local `*.db` are git-ignored. `CHANGELOG.md` follows Keep a Changelog.
  Working tree has the domain layer + `mod domain;` as new/unstaged work (not yet
  committed/pushed).

## Decisions so far

- Layering: Interfaces → Application → Domain; infrastructure implements
  domain/application ports (SQLx, SQLite, event bus, payments, object storage).
- Bounded contexts: Subscriber, Inventory, Device, Usage, Rating, Roaming,
  Billing, Payment, Dunning, Document.
- `Money` invariant: balance can never be negative — `from_cents(<0)` is a
  hard error (`NegativeBalance`).

## Next steps (when user provides them)

1. Phase 2 — Subscriber context continues: persistence/adapter for the
   Subscriber aggregate (migrations, SQLx repository), then application services.
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
