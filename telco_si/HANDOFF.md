# Session Handoff

_Last updated: 2026-09-19_

## Project

**telco_si** — Production-oriented Rust BSS/OSS platform.
Stack: Actix Web + Tokio + SQLx + SQLite, organized with Domain-Driven Design.

## Goal / Working agreement

Build the platform **incrementally**. The user dictates each step and writes the
code themselves in a step-by-step fashion. The assistant:
- Does **not** write application code proactively.
- Explains *why* / DDD concepts when asked.
- Can review code, run builds/tests, and verify.

## Current state

- `Cargo.toml` — minimal skeleton, **no dependencies yet** (deliberately kept bare).
- `src/main.rs` — hello-world stub only.
- `CHANGELOG.md` — Keep a Changelog format. `[Unreleased]` at top, then
  `[0.0.1] - 2026-09-19` (scaffold + roadmap). Future versions: 0.0.2, 0.0.3, ...
- Version history is appended by the user/project owner per phase.

## Decisions so far

- Repo root that git tracks is the parent dir (`/home/dali/WORK/utils`);
  `telco_si/` is currently untracked there.
- Target architecture (approved): Interfaces → Application → Domain layering;
  infrastructure implements domain/application ports; 10 bounded contexts.
- `src/` intentionally clean; nothing implemented except the hello-world main.

## Next steps (when user provides them)

1. Phase 1 — Foundation: add deps (Actix Web, Tokio, SQLx+SQLite, config, tracing),
   config loader, entry point, health endpoints, SQLite WAL + foreign keys,
   error-handling conventions, DDD directory structure.
2. Phase 2 — Subscriber context, and so on (see CHANGELOG roadmap).

## Reminders for the next session

- Wait for the user to give build steps; do not scaffold code unprompted.
- Update `CHANGELOG.md` versions and this handoff as phases complete.