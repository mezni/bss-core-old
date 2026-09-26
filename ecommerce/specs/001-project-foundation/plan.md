# Implementation Plan: Project Foundation (Phase 0)

**Branch**: `001-project-foundation` (not created — no branch hook registered) | **Date**: 2026-09-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-project-foundation/spec.md`

## Summary

Deliver Phase 0 of `docs/plan.md` §6: a repository that a new contributor can install,
configure, verify, and test in two commands, reproducibly and without leaking anything.

The technical approach is to adopt the project's chosen tooling end to end rather than
assemble it from parts. A `uv`-managed project with a `src/` layout and the `uv_build`
backend gives a single importable package, a committed lockfile, and an interpreter
pinned to the version this feature is verified on — which is what makes the spec's
reproducibility criteria true rather than aspirational. Around that core, four small
standard-library checks (`ruff`, `mypy`, `pytest`, and two repository-hygiene scripts)
turn the spec's success criteria into assertions a contributor can run, and the two
published documents that contributors read first — `README.md` and `.env.example` — are
restructured to carry an explicit availability marker, so a documented command can never
be mistaken for a runnable one.

No application code, no database, and no domain model are created. The layer subpackages
published in `docs/architecture.md` are deliberately left uncreated; each is introduced
by the phase that first puts code in it (research D15).

## Technical Context

**Language/Version**: Python 3.12+ accepted; verified on 3.12 only (clarification 5).
Pinned by `requires-python = ">=3.12"` plus a committed `.python-version` = `3.12`
(research D2).

**Primary Dependencies**: fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy,
alembic, httpx, faker (runtime); pytest, ruff, mypy, pytest-cov (development). All
runtime declarations are recorded in `docs/development.md` with a *Declared for* value;
several are declared for Phases 1–2 of this same feature (research D5, D6, D7).

**Storage**: N/A in this phase. No database, no schema, no migrations — SQLite and Alembic
arrive in Phase 2. The `data/` directory is created and ignored, nothing writes to it yet.

**Testing**: pytest, with the three mandated areas `tests/unit/`, `tests/integration/`,
`tests/api/` each holding a tracked `README.md`; `tests/unit/test_package.py` is the
minimum real check that keeps a clean run from passing by collecting nothing
(research D11, D12).

**Target Platform**: Linux, macOS, or Windows developer workstation with a supported
CPython 3.12+. Verification is performed on 3.12; newer interpreters are accepted but
unverified (FR-002). No CI pipeline is introduced — out of scope per the spec's
Assumptions, and if one is added later it MUST consume the documented commands only.

**Project Type**: Python library/tooling foundation for a modular-monolith web service.
This phase delivers the project skeleton and its developer-facing command surface; the
web service itself is Phase 1.

**Performance Goals**: the full check run completes in under 60 seconds from a clean
checkout (SC-005); a contributor reaches a verified environment in under 10 minutes and
at most two documented commands (SC-001).

**Constraints**: the dependency resolution is committed and never hand-edited (FR-003);
no second dependency manager, build system, or test runner (FR-006, FR-008, FR-017);
the project stays a modular monolith with no services, brokers, or distributed runtime
(FR-008); every declaration carries a recorded purpose (FR-005).

**Scale/Scope**: one importable package, zero endpoints, 12 dependency declarations, 30
documented configuration variables, 10 available convenience commands, 3 test areas.

## Constitution Check

*GATE: evaluated before Phase 0 research and re-evaluated after Phase 1 design.*

**Authority**: `.specify/memory/constitution.md` v1.1.1.

| Gate | Requirement | Verdict | Evidence |
|------|-------------|---------|----------|
| I. Domain Independence | Domain MUST NOT import framework libraries | **Pass** | No domain code exists in this phase. The single package created is a version-bearing namespace only, importing nothing (research D15). |
| II. Determinism | Behaviour deterministic given the same inputs | **Pass** | The committed lockfile plus `uv sync` is the mechanism; SC-003 is directly checkable. `RANDOM_SEED`, `FAKE_CLOCK`, and `SEED_PROFILE` are documented in `.env.example` with planned markers rather than silently omitted. |
| III. Explicit Business Rules | Rules enforced by domain/application logic | **N/A** | No business behaviour is delivered in this phase. Recorded so the omission is visible, not silent. |
| IV. Testability & Isolation | `tests/{unit,integration,api}`, no order dependence, dedicated test data | **Pass** | All three areas created and tracked (FR-021, SC-012); one order-independent smoke check; no test touches development data because no database exists yet. |
| V. Simple Local Development | Modular monolith; small number of commands; abstractions must earn their place | **Pass** | Two commands to a verified environment (SC-001); one dependency manager, one build backend, one test runner; five layer subpackages deliberately **not** pre-created (research D15). |
| Technology Stack | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, SQLite, pytest, HTTPX, uv; `uv.lock` committed | **Pass** | Declared per `docs/plan.md` §6; `uv.lock` committed (FR-003). SQLite and Alembic are declared but unused until Phase 2, which is recorded in the dependency-purpose table rather than hidden. |
| Database & Data Management | Alembic-only schema management; no `create_all()` | **N/A** | No schema in this phase. |
| Development Workflow | `specs/` is canonical; behaviour specified before implementation; docs updated with behaviour | **Pass** | This feature lives in `specs/001-project-foundation/`; `README.md`, `docs/development.md`, and `CHANGELOG.md` updates are in scope (FR-015, FR-016). |
| Project Documentation Layout | `README.md`, `CHANGELOG.md`, `docs/*`, secret-free `.env.example`, `.gitignore` | **Pass** | The layout already exists; this phase brings `README.md` and `.env.example` into line with FR-009/FR-015 and adds `.gitignore` (FR-013). |
| Security & Observability | Externalised config; no committed secrets; error envelope; `GET /health` | **Partial — N/A this phase** | Externalised config and secret hygiene are in scope and enforced (FR-009–FR-014, D8). The error envelope, `GET /health`, and logging belong to Phases 1–2 of this feature. |
| Governance | Conflicts identified, not silently resolved | **Pass, with one deferred conflict** | See below. |

**Gate result: PASS.** No unjustified violation. Complexity Tracking is therefore empty.

**Note on the sensitive-key set.** `scripts/check_repo_hygiene.py` must fail on a tracked
file that assigns a non-empty value to a sensitive key. `docs/configuration.md` §42 marks
exactly one setting sensitive (`AUTH_FAKE_TOKEN_SECRET`), so that reference alone gives the
script a one-entry list. The script therefore also matches a generic
`(SECRET|TOKEN|PASSWORD|API_KEY)` pattern, which is a superset of the reference. If
`sensitive` markings are ever added to §42, the reference list is the authority and the
generic pattern remains the backstop; the two must not be treated as equal.

**Deferred conflict, recorded not resolved.** The constitution's *Speckit Development
Process* section enumerates `001-foundation` … `011-observability` as the feature layout;
the repository now contains only `001-project-foundation`. Per clarification 2 this
enumeration is read as an illustrative roadmap, and the divergence is carried as a
deferred conflict to be resolved when the second feature is specified. It does not block
this phase, and no requirement of this plan depends on the old slugs.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-foundation/
├── spec.md                 # the specification (input, unchanged by this command)
├── plan.md                 # this file
├── research.md             # Phase 0 output — 16 decisions, all clarifications resolved
├── data-model.md           # Phase 1 output — configuration, dependency, and command records
├── quickstart.md           # Phase 1 output — runnable validation of SC-001 … SC-012
├── checklists/
│   └── requirements.md     # spec quality checklist, 16/16
├── contracts/
│   ├── README.md           # contract index and rationale
│   ├── developer-commands.md   # the command surface contract (FR-017, SC-009)
│   └── config-template.md      # the .env.example format contract (FR-009, SC-007)
└── tasks.md                # Phase 2 output — NOT created by /speckit.plan
```

### Source Code (repository root)

Everything below is created by this phase. Paths not listed do not exist yet.

```text
.
├── pyproject.toml              # project metadata, deps, ruff + mypy + pytest config
├── uv.lock                     # committed resolution (FR-003)
├── .python-version             # 3.12 — the verified interpreter (D2)
├── .gitignore                  # .env, data/, .venv, caches, build artifacts (FR-013)
├── .env.example                # 30 settings, secret-free, each with a status marker
├── Makefile                    # 10 available targets; 11 marked planned (D16)
├── README.md                   # restructured: works today + target workflow (D13)
├── CHANGELOG.md                # entry added in the same change (FR-016)
├── alembic.ini                 # NOT created — Phase 2
├── docs/
│   ├── development.md          # gains the dependency-purpose table (D6) and target status (D16)
│   └── configuration.md        # unchanged; it is the source of truth for .env.example
├── scripts/
│   ├── check_repo_hygiene.py   # ignored-path and secret scan (D8)
│   └── check_config_template.py# .env.example vs configuration.md §42 coverage (D9)
├── src/
│   └── ecommerce/
│       └── __init__.py         # __version__ only; the single importable package (D1, D14, D15)
└── tests/
    ├── unit/
    │   ├── README.md           # what belongs here (D12)
    │   └── test_package.py     # import + version assertion (D11)
    ├── integration/
    │   └── README.md           # tracked so the area survives a fresh clone (D12)
    └── api/
        └── README.md           # tracked so the area survives a fresh clone (D12)
```

**Not created, and why**: `src/ecommerce/{api,application,domain,infrastructure,config,seed}/`,
`alembic.ini`, `migrations/`, `data/`, and the FastAPI entrypoint. Creating empty layer
packages would pre-empt Phases 1–2, the generator, and the observability feature, and
constitution Principle V requires a demonstrated purpose for every abstraction (research
D15). `data/` is ignored and created at runtime by Phase 2 infrastructure.

**Structure Decision**: single `src/`-layout project — Option 1 of the template, chosen
because this project is one deployable modular monolith and the option's structure maps
directly onto the spec's "exactly one importable source package" (FR-007). The `tests/`
tree follows the constitution's mandated `unit` / `integration` / `api` split rather than
the template's default `unit` / `integration` / `contract`, because the constitution is
authoritative and names the three areas explicitly. Options 2 and 3 are deleted: there is
no frontend and no mobile client in this project.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Empty. The Constitution Check gate passed with no unjustified violation.

Two additions were considered and rejected as unjustified complexity before reaching
this table: the pre-commit framework (research D8) and a generated `.env.example`
(research D9). Both were declined under Principle V, and neither is recorded here as a
violation because neither is being adopted.

## Re-checked After Phase 1 Design

| Gate | Verdict | Change from the pre-research check |
|------|---------|--------------------------------------|
| I. Domain Independence | Pass | Unchanged. The Phase 1 artifacts describe configuration and command records, not domain entities; no framework import is introduced. |
| II. Determinism | Pass | Strengthened. `data-model.md` gives the Configuration Setting record a fixed "declared for" value, which is the input the reproducibility criteria depend on. |
| IV. Testability & Isolation | Pass | Strengthened. `quickstart.md` maps each success criterion to a runnable command, so SC-001–SC-012 are verifiable rather than asserted. |
| V. Simple Local Development | Pass | Unchanged. The command surface in `contracts/developer-commands.md` exposes 10 targets and marks 11 as planned, so nothing is promised that cannot run. |
| Security & Observability | Partial — N/A this phase | Unchanged. The error envelope, `GET /health`, and logging remain Phase 1–2 work; secret hygiene is enforced now. |
| Governance | Pass, one deferred conflict | Unchanged and now recorded in `research.md` D6 and in the dependency-purpose table, so the deferred nature of the fastapi/uvicorn/sqlalchemy/alembic/httpx declarations is visible rather than implied. |

**Post-design gate result: PASS.** No design decision introduced a violation.
