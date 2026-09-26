# Implementation Plan: FastAPI Foundation

**Branch**: `002-fastapi-foundation` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-fastapi-foundation/spec.md`

## Summary

Phase 1 of the fake e-commerce server: turn a bare Python package into a running,
self-describing HTTP service. The feature delivers a single documented start command, an
unversioned dependency-free liveness check, a reserved configurable versioned route
namespace, machine- and human-readable API descriptions gated by two independent
configuration switches, a single consistent error envelope for unknown paths, and an
automated check for every one of those behaviours. It adds no business capability, no
persistence, and no authentication.

The technical approach is the smallest structure that satisfies the constitution's
inward-pointing dependency rule: an `api` layer (routers, error envelope, wiring) over an
`application`/`domain` core that stays framework-free, with all configuration resolved
once at startup through Pydantic Settings and every switch having a documented default so
the server runs from a clean checkout with no configuration file.

**This plan also carries three corrections to Phase 0 scaffolding.** Planning surfaced
that the declared dependency groups are not installed by `uv sync`, that `uv.lock`
therefore contains no dependencies, and that the `ruff` and `pytest` tool configuration
sits in sections those tools do not read. All three block this feature's own acceptance
criteria, so fixing them is in scope here rather than deferred. See
[Phase 0 prerequisites](#phase-0-prerequisites-blocking).

## Technical Context

**Language/Version**: Python 3.12 (pinned in `.python-version`; `requires-python = ">=3.12"`)

**Primary Dependencies**: FastAPI, Uvicorn (ASGI server), Pydantic v2, Pydantic Settings v2
(settings from environment), pytest, HTTPX (via FastAPI's `TestClient`)

**Storage**: N/A for this feature. No database is opened, and no model or migration is
introduced. `DATABASE_URL` is deliberately not read yet; a later phase owns persistence.

**Testing**: pytest with the constitution-mandated `tests/unit`, `tests/integration`,
`tests/api` layout. API tests drive the ASGI app in-process through `TestClient`, so no
server process and no port binding is required for the suite.

**Target Platform**: Linux server, bound to loopback by default for development. No
container, no Windows or macOS requirement.

**Project Type**: web-service (modular monolith)

**Performance Goals**: The specification sets no latency or throughput target, because
this phase exposes no business route. Derived, and deliberately modest: the liveness check
answers in under 100 ms locally, and the full documented verification run completes in
under 60 seconds (SC-007). No concurrency or load requirement exists yet.

**Constraints**:
- Runs from a clean checkout to a serving liveness check in at most two documented
  commands (SC-001), with no configuration file present (FR-010).
- Configuration is read once at startup; an invalid value fails startup naming the
  setting and its accepted values (FR-011), never falling back silently.
- The liveness check MUST NOT touch a database, cache, migration state, or any external
  provider (FR-003), so it must not import the persistence layer even transitively.
- `uv.lock` MUST be committed and MUST cover every declared dependency (constitution).
- No secret may be required to run, and no secret may be committed (FR-012).
- Domain code MUST stay importable without FastAPI, a database, or an event loop
  (constitution, Principle I).

**Scale/Scope**: One application package, four configuration switches in active use, two
HTTP endpoints (`GET /health` plus a deliberately empty versioned namespace), one error
envelope, and one open question deferred to the observability phase (the request
identifier). No user data, no background work, no external service.

## Phase 0 prerequisites (blocking)

These were found while filling Technical Context. Each one is verified, and each blocks a
requirement in this feature, so each becomes a task in `/speckit.tasks` and must land
before the feature's own tasks.

| # | Finding | Evidence | Blocks |
|---|---|---|---|
| P1 | Runtime and development dependencies are declared in `[dependency-group.runtime]` and `[dependency-group.development]`. Neither is uv's default `dev` group, so `uv sync` installs nothing. | `uv sync --dry-run` reports it would *uninstall* all 14 dev packages | SC-001, SC-006, constitution `uv.lock` rule |
| P2 | `uv.lock` contains exactly one package (`ecommerce`). No dependency is locked. | `grep -c '^\[\[package\]\]' uv.lock` → `1` | Constitution: "`uv.lock` MUST be committed" |
| P3 | `[project.tool.ruff]` is not a section ruff reads (it reads `[tool.ruff]`), and `print.line-length-limit` is not a ruff key (it is `line-length`). The project's line length is therefore unset. | `ruff check --show-settings` reports no configured line length | `make lint` / `make format` correctness |
| P4 | `[project.tool.pytest.ini_options]` sets `python_paths`, which is not a pytest ini option (it is `pythonpath`). Tests import the package only because `uv` installs it editable. | declared key is `python_paths`; `pytest --collect-only` succeeds via the editable install | Test-suite portability |
| P5 | `.env.example`, required by the constitution and depended on by FR-010 through FR-012, does not exist. | file absent | FR-010, FR-011, FR-012 |

P1 and P2 are the same root cause and are fixed together: move runtime dependencies to
`[project] dependencies` and development dependencies to `[dependency-groups] dev`, then
re-lock.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Re-verified after Phase 1 design; result unchanged. All gates pass.

| Gate | Source | Result |
|---|---|---|
| Domain layer free of framework dependencies | Principle I | PASS — this feature adds no domain behaviour. The only logic is error mapping and settings, both at the boundary. The domain package stays importable without FastAPI, which a unit check asserts. |
| Deterministic behaviour, no uncontrolled randomness | Principle II | PASS — nothing random is generated. |
| Explicit business rules | Principle III | N/A — no business rules in scope. |
| Test layout `unit` / `integration` / `api`, isolated | Principle IV | PASS — all three directories are used. The dedicated SQLite test database is N/A because nothing persists. |
| Simple local development; modular monolith | Principle V | PASS — two commands from clean checkout; no new abstraction without demonstrated purpose. The error envelope and settings objects are the only new abstractions and both are required by the spec. |
| Technology baseline; no second framework | Technology Stack | PASS — FastAPI, Pydantic v2, Uvicorn, pytest, HTTPX only. `TestClient` is HTTPX-based, so no extra HTTP client is introduced. |
| Public routes versioned under `/api/v1/` | API Design | PASS with a documented exception — the liveness check is unversioned, as `docs/API.md` §25.1 requires and §25.2 justifies. All other public routes sit under the configurable prefix whose default is `/api/v1`. |
| Consistent four-field error envelope; no stack traces | Security & Observability | PASS — one handler emits `code`, `message`, `details` (always an array), `request_id` (always present). `NOT_FOUND` and `INTERNAL_ERROR` are the only codes this phase can emit. |
| Configuration externalized, read once, fails fast, no secrets | Security & Observability | PASS — the settings object is constructed once at import of the application factory; validation errors name the offending setting. |
| `GET /health` exposed; readiness may come later | Security & Observability | PASS — in scope, with no version and no dependency access. |
| `uv.lock` committed | Technology Stack | PASS **after P1/P2** — currently violated; fixed as a prerequisite. |
| Documentation updated when behaviour changes | Documentation Layout | PASS — this feature changes behaviour, so `README.md`, `CHANGELOG.md`, `docs/API.md`, `docs/configuration.md`, and `docs/development.md` are updated as part of the feature. |
| All Speckit artifacts under `specs/` | Speckit Process | PASS — `specs/002-fastapi-foundation/`. |
| No microservices, broker, event sourcing, or CQRS | Principle V | PASS — explicitly forbidden by FR-017 and not introduced. |

### Divergences identified (not silently resolved)

The constitution requires conflicts to be named explicitly. Three were found; none is a
principle violation, and none is left implicit.

1. **The constitution's feature roadmap does not match the repository.** The constitution
   lists `001-foundation` and `002-product-catalog`; the repository has
   `001-project-foundation` and `002-fastapi-foundation`. Phase 0 turned out to be
   project scaffolding rather than the API foundation, so the API foundation took number
   002 and every later feature shifts by one. The constitution's enumerated list is now
   wrong. Resolution: amend the constitution's list (a PATCH — no principle changes) as a
   tracked task. This plan proceeds on the repository's actual numbering, which is the
   authoritative one per the constitution's own rule that the active directory is recorded
   in `.specify/feature.json`.
2. **`.env.example` is required but absent** (P5). Its absence is recorded in the spec's
   assumptions rather than assumed away, and creating it is a prerequisite task.
3. **`docs/configuration.md` §11 contains a self-contradictory sentence** about
   `API_DOCS_ENABLED`. It says the switch "hides `/docs` and `/openapi.json`, but **not**
   the schema itself from anyone who knows the path". `/openapi.json` *is* how the schema
   is served; the document names no other path. Resolved in
   [research.md](./research.md) (Decision D-05) in favour of the implementable reading, and
   the document needs a wording fix as a tracked task.

## Project Structure

### Documentation (this feature)

```text
specs/002-fastapi-foundation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # The generated API description, as the contract
│   ├── error-envelope.md# The single error structure every failure returns
│   └── configuration.md # Settings this feature reads, with defaults
├── spec.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/ecommerce/
├── __init__.py            # __version__ — the installed version, asserted against APP_VERSION
├── main.py                # Application factory and ASGI entry point (uvicorn ecommerce.main:app)
├── config.py              # Settings: environment parsing, documented defaults, fail-fast
├── domain/                # Framework-free core. No FastAPI, no I/O.
│   └── __init__.py
├── application/           # Use-case orchestration. Depends inward on domain only.
│   └── __init__.py
├── api/
│   ├── __init__.py
│   ├── router.py          # The reserved versioned router, mounted with the configured prefix
│   ├── health.py          # GET /health — operational, unversioned, dependency-free
│   └── errors.py          # The single error envelope and its exception handlers
└── observability/
    └── request_id.py      # Minimal request-id seam, expanded by the observability phase

