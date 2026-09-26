# Contract: Error Envelope

**Feature**: `002-fastapi-foundation` | **Date**: 2026-09-26

One structure for every failure the application returns. This is the feature's entire
error contract; `contracts/openapi.yaml` carries the same shape in schema form.

## Shape

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": [],
    "request_id": "7d3f4a2e-1c4b-4a90-9f31-2b8e6d5a0c11"
  }
}
```

Four fields, always all present, nested under a single top-level `error` key.

| Field | Type | Rule |
|---|---|---|
| `code` | string | Stable and machine-readable. Never a sentence, never a number that changes meaning. |
| `message` | string | Human-readable. For a 500 it is a fixed generic string. |
| `details` | array | Always an array. `[]` when there are no field issues. **Never an object, never `null`, never omitted.** |
| `request_id` | string | Always present so a client can quote it in a bug report. |

## Codes reachable in this feature

| Code | Status | Raised when |
|---|---|---|
| `NOT_FOUND` | 404 | The requested path is not a known route. |
| `VALIDATION_ERROR` | 422 | A request fails schema validation. Not reachable yet — no endpoint accepts input — but the handler is registered now so the first feature that takes input inherits the contract rather than inventing it. |
| `INTERNAL_ERROR` | 500 | An unanticipated exception. |

The remaining fourteen published codes belong to later features. None is invented here:
a code with no feature behind it is an undocumented promise.

## Guarantees

1. **One code path builds the envelope.** Both the `HTTPException` handler and the
   catch-all `Exception` handler construct the body through the same function, so the
   four fields and the always-array `details` rule hold by construction rather than by
   convention (FR-008).
2. **No internal detail escapes** (FR-009). The catch-all handler logs the traceback
   server-side and returns a fixed message. No exception type, message, stack frame, or
   file system path appears in any field.
3. **An unknown path is a normal outcome, not an exception.** It produces the same
   envelope as any other 404 rather than a framework default page (FR-008, SC-004).
4. **A client-supplied request id is sanitised before it is echoed.** An inbound
   `X-Request-ID` is truncated and character-screened, because an unbounded
   client-controlled value reflected into every error response is an injection surface.
   See `research.md` D-06.

## Non-goals

- No localisation, no i18n keys, no message catalogue.
- No retry or backoff hints in the body.
- No field-level validation details are produced yet, because nothing accepts input. The
  `details` array is `[]` on every response this feature can generate.
