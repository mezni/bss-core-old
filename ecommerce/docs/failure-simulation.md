# Failure Simulation — Fake E-Commerce Server

> **Status:** Draft
> **Authority:** `.specify/memory/constitution.md` v1.1.0

Failure simulation is a **first-class capability**, not a side effect. Its purpose is to let clients
and tests reproduce real-world failure modes on demand, deterministically, without patching code.

---

## 1. Principles

1. **Off by default.** A developer must never hit a simulated failure unexpectedly.
2. **Deterministic first.** The same failure request produces the same failure behavior, every
   time.
3. **Randomized is separate.** Resilience testing MAY use random injection, but it is
   independently controllable and cannot contaminate the deterministic path.
4. **Realistic.** Simulated failures follow the same compensation and transaction rules as real
   ones — otherwise they test nothing.
5. **Contained.** Failure logic lives in infrastructure (fake providers, middleware), never in the
   domain.

---

## 2. Scenarios

| Scenario | Where it fires | HTTP | Error code |
|---|---|---|---|
| `payment_declined` | Fake payment provider | `402` | `PAYMENT_DECLINED` |
| `payment_timeout` | Fake payment provider | `504` | `SIMULATED_FAILURE` |
| `payment_provider_error` | Fake payment provider | `502` | `SIMULATED_FAILURE` |
| `inventory_unavailable` | Fake inventory provider | `409` | `INSUFFICIENT_INVENTORY` |
| `service_timeout` | Middleware / any request | `504` | `SIMULATED_FAILURE` |
| `internal_server_error` | Middleware / any request | `500` | `INTERNAL_ERROR` |

Additional categories supported by the system: HTTP 4xx and 5xx failures, payment declines,
inventory conflicts, artificial latency, timeouts, external-service failures, temporary failures,
and configurable failure rates.

---

## 3. Triggering

### 3.1 Deterministic — request header (primary)

```http
X-Fake-Failure: payment_declined
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'X-Fake-Failure: payment_declined' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
```

One scenario per request. The header is consumed by middleware and translated into a
provider-level directive for the duration of that request only.

### 3.2 Deterministic — configuration

Global behavior is set by environment variables (see `docs/configuration.md` §5):

| `FAKE_FAILURE_ENABLED` | `FAKE_FAILURE_RATE` | Behavior |
|---|---|---|
| `false` | any | Simulation off; `X-Fake-Failure` **ignored** |
| `true` | `0.0` | Deterministic failures only, on explicit request |
| `true` | `> 0.0` | Deterministic **and** randomized injection |

### 3.3 Randomized — resilience testing

```bash
FAKE_FAILURE_ENABLED=true FAKE_FAILURE_RATE=0.25 uv run uvicorn ecommerce.main:app
```

`FAKE_FAILURE_RATE` is the probability that a request triggers a randomly chosen scenario. It MUST
default to `0.0`, and it is never used to satisfy a functional test.

### 3.4 Artificial latency

```bash
FAKE_LATENCY_MS=500      # every request delayed 500ms
```

Useful for exercising client timeouts and retry/backoff logic. Latency applies **in addition to**
whatever a scenario does.

---

## 4. Determinism Guarantee

The same failure request MUST produce the same failure behavior:

```bash
for i in 1 2 3; do
  curl -s -o /dev/null -w '%{http_code}\n' -X POST "$BASE/api/v1/checkout" \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H 'X-Fake-Failure: payment_declined' \
    -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
done
# 402
# 402
# 402
```

Two properties make this hold:

* The scenario is **named**, not sampled — no coin flip.
* Any randomness inside the failure path (transaction IDs, log jitter) uses the same seeded RNG or
  a counter.

Randomized injection is the deliberate exception, and it is off unless `FAKE_FAILURE_RATE > 0`.

---

## 5. Behavior Per Scenario

### `payment_declined` → `402 PAYMENT_DECLINED`

The provider rejects the authorization. This is the most important scenario, because it exercises
**compensation**.

```text
Checkout
   ↓
Inventory reserved
   ↓
Payment declined
   ↓
Inventory released
   ↓
Order marked failed
```

Required end state:

* Order exists with `status = failed` and a `failure_reason`.
* Reserved inventory returned to available — **stock is not left held**.
* Payment row reflects the decline; it is never later flipped to successful.
* The failure is observable, not silently swallowed.

A declined payment MUST NOT become successful later.

