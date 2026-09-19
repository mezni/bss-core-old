# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version history

| Version | Feature Domain | Key Objectives |
|---------|----------------|----------------|
| 0.0.1   | Foundation | Project scaffold, DDD structure, dependencies, config, entry point |

### Legend

- Feature Domain: bounded context (or set of contexts) delivered by the version.
- Key Objectives: main deliverables scoped to that version.

## [Unreleased]

## [0.0.1] - 2026-09-19

### Added

- Initial Rust project scaffold for the telco_si BSS/OSS platform.
- Target architecture:
  - Interfaces → Application → Domain layering with strict dependency rules.
  - Infrastructure implements domain/application ports (SQLx, SQLite, event bus, payments, object storage).
  - Bounded contexts: Subscriber, Inventory, Device, Usage, Rating, Roaming, Billing, Payment, Dunning, Document.

### Planned roadmap

- Phase 1 — Foundation: Cargo config, Actix Web, Tokio, SQLx + SQLite (WAL + foreign keys), config loader, entry point, health endpoints, error-handling conventions, logging/tracing.
- Phase 2 — Subscriber context.
- Phase 3 — Inventory (MSISDN, SIM/IMSI).
- Phase 4 — Device (IMEI).
- Phase 5 — Usage / CDR.
- Phase 6 — Rating engine.
- Phase 7 — Roaming.
- Phase 8 — Billing.
- Phase 9 — Payments.
- Phase 10 — Dunning.
- Phase 11 — Documents / PDF.
- Phase 12 — Production architecture (events, outbox, observability, security, Docker, CI/CD).

The src/ directory is intentionally kept empty (only the hello-world `main.rs`) until
implementation steps are provided incrementally.
