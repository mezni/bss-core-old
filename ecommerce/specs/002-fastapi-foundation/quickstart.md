# Quickstart: Validating the FastAPI Foundation

**Feature**: `002-fastapi-foundation` | **Date**: 2026-09-26

How to confirm this feature works end to end. Every command below is expected to work
from a clean checkout after the prerequisite corrections land. This is a validation and
run guide — implementation details belong in `tasks.md`.

Two documented commands must reach a serving liveness check (SC-001). They are
`make install` and `make run`.

---

## Prerequisites

- `uv` on `PATH`. Nothing else — no system Python, no virtualenv to create by hand.
- A clean checkout. No configuration file is needed, and none should be created
  (FR-010, FR-012).
- Free TCP port 8000, or set `PORT` to another.

## Validation scenarios

### V-1 — Clean checkout reaches a serving liveness check (SC-001)

```bash
make install     # uv sync — installs the project and its dependencies
make run         # starts the server on 127.0.0.1:8000
```

Then, in a second shell:

```bash
curl -s http://127.0.0.1:8000/health
```

**Expected**: exactly

```json
{"status":"ok"}
```

Two commands, no manual configuration, no undocumented step. Note the response carries no
version and no dependency status (FR-002, FR-003) — if either appears, the endpoint is
wrong.

### V-2 — The description matches the published contract (FR-005, SC-003)

```bash
curl -s http://127.0.0.1:8000/openapi.json | python -m json.tool > /dev/null && echo "parses"
curl -s http://127.0.0.1:8000/openapi.json | grep -o '"version": *"[^"]*"'
```

**Expected**: `parses`, and a version equal to `APP_VERSION` and to the installed package
version:

```bash
uv run python -c "import importlib.metadata as m; print(m.version('ecommerce'))"
```

All three must agree. If they disagree, the version equality check has failed and
`make check` will say so (SC-011).

Compare the whole document against `contracts/openapi.yaml`. It is expected to contain
`/health` and **no** `/api/v1` path entry, because the versioned namespace is reserved but
empty.

### V-3 — Human-readable descriptions are served (FR-004)

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/docs      # expect 200
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/redoc     # expect 200
```

### V-4 — The switches are independent (FR-004, Story 2 AS 5)

Restart with one switch off:

```bash
API_DOCS_ENABLED=false make run
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/openapi.json  # expect 404
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/docs          # expect 404
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/redoc         # expect 200
curl -s http://127.0.0.1:8000/health                                        # expect {"status":"ok"}
```

**Expected**: the disabled pair is gone, the other description and the liveness check are
unaffected. Then repeat with `API_REDOC_ENABLED=false` to confirm the second switch is
genuinely independent. See `contracts/configuration.md` for the known wording divergence
in the source document.

### V-5 — Unknown paths return the standard envelope (FR-008, FR-009, SC-004)

```bash
curl -s http://127.0.0.1:8000/nope
```

**Expected**: HTTP 404 with all four fields present, `details` an array, `request_id` a
string:

```json
{"error":{"code":"NOT_FOUND","message":"...","details":[],"request_id":"..."}}
```

Then confirm nothing leaks (FR-009):

```bash
curl -s http://127.0.0.1:8000/nope | grep -Ei 'traceback|/home/|site-packages|\.py"|File "'
```

**Expected**: no output.

### V-6 — Configuration is honoured, and bad values fail loudly (FR-010, FR-011, FR-012)

```bash
API_V1_PREFIX=/api/v2 make run       # a non-default prefix is accepted
```

```bash
API_DOCS_ENABLED=flase make run      # typo, not "false"
```

**Expected**: startup fails with a message naming `API_DOCS_ENABLED` and its accepted
values. It must **not** start with the descriptions silently disabled.

Also confirm the server starts with no configuration file at all, and with an empty one:

```bash
: > .env && make run && rm -f .env
```

**Expected**: starts normally on defaults.

### V-7 — Startup failure is actionable (FR-013, FR-014)

```bash
make run &                            # occupy the port
PORT=8000 make run                    # then start a second one
```

**Expected**: the second startup fails naming the occupied port, not with an unrelated
low-level error. And confirm the default bind is loopback-only:

```bash
ss -ltnp 2>/dev/null | grep 8000
```

**Expected**: bound to `127.0.0.1`, not `0.0.0.0` (FR-013).

### V-8 — The full verification run (SC-005, SC-006, SC-007, SC-010)

```bash
make check
```

**Expected**: lint, format, typecheck, and test all pass; the run completes in under 60
seconds. A run reporting success while executing zero tests is a failure (SC-006) — the
output must show the collected test count.

The convenience form and the plain form must agree (SC-010):

```bash
uv run pytest     # expect the same result as the `test` step above
```

### V-9 — Layering is enforced, not just intended (constitution, Principle I)

```bash
uv run python -c "import ecommerce.domain"     # must succeed with no FastAPI loaded
uv run python -c "import sys, ecommerce.domain; print('fastapi' in sys.modules)"
```

**Expected**: `False`. The domain layer imports without the framework. This is also
asserted in `tests/unit/`, so `make check` catches a regression without this manual step.

---

## What each scenario proves

| Scenario | Requirement | Automated equivalent |
|---|---|---|
| V-1 | SC-001, FR-010, FR-013 | `tests/integration/` wiring; manual because it starts a real server |
| V-2 | FR-005, SC-011, SC-003 | `tests/unit/` version equality; `tests/api/` description parses |
| V-3, V-4 | FR-004 | `tests/integration/` and `tests/api/` switch behaviour |
| V-5 | FR-008, FR-009, SC-004 | `tests/api/` envelope and leakage assertions |
| V-6 | FR-010, FR-011, FR-012 | `tests/unit/` settings defaults and failure messages |
| V-7 | FR-013, FR-014 | Manual — port contention is awkward to simulate reliably |
| V-8 | SC-005, SC-006, SC-007, SC-010 | The suite itself |
| V-9 | Constitution, Principle I | `tests/unit/` import assertion |

## Order to run them

V-8 first, because it is fast and fails loudly if the prerequisites were not fixed. Then
V-1, which needs a running server for V-2 through V-7. V-9 is independent.
