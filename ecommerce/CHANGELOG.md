# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Pre-release.** The project has no released version. Everything below is unreleased work in
> progress.

---

## [Unreleased]

### Added

#### Governance

- **Constitution v1.1.0** — replaced all template placeholders with a concrete governance baseline
  for the Fake E-Commerce Server:
  - Five core principles — Domain Independence, Determinism and Reproducibility, Explicit Business
    Rules, Testability and Isolation, Simple Local Development.
  - Technology stack and API design constraints (Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy
    2.x, Alembic, SQLite, pytest, HTTPX, uv).
  - Database and data management rules (Alembic-only schema management; no
    `Base.metadata.create_all()` as the primary mechanism).
  - Development workflow and feature-completion criteria.
  - **Speckit Development Process** — mandates that all Spec Kit output lives under `specs/`, with
    a sequential `NNN-slug/` layout and a roadmap of independently implementable features.
  - Project documentation layout requirement.
  - Security, observability, error-envelope, and configuration requirements.
  - Governance: amendment procedure, semantic versioning policy, compliance expectations.
- **Constitution v1.0.0** — initial substantive ratification of the governance baseline.

#### Specifications

- Feature roadmap scaffolded under `specs/`:
  `001-foundation`, `002-product-catalog`, `003-customers`, `004-cart`, `005-orders`,
  `006-inventory`, `007-payments`, `008-fake-data-generator`, `009-failure-simulation`,
  `010-authentication`, `011-observability`.
- `specs/README.md` — feature roadmap, per-directory artifact layout, and the working workflow.

#### Documentation

- `README.md` — project entry point: purpose, features, technology stack, installation, running
  migrations, generating fake data, running tests, and example API requests.
- `CHANGELOG.md` — this file.
- `docs/PRD.md` — product requirements: users and roles, functional requirements per bounded
  context, checkout workflow, fake-data generation, failure simulation, non-functional
  requirements, and explicit out-of-scope items.
- `docs/plan.md` — implementation plan: technology stack, architectural approach, project
  structure, 16 implementation phases with objectives/tasks/completion criteria, migration and
  repository strategy, quality gates, and definition of done.
- `docs/architecture.md` — layering and dependency direction, layer responsibilities, bounded
  contexts, module layout, repository pattern, transaction and consistency strategy, database
  architecture, external systems and fake providers, determinism strategy, and extensibility.
- `docs/API.md` — HTTP contract: conventions, money representation, error format and stable error
  codes, status codes, pagination/filtering/sorting, authentication and authorization, resource
  schemas, and the full endpoint table per bounded context.
- `docs/database.md` — SQLite persistence model: table-by-table columns and constraints, entity
  relationships, constraint strategy, index rationale, transaction guidance, migration strategy,
  SQLite-specific behavioral caveats, and test database policy.
- `docs/generator.md` — fake-data generator: scope, CLI options, dataset profiles, determinism
  guarantees, generation order, validation checks, realistic data distributions, reset semantics,
  transaction handling, test-data reuse, architecture, and failure behavior.
- `docs/configuration.md` — environment variables, per-environment behavior for
  development/test/production, `.env.example` contract, precedence rules, failure-simulation
  defaults, and startup validation.
- `docs/testing.md` — testing strategy: `unit`/`integration`/`api` layout, test database policy,
  fixtures, generator reuse, determinism controls, per-tier coverage, failure scenario matrix, and
  isolation rules.
- `docs/failure-simulation.md` — failure simulation: principles, scenario table, triggering
  mechanisms, determinism guarantee, per-scenario behavior and required end state, implementation
  boundaries, safety rules, and test matrix.
- `docs/development.md` — developer workflow: prerequisites, setup, database, fake data, running
  the server, calling the API, testing, Makefile targets, feature workflow, and troubleshooting.

### Known Issues

- **C1 — Spec feature decomposition undecided.** `docs/plan.md` §30 proposes a 16-feature
  breakdown in which the fake-data generator is `010-fake-data-generator`, while the `specs/` tree
  uses an 11-feature breakdown in which it is `008-fake-data-generator`. The 11-feature layout is
  currently authoritative. A decision is required before any `/speckit.specify` run creates
  `012-`+ directories. See `docs/plan.md` §30.
- **C2 — Constitution path resolved.** `docs/plan.md` originally listed `constitution.md` at the
  repository root; the authoritative location is `.specify/memory/constitution.md`. Resolved.
- **C3 — Generator entrypoint resolved.** `python -m ecommerce.seed` (constitution §20) requires
  `seed/__main__.py`; the original structure omitted it. Resolved by including it.

---

## Future Releases

Planned, in roadmap order. See [`specs/README.md`](specs/README.md).

- `001-foundation` — project scaffolding, configuration, logging, error envelope, `GET /health`,
  Alembic baseline.
- `002-product-catalog` — categories, products, search, filtering, pagination, CRUD.
- `003-customers` — registration, profile, status lifecycle.
- `004-cart` — cart lifecycle, cart items, quantity rules, pricing.
- `005-orders` — order lifecycle, order items, state transitions.
- `006-inventory` — stock levels, reservation, release, conflict detection.
- `007-payments` — payment states, synthetic fake payment provider.
- `008-fake-data-generator` — deterministic fake-data generator and CLI.
- `009-failure-simulation` — deterministic and randomized failure injection.
- `010-authentication` — fake authentication and explicit authorization rules.
- `011-observability` — request IDs, structured logging, domain events, health checks.

[Unreleased]: https://example.invalid/ecommerce/compare/v0.0.0...HEAD
