# Data Model: Project Foundation (Phase 0)

**Feature**: `001-project-foundation` | **Date**: 2026-09-26 | **Plan**: [plan.md](plan.md)

Phase 0 persists **no domain data**. There is no database, no schema, and no migration
in this phase — SQLite and Alembic arrive in Phase 2. What follows are the *records* the
foundation maintains in version-controlled files, described as entities because each has
attributes, validation rules, and in two cases a lifecycle that later features extend.

Each record below maps to exactly one file, and that file is the only place the fact
lives. Nothing is duplicated into a second document; where a second file must reference
a record, it references the file, not a copy of its contents.

---

## Configuration Setting

**Represents**: one externally supplied value that affects behaviour.
**Stored in**: `.env.example` (committed, secret-free, exhaustive) and documented in
`docs/configuration.md` §42, which is the authoritative reference. The check
`scripts/check_config_template.py` compares the two key sets (research D9).

**Volume**: exactly 30 settings — the full published reference, including the two marked
*Reserved* (`METRICS_ENABLED`, `TRACING_ENABLED`) and the one sensitive setting
(`AUTH_FAKE_TOKEN_SECRET`).

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | identifier | yes | Upper snake case. Must be a member of the published reference key set; the check fails on a key present in one file and absent from the other. |
| `type` | enum | yes | One of `str`, `int`, `float`, `bool`, `enum`, `list`, ISO-8601 timestamp. |
| `default` | value or *unset* | yes | Must equal the reference default. An unset default is written as *(unset)*, never as an empty string masquerading as a value. |
| `purpose` | text | yes | One line, stating the effect, not the mechanism. |
| `validation_rule` | text | conditional | Required for constrained values: enum membership, numeric range, or format. Omitted only for unconstrained types. |
| `status` | enum | yes | `honoured` or `planned (<phase>)`. **A missing status is non-conforming** (FR-009, clarification 3). |
| `sensitive` | boolean | yes | True only for `AUTH_FAKE_TOKEN_SECRET`. A sensitive setting ships commented out with a synthetic value and MUST NOT carry a real credential (FR-010). |
| `environments` | list | yes | `all`, or a subset of development / test / production. |

**Lifecycle**: `planned (<phase>)` → `honoured` when the phase that reads the setting
lands. The transition is a one-word edit in `.env.example` plus the corresponding runtime
change; the check does not permit a setting to be `honoured` without the runtime that
reads it, which is the invariant behind the spec's edge case "a setting takes effect at
runtime but is absent from the template".

**Validation rules that must fail loudly**: a key in `.env.example` that the reference
does not define; a reference key absent from `.env.example`; an entry with no status
token; a default that disagrees with the reference.

---

## Dependency Declaration

**Represents**: one third-party capability the project relies on.
**Stored in**: `pyproject.toml` (the declaration) and `docs/development.md` → *Dependency
purposes* table (the record of purpose). The declaration and the record are read
together by `scripts/check_repo_hygiene.py` (research D6, D7).

**Volume**: 12 declarations — the 9 named in `docs/plan.md` §6 (of which pytest is a
development dependency) plus ruff, mypy, and pytest-cov.

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | identifier | yes | Must match a PyPI distribution name. |
| `scope` | enum | yes | `runtime` or `development`. A `development` dependency MUST NOT be required to run the application (FR-004). |
| `declared_for` | enum | yes | `phase 0` or `later phase (<n>)`. This is the allow-list that keeps the unused-dependency check from failing on the project's own correct state (research D7). |
| `purpose` | text | yes | One line. Its absence fails FR-005 and SC-004. |
| `duplicate_justification` | text | conditional | Required only when the dependency duplicates a capability the project already has. Its absence fails FR-006. |
| `resolved_version` | version | yes | Recorded once, centrally, in the committed `uv.lock`. Never hand-edited (FR-003). |

**Lifecycle**: `proposed` → `accepted` (recorded in the table, lockfile regenerated) or
`rejected` (a note in the table explaining which existing capability already covers it).
A dependency is never added to `pyproject.toml` in the same change that omits it from the
table.

**Validation rules that must fail loudly**: a declared dependency absent from the table;
a table entry absent from `pyproject.toml`; a declaration that is neither imported
anywhere in `src/` or `tests/` nor marked `later phase (<n>)`; a hand-edited `uv.lock`,
detected as a declaration/resolution mismatch by `uv sync` itself.

---

## Convenience Command

