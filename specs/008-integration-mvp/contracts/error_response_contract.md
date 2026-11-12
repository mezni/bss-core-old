# Contract: Standardized Error Response

**Applies to**: All API endpoints of the consolidated application (all modules and integration workflows), versioned under `/api/v1`.

**Description**: Every error response — regardless of module — uses one standardized JSON envelope with an appropriate HTTP status code, per FR-007 and the spec clarification.

**Envelope format**:

```json
{
  "error": "<type>",
  "message": "<human-readable message>",
  "code": "<error-code>"
}
```

| Field | Type | Description |
|---|---|---|
| `error` | string | Error type slug, lowercase, dot/underscore separated — e.g., `"validation_error"`, `"not_found"`, `"authorization"` |
| `message` | string | Human-readable, actionable description of what failed and (where possible) how to correct it |
| `code` | string | Stable, uppercase machine-readable error code — e.g., `"VALIDATION_ERROR"`, `"NOT_FOUND"` |

**Status-to-code mapping**:

| HTTP Status | `code` | Typical Cause |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Malformed/invalid request payload (incl. Pydantic request validation) |
| 401 | `UNAUTHENTICATED` | Missing, expired, or invalid bearer token |
| 403 | `FORBIDDEN` | Valid token lacking the required permission |
| 404 | `NOT_FOUND` | Referenced resource does not exist |
| 409 | `CONFLICT` | Domain conflict — invalid state transition, duplicate (e.g., duplicate invoice, payment on paid invoice, shipment for non-confirmed order), stale update |
| 422 | `UNPROCESSABLE_ENTITY` | Semantically invalid business payload |
| 500 | `INTERNAL_ERROR` | Unhandled server error; message must not leak internals or secrets |

**Examples**:

```json
// 403 FORBIDDEN — workflow authorization denial
{
  "error": "authorization",
  "message": "Token lacks required permission 'user:billing' for this workflow.",
  "code": "FORBIDDEN"
}

// 409 CONFLICT — duplicate invoice generation
{
  "error": "conflict",
  "message": "Order 42 already has an invoice; duplicate generation is not allowed.",
  "code": "CONFLICT"
}

// 404 NOT_FOUND
{
  "error": "not_found",
  "message": "Customer 99 not found.",
  "code": "NOT_FOUND"
}
```

**Rules**:

- Every error response — including unhandled exceptions mapped to 500 — uses this envelope; no bare HTTPException bodies
- `message` never contains stack traces, SQL, secrets, or token material
- Error codes are stable across releases (asserted by contract tests)
- Authorization denials (401/403) additionally emit structured log events with the required permission (see `authorization_contract.md`)
- Deviation from `docs/api-design.md` RFC 9457 Problem Details is governed per constitution Section 15 — recorded in `research.md` Decision 3; `docs/api-design.md` is updated to this format