tests/
├── unit/                  # Settings defaults and failure messages; version equality;
│                          # domain importable without FastAPI
├── integration/           # App factory wiring: router mounted under the configured prefix;
│                          # description switches honoured
└── api/                   # GET /health contract; OpenAPI parses and lists the route;
                           # description switches on/off; 404 envelope; no leakage

data/                      # Created only when a later phase needs a database
```

**Structure Decision**: Single-package `src/` layout, matching the existing
`src/ecommerce/` and the repository's `pythonpath`. The `domain/`, `application/`, `api/`,
and `observability/` split exists to make the constitution's inward-pointing dependency
rule visible in the directory tree rather than only in a convention, and it is what lets
the unit suite assert that the domain imports without FastAPI. `domain/` and
`application/` are created empty in this phase — no speculative abstraction is added
beyond the two packages the constitution's layering rule requires. `observability/` is a
single module, not a subsystem, because the spec requires a request identifier and
nothing else; the observability feature (011) will grow it.

The constitution's `tests/integration/` requirement is honoured even though this phase has
no database: integration tests here cover application-factory wiring, which is genuine
cross-component behaviour distinct from the HTTP-level checks in `tests/api/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations require justification. Every gate passes, and the three divergences above
are documentation and dependency-declaration corrections, not complexity the design
introduces. The two decisions most open to a "too clever" objection are recorded here
with the simpler alternative that was rejected, so the choice is reviewable:

| Decision | Simpler alternative rejected because |
|---|---|
| Four-layer package split (`domain`/`application`/`api`/`observability`) created in a feature that adds no business logic | Rejected flat layout: the constitution's Principle I is the project's defining constraint, and a flat layout would leave the inward-pointing rule unenforced until the first real domain feature, which is exactly when retrofitting it is most expensive. Two of the four packages stay empty in this phase, which is the cost. |
| `domain/` and `application/` created as empty packages | Rejected deferring them: an empty package is the cheapest possible statement of intent, and deferring means the first business feature invents the boundary while the only feature that could have constrained it is already closed. |