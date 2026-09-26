# Phase 1 Data Model: FastAPI Foundation

**Feature**: `002-fastapi-foundation` | **Date**: 2026-09-26

This feature persists nothing and models no business data. There is no database, no
migration, and no entity with fields or state transitions. What follows is the complete
set of *value objects* the feature exchanges, plus the configuration state that governs
them, so `/speckit.tasks` has a closed list of what to build.

The constitution's rule that "database models MUST NOT automatically become public API
schemas" has no application here — there are no database models. The rule that shapes
this document instead is that Pydantic v2 performs validation at API boundaries while
business rules do not live inside Pydantic schemas. Both objects below are boundary
concerns, which is the correct place for them.

---

## 1. `HealthStatus` — the liveness response

The entire body of `GET /health`, and the feature's only response schema.

| Field | Type | Required | Value | Source |
|---|---|---|---|---|
| `status` | literal `"ok"` | yes | Always `"ok"` | Constant |

**Validation rules**: none beyond the literal. There is deliberately no version field, no
timestamp, no uptime, and no dependency status.

| Rule | Requirement | Rationale |
|---|---|---|
| The response MUST NOT contain a version | FR-002 | `docs/API.md` §25.1 publishes exactly `{"status": "ok"}`; the version belongs on `/ready`, which §25.2 marks planned and not required. A versioned liveness probe is the wrong place for it. |
| The response MUST NOT reflect any dependency's state | FR-003 | A liveness probe that fails when a dependency is slow causes orchestrators to restart healthy processes. |
| The response MUST NOT vary with configuration | FR-003 | The check reports that the process is alive, nothing more. Any variation would make it a readiness signal. |

**State transitions**: none. The endpoint either answers or the process is not running;
there is no "degraded" state to represent. A failing liveness check is expressed by the
absence of a response, not by a payload.

---

## 2. `ErrorEnvelope` — the single failure structure

Returned by every failing request, in this phase for unknown paths (404) and unhandled
server faults (500).

| Field | Type | Required | Meaning | Source |
|---|---|---|---|---|
| `error.code` | string | yes | Stable machine-readable code | Exception-to-code mapping at the API boundary |
| `error.message` | string | yes | Human-readable summary | The mapped code's message, or a fixed generic message for 500 |
| `error.details` | array | yes | Field-level issues. **Always an array**, empty when there are none. **Never an object.** | Validation issues; otherwise `[]` |
| `error.request_id` | string | yes | Identifier a client can quote in a bug report | `X-Request-ID` if supplied and acceptable, else a generated UUID4 |

The envelope nests everything under a single top-level `error` key.

**Validation rules**:

| Rule | Requirement | Rationale |
|---|---|---|
| All four fields are always present | FR-008 | The constitution and `docs/API.md` §12 make the envelope fixed at four fields; `details` is never omitted and `request_id` is never absent. |
| `details` is always an array | FR-008 | A consumer must be able to iterate it without a null check. Divergence E17 settled this explicitly. |
| No exception text, stack frame, or file system path in any field | FR-009 | Internal detail is the project's most common accidental leak. The generic handler returns a fixed message and logs the detail server-side. |
| `code` is drawn from the published list | FR-008 | This phase can emit only `NOT_FOUND`, `VALIDATION_ERROR`, and `INTERNAL_ERROR`. Inventing a code would put an unpublished value in a published contract. |

**State transitions**: none. An error report is a terminal value; it is written once and
never mutated.

---

## 3. `Settings` — configuration state, not exchanged data

Read once at application construction. Never serialised into a response. Listed here
because it is the feature's only mutable-by-environment state and every switch in it is a
requirement.

| Setting | Type | Default | Requirement | Failure behaviour |
|---|---|---|---|---|
| `app_name` | string | `Fake E-Commerce Server` | FR-005 | Startup fails naming the setting |
| `app_version` | string | `0.1.0` | FR-005, SC-011 | Startup fails naming the setting |
| `app_env` | enum | `development` | FR-010 | Startup fails listing accepted values |
| `api_v1_prefix` | string | `/api/v1` | FR-006 | Startup fails on empty or conflicting value |
| `api_docs_enabled` | boolean | `true` | FR-004 | Startup fails; never coerces a non-boolean to "off" |
| `api_redoc_enabled` | boolean | `true` | FR-004 | Startup fails; never coerces a non-boolean to "off" |
| `host` | string | `127.0.0.1` | FR-013 | Startup fails naming the setting |
| `port` | integer | `8000` | FR-014 | Startup reports the port is occupied |

**Validation rules**:

| Rule | Requirement | Rationale |
|---|---|---|
| Invalid values fail startup; no silent fallback | FR-011 | A typo that silently disabled the descriptions would present as a working server with no documentation, which is harder to diagnose than a refusal to start. |
| A non-boolean switch value is an error, not `false` | FR-004, edge case | Same rationale, and the failure mode is specifically "looks off when the author meant on". |
| An empty `api_v1_prefix` is an error | FR-006, edge case | An empty prefix would place future business routes outside the versioned namespace, breaking the contract every client depends on. |
| No setting is required to be present | FR-010, FR-012 | Every value has a default, so the server starts with no configuration file, and no secret is needed to run. |
| The object is immutable after construction | FR-011, constitution | "Settings are read once at startup"; mutating them mid-process would make behaviour depend on request order. |

**Version relationship**: `app_version` is the published source per the spec's
clarification. `importlib.metadata.version("ecommerce")` is the installed source. SC-011
requires them to be equal, asserted by an automated check, so a bump that updates only
one fails `make check`. See `research.md` D-04.

---

## 4. Deliberately absent

Recording these prevents a later feature from assuming the foundation provides them.

| Not modelled | Why | Belongs to |
|---|---|---|
| `ReadinessReport` | §25.2 marks it planned, not required. Liveness is specified to be independent of it. | A later feature |
| Any domain entity | No business capability is in scope (FR-018) | Product catalog, cart, orders, inventory, payments |
| Authentication identity or role | §18 places authentication in Phase 12 | `010-authentication` |
| Any persistence entity or migration | Nothing is stored (FR-018) | The first feature needing a database |
| Request metrics or log records | Observability is a later phase; this feature supplies only the `request_id` the error envelope mandates | `011-observability` |
| Pagination, filtering, or sorting | No list endpoint exists to page | The first feature with a collection resource |
