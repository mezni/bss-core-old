# Phase 0 Research: FastAPI Foundation

**Feature**: `002-fastapi-foundation` | **Date**: 2026-09-26

Every `NEEDS CLARIFICATION` from Technical Context is resolved below, together with the
implementation questions the spec leaves open and the three defects planning surfaced in
Phase 0 scaffolding. Each entry states the decision, the reasoning, and what was
rejected, so a later feature can rely on the answer instead of re-deriving it.

---

## D-01: How are dependencies declared so that `uv sync` actually installs them?

**Question**: `[dependency-group.runtime]` and `[dependency-group.development]` are
declared, yet `uv sync` installs nothing and `uv.lock` holds one package. What is correct?

**Decision**: Runtime dependencies go in `[project] dependencies`. Development
dependencies go in `[dependency-groups] dev`. Re-lock with `uv lock` and commit
`uv.lock`.

**Rationale**: `uv sync` installs the project's own dependencies plus the `dev` group by
convention; a PEP 735 group named anything other than `dev` is opt-in and is skipped.
`runtime` and `development` are therefore invisible to the default sync, which is why
`uv sync --dry-run` reports it would *uninstall* the 14 dev packages that were installed
manuscriptly and leave the project with no FastAPI at all. `[project] dependencies` is
also what makes the project correctly installable by any tool, not only uv.

**Alternatives considered**:
- Rename the groups to `dev` and keep both as groups. Rejected: it leaves the runtime set
  out of `[project] dependencies`, so a non-uv install of the package silently omits
  FastAPI. That is a packaging bug waiting for a different tool.
- Add `[tool.uv] default-groups = ["runtime", "development"]`. Rejected: it works, but it
  encodes a uv-specific escape hatch to work around a misdeclaration, and the next
  reader has to discover it. Fixing the declaration is strictly clearer.

**Consequence**: This feature's first task is a correction to `pyproject.toml`, and
`uv.lock` grows from one package to the full transitive set. The constitution's
"`uv.lock` MUST be committed" gate cannot pass until this lands.

---

## D-02: Where does ruff read its configuration?

**Question**: `[project.tool.ruff]` with `print.line-length-limit = 120` — is that honoured?

**Decision**: Rename the section to `[tool.ruff]` and the key to `line-length = 120`.

**Rationale**: `ruff check --show-settings` reports no configured line length, so the
section and the key are both ignored. The project has been running ruff's default of 88
while believing it enforces 120, which means `make format` and `make lint` have been
checking a different rule set than the one the project believes in.

**Alternatives considered**:
- Keep the default of 88 and drop the setting. Rejected: 120 was the stated intent and is
  a reasonable width for a project with wide error envelopes and config tables.
- `line-length` under `[project.tool.ruff]`. Rejected: the section name is still wrong;
  ruff does not read `[project.tool.*]` at all.

---

## D-03: How does `pytest` find `src/`?

**Question**: `python_paths = ["src/"]` is declared. Does pytest honour it?

**Decision**: Rename the key to `pythonpath`.

**Rationale**: `python_paths` is not a pytest ini option, so it is inert. The suite
currently collects only because uv installs the project into the venv as editable, which
puts `src/ecommerce` on the path as a side effect of packaging rather than by
configuration. The setting is misleading: it suggests the path is configured when it is
not. `pythonpath` is the real option (pytest ≥ 7).

**Alternatives considered**:
- Delete the key and rely on the editable install. Rejected: it works today but makes the
  suite depend on installation mode, so a plain `pytest` in a fresh shell against a
  non-installed tree fails for a reason unrelated to the tests.
- Switch to a `src`-less flat layout. Rejected: out of scope and a packaging change with
  no benefit to this feature.

---

## D-04: Which version is published, and how is drift prevented?

**Question**: The spec's clarification fixes the published version as the `APP_VERSION`
setting, with a test asserting the installed package version equals it. Where does the
installed version come from?

**Decision**: The installed version is read from package metadata via
`importlib.metadata.version("ecommerce")`, with `ecommerce.__version__` retained as the
human-readable mirror already present in `__init__.py`. The test asserts
`importlib.metadata.version("ecommerce") == settings.app_version`.

**Rationale**: Package metadata is the value `uv` actually installed and is the only
source that cannot drift from what is on disk. Reading the literal in `__init__.py`
would compare a declared constant against a declared setting — two literals that can
agree while both disagree with the installed distribution. Reading metadata closes the
loop.

