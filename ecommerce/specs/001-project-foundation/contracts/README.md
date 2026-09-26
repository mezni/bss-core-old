# Contracts: Project Foundation (Phase 0)

**Feature**: `001-project-foundation` | **Date**: 2026-09-26

## Why there is no API contract here

Phase 0 exposes **no HTTP interface**. The web application, its routes, and the
`/health` endpoint are Phase 1 work, and the database baseline is Phase 2. Producing an
OpenAPI contract now would document behaviour that does not exist and that the spec
explicitly places out of scope.

This project is not purely internal, though. It exposes two real interfaces to the people
who use it, and both are contractual in the strict sense: a contributor's tooling and CI
depend on their exact spelling, and the spec's success criteria are asserted against
them.

| Contract | Interface | Governs |
|---|---|---|
| [developer-commands.md](developer-commands.md) | The command surface — what a contributor types | FR-001, FR-017, FR-019, FR-023, SC-001, SC-005, SC-009 |
| [config-template.md](config-template.md) | The `.env.example` file format and coverage rule | FR-009, FR-010, FR-011, FR-012, SC-007, SC-008 |

## Contract status

Both contracts are **binding** on this feature. Neither is provisional. A later phase may
extend them, but any change to a spelling, a target name, or the marker token is a
breaking change and must be recorded in `CHANGELOG.md` in the same change (FR-016).

`docs/configuration.md` §42 remains the upstream authority for configuration variables.
`config-template.md` defines only the *file format* and the *coverage rule*; it does not
restate the variables, so the two cannot drift.
