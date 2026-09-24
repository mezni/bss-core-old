# Session Handoff

_Last updated: 2026-09-24_

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

Runtime/API (0.0.1–0.0.2 Foundation) and Phase 2 Subscriber context are
implemented and tested end to end. The changelog now tracks this as
**0.0.5 (Foundation + Subscriber)**, dated 2026-09-24.

- **HTTP API** (`src/interfaces/http/`):
  - `POST /subscribers` (201), `GET /subscribers/{id}` (200/404),
    `POST /subscribers/{id}/suspend|activate|terminate` (200), all via
    `AppState` + `web::Data`. Central `ResponseError` maps `ApplicationError`
    to 404/409/400/400/409/500.
  - `GET /subscribers` — paginated list (default `page=1`, `page_size=20`,
    guards `page >= 1`, `1 <= page_size <= 100`) with optional
    `status` / `account_number` filters; invalid `status` → 400 via
    `parse_status()`.
- **Read models / query object**:
  - `src/application/subscriber/query.rs` — `SubscriberListItem`,
    `SubscriberPage`, and `SubscriberListQuery` (`page`, `page_size`,
    `status: Option<SubscriberStatus>`, `account_number`). List operations
    never rebuild the full aggregate.
  - HTTP DTO `SubscriberListRequest` (raw strings) is converted to the typed
    application query in the handler — arbitrary status strings can't reach
    the application layer.
  - `src/infrastructure/persistence/subscriber_repository.rs` `list()`
    builds page + `COUNT(*)` SQL with `sqlx::QueryBuilder` (dynamic
    structure, bound values only → no SQL injection).
- **Optimistic concurrency** (`version` column):
  - Migration `20260924153511_add_subscriber_version.sql`.
  - Domain `Subscriber` carries `version` (`version()`, `increment_version()`);
    `reconstitute()` reads it from the DB.
  - `ApplicationError::ConcurrencyConflict` added and mapped to 409, but the
    repository still returns `anyhow` (conflicts surface as
    `Infrastructure` → 500 today); a typed repository error design
    (`NotFound`/`Duplicate`/`ConcurrencyConflict`/`Database`) is deferred.
- **Domain events**:
  - `src/domain/events.rs` — `DomainEvent` (`SubscriberSuspended`,
    `SubscriberActivated`, `SubscriberTerminated`), past-tense facts,
    `Serialize + Deserialize`, metadata helpers `event_type()` /
    `aggregate_type()` / `aggregate_id()` / `occurred_at()`.
  - `Subscriber` collects events: empty on `new()`/`reconstitute()`, pushed
    only after valid transitions, read via `domain_events()` slice,
    drained by `take_domain_events()` / `clear_domain_events()`.
  - `src/application/event_publisher.rs` — `EventPublisher` port;
    `src/infrastructure/events/in_memory.rs` — `InMemoryEventPublisher`.
    **Not wired into the service yet** (durability problem → outbox).
- **Transactional outbox**:
  - Migration `20260924155420_create_outbox_events.sql` (with
    `(published_at, created_at)` index for the future publisher worker).
  - Repository `update()` replaced by
    `save(&subscriber, &[DomainEvent])`: single transaction =
    optimistic-lock `UPDATE` + one `INSERT` per event into `outbox_events`
    (JSON payload). Any failure rolls back both.
  - Service `suspend`/`activate`/`terminate`:
    mutate → `domain_events().to_vec()` → `save()` → `clear_domain_events()`
    → `increment_version()`. `create()` still uses `repository.create()`
    (no `SubscriberCreated` event yet).
- **Tests** — `cargo test`: 17 domain unit tests + 12 integration tests
  (create/get, duplicate, lifecycle, HTTP create 201 / invalid 400, list
  pagination, status/account_number filters, invalid status 400, stale update
  rejected, outbox row on suspend).
- **CHANGELOG.md** — Keep a Changelog. Version history consolidated: only
  `0.0.5` (newest), `0.0.2`, `0.0.1`; `0.0.3`/`0.0.4` were removed (never
  released); empty `## [Unreleased]` sits at the top for future work.
- **Git** — repo root is the monorepo `/home/dali/WORK/utils`; `telco_si/target/`
  and local `*.db` are git-ignored. Code + CHANGELOG committed through
  `389d83e Add transactional Outbox Pattern`; the pending change is this
  updated handoff.

## Decisions so far

- Layering: Interfaces → Application → Domain; infrastructure implements
  domain/application ports (SQLx, SQLite, event bus, payments, object storage).
- Bounded contexts: Subscriber, Inventory, Device, Usage, Rating, Roaming,
  Billing, Payment, Dunning, Document.
- `Money` invariant: balance can never be negative — `from_cents(<0)` is a
  hard error (`NegativeBalance`).
- Application errors are typed (`ApplicationError`) and mapped to HTTP status
  codes once, centrally, via `ResponseError`.
- Read models (`SubscriberListItem`/`SubscriberPage`) are separate from the
  aggregate; query filters are typed domain values, not raw strings.
- Optimistic locking via `version` (conditional `UPDATE ... AND version = ?`).
- State transitions emit domain events only on success; events are persisted
  with the aggregate in one transaction (outbox), never written to the
  publisher directly from a request (avoid DB-update/event-inconsistency).
- `EventPublisher` port is dependency-inverted (in-memory impl for now).

## Next steps (when user provides them)

1. Subscriber context continues (part 8+): likely an outbox publisher worker
   that drains `outbox_events` where `published_at IS NULL` and dispatches via
   `EventPublisher`; possibly a `SubscriberCreated` event so `create()` also
   joins the outbox; possibly typed repository errors.
2. Phase 3 — Inventory (MSISDN, SIM/IMSI).
3. Phase 4 — Device (IMEI).
4. Phase 5 — Usage / CDR.
5. Phase 6 — Rating engine.
6. Phase 7 — Roaming.
7. Phase 8 — Billing.
8. Phase 9 — Payments.
9. Phase 10 — Dunning.
10. Phase 11 — Documents / PDF.
11. Phase 12 — Production architecture (events, outbox worker, observability, security, Docker, CI/CD).

## Reminders for the next session

- Wait for the user to give build steps; do not scaffold code unprompted.
- Update `CHANGELOG.md` versions and this handoff as phases complete.
- Push confidently: no oversized blobs remain; the next push is a normal
  fast-forward from `origin/main`.
- `cargo build`/`cargo test` may stall on first run (network fetch); use
  `--offline` if dependencies are already cached.
- `cargo sqlx migrate ...` needs `DATABASE_URL` (e.g.
  `DATABASE_URL=sqlite://telco_si.db cargo sqlx migrate info`).