Note this yields three places that name a version: `pyproject.toml`, `__init__.py`, and
the `APP_VERSION` default. The test is the guard, exactly as the clarification requires;
`make check` fails if a bump touches only some of them.

**Alternatives considered**:
- Derive `APP_VERSION`'s default from installed metadata, so there is one source. This
  would satisfy the spec's drift clause more elegantly, but it makes an environment
  variable's default depend on installation state, and the clarification explicitly
  chose the setting as the published source. Following the clarification as written.
- Read the literal in `__init__.py` for the comparison. Rejected as above: it does not
  detect drift from the installed distribution.

---

## D-05: What does `API_DOCS_ENABLED=false` actually disable?

**Question**: `docs/configuration.md` §11 says the switch "hides `/docs` and
`/openapi.json`, but **not** the schema itself from anyone who knows the path". Those two
clauses cannot both hold, because `/openapi.json` is how the schema is served. Which
reading is implementable?

**Decision**: `API_DOCS_ENABLED=false` sets both `docs_url` and `openapi_url` to `None`,
so `/docs` and `/openapi.json` both return 404. `API_REDOC_ENABLED=false` sets
`redoc_url` to `None`, so `/redoc` returns 404. The "not a security control" clause is
retained as intent, not as behaviour.

**Rationale**: FastAPI serves the schema at exactly one URL, `openapi_url`, and the
document names no second path. The only reading under which the schema "remains
retrievable by someone who knows the path" would require inventing an undocumented
second endpoint, which would itself be unspecified behaviour. The clause is therefore
best read as a warning — do not treat these switches as protecting anything sensitive —
and that warning is preserved in the code comments and in the spec.

The independent-switch requirement is satisfied by construction: the two flags map to
disjoint URL parameters, so turning one off cannot affect the other, and neither affects
`/health`, which is registered independently of the description URLs.

**Alternatives considered**:
- Keep the schema served at a second, private path. Rejected: no such path is specified
  anywhere, and inventing one creates an undocumented endpoint — a direct violation of
  the constitution's "MUST NOT introduce substantial undocumented functionality".
- Treat the sentence as authoritative over the framework and fail startup on
  contradiction. Rejected: a documentation ambiguity is not a reason to refuse to start.

**Consequences**:
1. The spec's FR-004 sentence — "a consumer who knows the path can still retrieve the
   schema" — describes behaviour this decision does not implement. FR-004 is corrected to
   state that the switches are not a security boundary, dropping the retrieval claim.
2. `docs/configuration.md` §11 needs a wording fix so the published contract stops
   contradicting itself. Tracked as a task.

---

## D-06: How is the request identifier produced without building the observability phase?

**Question**: FR-008 requires every error to carry a request identifier, and the
constitution places request logging and metrics in the observability phase. What is the
minimum that satisfies the spec without pre-empting that phase?

**Decision**: A single `observability/request_id.py` module provides the identifier
resolution, used by the error handler and nowhere else. It honours an inbound
`X-Request-ID` header when present and generates a UUID4 otherwise, exposes no metrics,
writes no logs, and registers no middleware beyond attaching the value to the request
state.

**Rationale**: The error envelope mandates `request_id` on every failure, so something
must produce it. A dedicated module keeps that one responsibility named and gives the
observability feature an obvious seam to grow into, without this feature guessing at log
formats, metric names, or trace propagation — all of which are that phase's decisions and
would be churn if invented here.

**Alternatives considered**:
- Generate the identifier inside the error handler. Rejected: it couples identifier
  policy to error formatting, and the observability phase would have to unpick it to
  correlate non-error requests.
- Trust an inbound `X-Request-ID` unconditionally. Rejected: an unbounded client-supplied
  value is echoed into every error response, which is a log-injection and header-injection
  surface. Truncating and character-screening the value before echoing is the minimum
  acceptable handling, and the module owns it.
- Implement full request logging now. Rejected: out of scope by FR-018, and the log
  format is a published decision owned by the observability phase.

---

## D-07: How is the versioned namespace reserved without a placeholder route?

**Question**: The clarification dropped the requirement that the empty versioned
namespace appear in the machine-readable description. What actually reserves it?

**Decision**: Create a router carrying the configured prefix, register it with the
application, and mount it with no routes. The namespace is thereby reserved in the
routing table and configurable, and it appears in the generated description the moment
the first route is added to it — which Story 3 does.