**Represents**: a named task wrapping a plain documented command.
**Stored in**: `Makefile` (the target) and `docs/development.md` §31 (the published
list). The contract is `contracts/developer-commands.md`.

**Volume**: 10 available (`help`, `install`, `test`, `test-unit`, `coverage`, `lint`,
`format`, `typecheck`, `check`, `clean`); 11 published but marked `planned` in this phase
(`bootstrap`, `migrate`, `migrate-new`, `migration-status`, `seed`, `seed-test`,
`seed-large`, `seed-args`, `reset`, `db-reset`, `run`).

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | identifier | yes | The word a contributor types after `make`. |
| `wraps` | command | yes | The exact plain command, runnable without `make`. A target that performs work its wrapped command does not is non-conforming (FR-017, SC-009). |
| `purpose` | text | yes | One line. |
| `status` | enum | yes | `available` or `planned`. A `planned` target MUST be visible as planned in the Makefile help output and in the documentation — never silently missing, never present and always failing (research D16). |

**Lifecycle**: `planned` → `available` when the wrapped command starts working. The
transition updates the Makefile, the help text, and `docs/development.md` §31 together.

**Validation rules that must fail loudly**: an `available` target whose wrapped command
exits non-zero; a documented command that appears in no target and in no documented
plain form; a `planned` target that is nonetheless runnable without being marked
available.

---

## Automated Check

**Represents**: a runnable verification step contributing to `make check`.
**Stored in**: the tool's own configuration in `pyproject.toml`, plus the two standalone
scripts under `scripts/`.

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | identifier | yes | `lint`, `format-check`, `typecheck`, `test`, `repo-hygiene`, `config-template`. |
| `reports` | text | yes | What a failure tells the contributor to fix (FR-019). A check that cannot fail is non-conforming. |
| `exit_signal` | non-zero integer | yes | Propagated by `make check`'s `&&` chain; the first failure aborts the run. |

**Volume**: 6 checks. Two are tool-native (`ruff check`, `ruff format --check`, `mypy`,
`pytest`); two are the project scripts from research D8 and D9.

**Validation rules that must fail loudly**: a check that exits zero on a deliberately
injected violation — the four injection cases named in SC-006 are formatting drift, a
failing test, an unused dependency, and a staged local configuration file.

---

## Test Area

**Represents**: one of the three mandated test categories.
**Stored in**: `tests/unit/README.md`, `tests/integration/README.md`,
`tests/api/README.md`.

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | enum | yes | `unit`, `integration`, or `api` — the three areas the constitution mandates. |
| `covers` | text | yes | What belongs here. |
| `must_not` | text | yes | What must never appear here, e.g. execution order dependence, or mutation of development data (FR-022). |
| `tracked` | boolean | yes | Must be true. An area holding no tracked file is absent from a fresh clone and FR-021 is unverifiable (clarification 4, SC-012). |
| `test_module_count` | integer | derived | `unit` = 1 in this phase; `integration` and `api` = 0. |

**Validation rules that must fail loudly**: a missing area; an area with no tracked file;
a test module outside `tests/unit/` in this phase.

---

## Documentation Set

**Represents**: the entry-point document and the published design documents a contributor
or stakeholder reads.

| Attribute | Type | Required | Rule |
|---|---|---|---|
| `name` | identifier | yes | `README.md`, `CHANGELOG.md`, or a document under `docs/`. |
| `audience` | text | yes | Who reads it first. |
| `update_obligation` | text | yes | The condition that forces an update in the same change (FR-016). |
| `status_markers_present` | boolean | conditional | Required for `README.md` only: every documented command carries a status token (FR-015, clarification 1). |

**Relationships**: `README.md` summarises and links the `docs/` set rather than
restating it; `.env.example` is validated against `docs/configuration.md` §42 rather than
documented twice; `CHANGELOG.md` records the change in the same commit that makes it.

---

## What is deliberately absent

| Absent | Why |
|---|---|
| Domain entities (Product, Customer, Cart, Order, Inventory, Payment) | Belong to features 002–007. Phase 0 creates no domain model. |
| Money as a value object | Representation is already settled project-wide as integer minor units (constitution, divergence A5). No value object exists yet to define. |
| Idempotency keys, request IDs, audit rows | Belong to the observability feature. |
| Database tables | Phase 2. |
| A `data/` directory entry | Created at runtime by Phase 2 infrastructure; ignored, not tracked. |
