# Contract: Developer Command Surface

**Feature**: `001-project-foundation` | **Status**: binding | **Date**: 2026-09-26

This is the interface a contributor, a reviewer, and any future CI job program against.
Its stability requirement is FR-017 and SC-009: every documented convenience command maps
one-to-one to a plain command that can be run without the convenience layer, and the two
behave identically.

---

## 1. The two-command path

The whole point of the phase. A contributor on a clean checkout runs exactly these:

| Step | Command | Success signal |
|---|---|---|
| Install | `uv sync` | exit 0, resolved versions match the committed `uv.lock` |
| Verify | `make check` | exit 0 |

Both are also available as `make install` and `make check`. Any other spelling of either
step is not part of this contract.

SC-001 holds that this path takes at most two commands and under ten minutes.

## 2. Target inventory

Ten targets are `available` in this phase. Each row's *plain command* column is the
contract: it MUST work exactly as written, from the project root, with no environment
activated and no prior `make` invocation.

| Target | Plain command | Purpose | Status |
|---|---|---|---|
| `help` | *(prints the target list; no wrapped command)* | Discover the surface | available |
| `install` | `uv sync` | Install runtime and development dependencies | available |
| `test` | `uv run pytest` | Run the whole suite | available |
| `test-unit` | `uv run pytest tests/unit` | Run unit checks only | available |
| `coverage` | `uv run pytest --cov=src/ecommerce --cov-report=term-missing` | Suite with a coverage report | available |
| `lint` | `uv run ruff check .` | Lint | available |
| `format` | `uv run ruff format .` | Rewrite formatting | available |
| `typecheck` | `uv run mypy src` | Type check | available |
| `check` | the six checks below, chained | Full verification | available |
| `clean` | remove caches and the local database file | Reset the working tree | available |

### 2.1 `make check` composition

`make check` MUST run these six, in this order, aborting at the first failure and
propagating its non-zero exit status (FR-019):

1. `uv run ruff check .`
2. `uv run ruff format --check .`
3. `uv run mypy src`
4. `uv run pytest`
5. `uv run python scripts/check_repo_hygiene.py`
6. `uv run python scripts/check_config_template.py`

Sequential order is part of the contract, not an implementation detail: a contributor
reading a failure needs the earliest problem reported first, and a formatting failure
reported after a type failure is materially more annoying to act on.

### 2.2 Published but not yet available

`docs/development.md` §31 publishes sixteen targets. The remaining eleven are `planned`
in this phase, because their wrapped commands do not exist yet:

`bootstrap`, `migrate`, `migrate-new`, `migration-status`, `seed`, `seed-test`,
`seed-large`, `seed-args`, `reset`, `db-reset`, `run`

A `planned` target MUST be visible as planned — in the Makefile help output and in the
documentation. It MUST NOT be silently absent, and it MUST NOT be present and fail every
time it is run (research D16).

## 3. Failure contract

| Situation | Required behaviour |
|---|---|
| Any check fails | Non-zero exit; the message identifies what needs attention (FR-019) |
| `uv.lock` disagrees with the declarations | Install fails with an actionable message; it MUST NOT silently resolve different versions |
| Interpreter older than 3.12 | Install fails with a message naming the required version |
| Interpreter newer than 3.12 | Install and checks succeed; nothing may claim the newer version was verified |
| A declared dependency is neither imported nor marked `later phase (<n>)` | `check` fails, naming the dependency |
| A tracked file matches the ignore rules, or a tracked file contains a secret-shaped assignment | `check` fails, naming the path |
| `.env.example` and `docs/configuration.md` §42 disagree on the key set | `check` fails, listing missing and extra keys |
| Test run collects nothing | `check` MUST fail. Success by collecting nothing is forbidden (FR-020) |
| A target is run from outside the project root | Defined behaviour — works, or fails with a clear message. Never a partial run |

## 4. Change rules

- Adding a target requires adding its plain command to `docs/development.md` in the same
  change. A target with no documented plain command violates FR-017.
- Renaming a target or changing a plain command is a breaking change: recorded in
  `CHANGELOG.md` in the same change (FR-016).
- Moving a target from `planned` to `available` requires its wrapped command to work
  first. The transition updates the Makefile, the help text, and `docs/development.md`
  §31 together.
- A target MUST NOT introduce a second dependency manager, build system, or test runner
  to achieve something the documented toolchain already does (FR-006, FR-008).

## 5. Explicitly not in this contract

- Any HTTP endpoint. Phase 1.
- `alembic` commands. Phase 2.
- Seed or generator commands. A later feature; the `seed` module is not created here.
- Continuous integration. Out of scope per the specification's Assumptions. If added, it
  MUST invoke only the plain commands in §2, and MUST NOT depend on a developer-local
  file.
