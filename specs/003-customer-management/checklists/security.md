# Security Review Checklist: Customer Management (S02)

Review date: 2026-11-09
Scope: `src/models/customer_management/`, `src/frontend/customer/`, `src/api/health.py`

## Authentication

- [x] Every customer endpoint declares a `get_permissions` dependency; no route is public.
- [x] Missing, malformed, expired, or invalid bearer tokens return `401 UNAUTHENTICATED`.
- [x] Tokens are verified with PyJWT using a fixed algorithm (`HS256`); unsigned tokens are rejected.
- [x] `BSS_JWT_SECRET` is read from the environment; the development fallback is documented as non-production.
- [x] Authorization failures return `403 FORBIDDEN` without revealing resource existence.

## Authorization

- [x] Read endpoints require `customer:view`.
- [x] Mutating endpoints (create, update, deactivate, reactivate, contacts, addresses) require `customer:manage`.
- [x] `customer:manage` does not implicitly grant `customer:view`; permissions remain separate.
- [x] Contract tests cover `401`, `403`, and permitted calls for read and write paths.
- [x] The Streamlit client forwards the bearer token and performs no authorization decisions of its own.

## Input validation

- [x] Pydantic request models use `extra="forbid"` and constrain lengths, enums, and pagination bounds.
- [x] Type-specific required fields are validated in the domain before persistence.
- [x] Email, phone, registration number, and ISO-2 country formats are validated and normalized.
- [x] Invalid payloads return the shared error envelope (`400 VALIDATION_ERROR` or `422 UNPROCESSABLE_ENTITY`).
- [x] Pagination clamps `page` to at least 1 and `page_size` to 1–100.

## Injection and data access

- [x] All database access uses SQLAlchemy ORM expressions and bound parameters; no string-built SQL.
- [x] Search terms are passed as bound `ilike` parameters, not interpolated into SQL.
- [x] Repository results are mapped to domain objects before leaving the module.
- [x] Downstream modules cannot import ORM models or repositories; they use `CustomerEligibilityPort`.

## Concurrency and integrity

- [x] Every aggregate mutation increments `version` and rejects stale versions with `409 STALE_UPDATE`.
- [x] Partial unique indexes enforce individual email and business registration uniqueness.
- [x] Database `IntegrityError` is translated to `DUPLICATE_CUSTOMER` or `DUPLICATE_PRIMARY_*`.
- [x] At most one primary contact and one primary address are enforced in the domain and by partial indexes.
- [x] Deactivation preserves contacts, addresses, and history; no destructive delete path exists.

## PII and logging

- [x] Lifecycle logs contain only `customer_id`, action, status, and version.
- [x] Names, emails, phone numbers, addresses, and registration numbers are never logged.
- [x] API responses expose only schema-whitelisted fields; no ORM internals or secrets are returned.
- [x] Error responses contain stable codes and safe messages; no stack traces or SQL are exposed.
- [x] DTOs are immutable snapshots and contain no ORM references.

## Verification

- [x] `uv run pytest` covers authentication, authorization, validation, concurrency, and persistence.
- [x] `uv run ruff check src tests` passes.
- [x] Migration upgrade/downgrade verified on a clean database.
- [x] Quickstart authorization and stale-update scenarios pass.