**Rationale**: The prefix is applied by the router itself, so a route added later
inherits the versioned path with no second registration step, which is what FR-007
requires. A description generated from an empty router is valid and simply has no paths,
which is a truthful report: there are no versioned endpoints yet. A placeholder route
would have made the description claim an endpoint that does not exist.

**Alternatives considered**:
- Mount a placeholder route until the first business feature. Rejected by the
  clarification, and it would put a fake endpoint in a published contract.
- Leave the router unmounted and add it with the first feature. Rejected: then the
  configurable prefix has no exercised code path in this phase, and FR-006's requirement
  that the prefix come from configuration would be untested until much later.

**Consequence**: Story 2's acceptance scenario 4 was rewritten during clarification to
require a *mounted* route rather than an empty namespace, so the observable proof lives
in `tests/api/` with a route present.

---

## D-08: How is the error envelope produced for every failure class?

**Question**: The constitution requires internal exceptions never to be exposed, and one
consistent envelope. Which handlers does this phase need?

**Decision**: Two handlers, both emitting the same four-field envelope:
`HTTPException` (and FastAPI's own `RequestValidationError`, which subclasses it) mapped
to its published status, and a catch-all `Exception` handler mapped to 500 with
`INTERNAL_ERROR`. Route-level 404s are produced by the router's default handler, so they
pass through the same path. The generic handler logs the traceback server-side and returns
a fixed message with no exception text, path, or frame in the body.

**Rationale**: A catch-all is the only way to satisfy FR-009 for unanticipated
exceptions, and mapping it to a fixed message is what keeps stack traces out of
responses. Because both handlers build the envelope through one function, the four fields
and the always-array `details` rule hold by construction rather than by convention.

**Alternatives considered**:
- One handler keyed on exception type. Rejected: same outcome, more branching, and a new
  exception type would silently bypass it.
- Translate every internal error into a domain-specific code now. Rejected: there are no
  domain errors yet, and inventing codes the spec does not require would put unpublished
  codes in a published contract.

---

## D-09: What is the test strategy for a feature whose subject is "the server runs"?

**Question**: SC-006 treats a run that executes zero checks as a failure, and SC-005
requires injected breakage to be detected. How is that achieved?

**Decision**: Three layers, matching the constitution's directories.
`tests/unit/` covers settings defaults, the fail-fast message naming a bad setting, the
version-equality assertion, and an import check proving `ecommerce.domain` imports
without FastAPI present. `tests/integration/` constructs the application through the
factory and asserts wiring: the versioned router is mounted under the configured prefix,
and each description switch produces the expected URL registration. `tests/api/` drives
the ASGI app in-process: the `/health` payload is exactly the published one, the
description parses and lists the mounted route, each switch's disabled state 404s while
the other description and `/health` still answer, and an unknown path returns the
four-field envelope with no leaked path or traceback.

**Rationale**: In-process ASGI testing removes port binding and server lifecycle from the
suite, which is what keeps the run inside SC-007's 60-second budget and makes it
order-independent as Principle IV requires. The import check is the only automated
enforcement of Principle I, and it is cheap.

**Alternatives considered**:
- Spawn a real Uvicorn subprocess per test. Rejected: slower, flakier, and it tests the
  deployment rather than the application. The real server is still validated — by
  `quickstart.md`, once, by a human or by an explicitly invoked check.
- One end-to-end test covering everything. Rejected: a single failure then gives no
  signal about which behaviour broke, which is the opposite of what SC-005 needs.

---

## D-10: Does this feature need `SQLAlchemy`, `Alembic`, or `Faker` installed?

**Question**: The constitution's baseline lists them, and `pyproject.toml` declares them,
but this phase has no persistence and no data.

**Decision**: Keep them declared in `[project] dependencies` so `uv.lock` reflects the
constitution's baseline, but import none of them in this feature. The health check
asserts at test time that the liveness route's module graph contains no database import.

**Rationale**: Removing them would make `uv.lock` a partial record of the mandated stack
and would force a lock change again when persistence arrives. Declaring a dependency is
not using it. The import assertion is what actually enforces FR-003, and it is stronger
than a code-review convention because it fails automatically.

**Alternatives considered**:
- Trim the dependency list to what Phase 1 uses. Rejected: the constitution mandates the
  baseline, and a lock that grows one dependency group at a time is noisier in review
  than one that records the intended stack up front.