### `inventory_unavailable` → `409 INSUFFICIENT_INVENTORY`

Fires when the reservation is attempted, regardless of actual stock on hand.

Required end state:

* **No order is created.**
* No payment is created.
* Stock levels unchanged.
* Cart remains intact so the customer can retry after restocking.

### `payment_timeout` → `504`

The provider never responds. Treated exactly like a decline for state purposes — the system cannot
wait forever, so it must compensate.

Required end state: identical to `payment_declined` (order `failed`, inventory released).

### `payment_provider_error` → `502`

The provider returns a malformed/erroneous response. Tests error handling rather than the decline
path.

Required end state: order `failed`, inventory released, provider error recorded in
`failure_reason`.

### `service_timeout` → `504`

Middleware-level. Delays the request past the client's timeout. MUST NOT leave partial writes.

### `internal_server_error` → `500`

Middleware-level. Verifies that unexpected faults produce a clean error envelope with **no** stack
trace, SQL, or internal path leaked to the client.

---

## 6. Error Envelope

All simulated failures use the standard envelope (`docs/API.md` §2):

```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Payment was declined by the issuer",
    "details": [
      { "field": "payment_method", "issue": "fake_card declined" }
    ],
    "request_id": "01J8Z9..."
  }
}
```

Clients distinguish simulated failures by the `X-Fake-Failure` echo response header and/or the
stable `code`. Error codes are stable identifiers and MUST NOT change meaning within `/api/v1`.

---

## 7. Implementation Boundaries

| Concern | Location | Not in |
|---|---|---|
| Header parsing, request-scoped directive | API middleware | Domain |
| Scenario → provider directive | API layer → application layer | Domain |
| Provider refusing to authorize | `infrastructure/external` fake provider | Domain |
| Latency injection | Middleware | Domain |
| State compensation | Application layer use case | Middleware |

The domain never asks "am I in failure mode?". The fake provider simply behaves as a provider that
declines or times out, and the application layer applies the same compensation rules it would for a
real provider. That is what makes the simulation meaningful.

---

## 8. Safety Rules

1. **Never in production-shaped environments.** With `APP_ENV=production`, the application refuses
   to start if `FAKE_FAILURE_ENABLED=true` or `FAKE_FAILURE_RATE > 0`.
2. **Off by default** in development and test.
3. **Scoped to a request** — a failure directive never leaks to the next request.
4. **No production data** — everything is synthetic.
5. **Same compensation as reality** — a simulated decline exercises the real rollback/compensate
   path, so tests cover production code rather than a parallel test-only path.
6. **No infinite latency** — `FAKE_LATENCY_MS` is bounded and validated at startup.

---

## 9. Testing Failure Simulation

Every scenario MUST have tests asserting **both** the response and the resulting state. A failure
that leaves corrupt state is worse than no failure at all.

| Scenario | Assert response | Assert state |
|---|---|---|
| `payment_declined` | `402` | Order `failed`; inventory released |
| `payment_timeout` | `504` | Order `failed`; inventory released |
| `payment_provider_error` | `502` | Order `failed`; inventory released |
| `inventory_unavailable` | `409` | No order; stock unchanged; cart intact |
| `service_timeout` | `504` | No partial writes |
| `internal_server_error` | `500` | No internal detail leaked |

Plus:

```text
Disabled by default        X-Fake-Failure ignored when simulation off
Repeatability              same request -> same status 3x
Isolation                  directive does not leak to the next request
Unknown scenario           422/400 with a clear message
Production guard           refuses to start with simulation enabled
Latency bound              FAKE_LATENCY_MS validated
```

See `docs/testing.md` §9.

---

## 10. Client Usage

```text
Happy path    -> assert 201
Declined      -> assert 402 + verify order failed + stock released
Short stock   -> assert 409 + verify no order created
Retry logic   -> decline once, then succeed; assert recovery
Timeouts      -> set FAKE_LATENCY_MS above the client timeout
Backoff       -> combine latency with a 502
```

A client written against this server should be genuinely robust: it must handle decline, timeout,
conflict, and server error without special-casing the fake server.

---

## 11. Related

* `docs/API.md` — error envelope and codes
* `docs/configuration.md` — the four failure variables and their interaction
* `docs/testing.md` — failure scenario test matrix
* `docs/architecture.md` §8 — fake providers behind ports
* `specs/009-failure-simulation` — the feature specification
