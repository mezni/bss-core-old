# Contract: Configuration

**Feature**: `002-fastapi-foundation` | **Date**: 2026-09-26

`docs/configuration.md` is the authority for setting names, types, and defaults. This
file records only the subset this feature reads, and the failure behaviour the spec
requires of each. The full catalogue is deliberately not duplicated here.

## Read once, at startup

Settings are constructed when the application is built, not per request. A request must
never be able to change how the server is configured (FR-011, constitution: "Settings
are read once at startup").

## Settings in scope

| Setting | Type | Default | Requirement | Invalid value |
|---|---|---|---|---|
| `APP_NAME` | string | `Fake E-Commerce Server` | FR-005 | Startup fails naming the setting |
| `APP_VERSION` | string | `0.1.0` | FR-005, SC-011 | Startup fails naming the setting |
| `APP_ENV` | enum | `development` | FR-010 | Startup fails listing accepted values |
| `API_V1_PREFIX` | string | `/api/v1` | FR-006 | Startup fails on empty or conflicting value |
| `API_DOCS_ENABLED` | boolean | `true` | FR-004 | Startup fails; never coerced to "off" |
| `API_REDOC_ENABLED` | boolean | `true` | FR-004 | Startup fails; never coerced to "off" |
| `HOST` | string | `127.0.0.1` | FR-013 | Startup fails naming the setting |
| `PORT` | integer | `8000` | FR-014 | Startup reports the port is occupied |

`DATABASE_URL` is **not** read by this feature. Nothing opens a database (FR-003,
FR-018); the first feature that persists data owns that setting.

## Failure rules

1. **No silent fallback** (FR-011). An unparseable value fails startup with a message
   naming the setting and its accepted values. Falling back to a default would mask the
   mistake behind a server that appears to work.
2. **A non-boolean switch is an error, not `false`** (FR-004, edge case). `API_DOCS_ENABLED=flase`
   must not read as "off": a typo that silently disabled both descriptions presents as a
   working server with no documentation, which is far harder to diagnose than a refusal
   to start.
3. **An empty `API_V1_PREFIX` is an error** (FR-006, edge case). An empty prefix would
   place future business routes outside the versioned namespace, breaking the contract
   every client depends on.
4. **No file is required** (FR-010, FR-012). Every setting has a default, so the server
   starts with no configuration file present, with the file empty, and with it partially
   filled. No secret is needed to run and none may be committed.
5. **The object is immutable after construction** (FR-011). Behaviour must not depend on
   request order.

## Version relationship

`APP_VERSION` is the **published** source of the version (FR-005, per the specification
clarification). The **installed** source is `importlib.metadata.version("ecommerce")`.

SC-011 requires them to be equal in 100% of verification runs, asserted by an automated
check, so a version bump touching only one of `pyproject.toml`, `__init__.py`, and the
`APP_VERSION` default fails `make check`. See `research.md` D-04 for why package metadata
is compared rather than the `__version__` literal.

## `.env.example`

Required by the constitution and depended on by FR-010 through FR-012, but **not yet
present in the repository**. It is recorded as a prerequisite in `plan.md` (P5) and as an
assumption in `spec.md`, not assumed to exist.

## Divergence to fix in the source document

`docs/configuration.md` §11 currently reads:

> `API_DOCS_ENABLED=false` in production (§28.3) hides `/docs` and `/openapi.json`, but
> **not** the schema itself from anyone who knows the path — it is a convenience switch,
> not a security control.

Those clauses contradict each other, because `/openapi.json` is the only URL the schema is
served from and no second path is named. This feature implements the first clause — both
URLs return 404 when the switch is off — and preserves the second as *intent*: the
switch is not a security boundary. Resolved as `research.md` D-05; the document's wording
is queued for correction.
