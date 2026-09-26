# HTTP API Contract — Fake E-Commerce Server

> **Status:** Draft — normative shape, not yet implemented.
> **Base path:** `/api/v1` · **Unversioned:** `/health`, `/docs`, `/openapi.json`
> **Authority:** `.specify/memory/constitution.md` v1.1.0, *Technology Stack and API Design*

All request and response bodies are JSON. All schemas shown are **explicit Pydantic schemas**.
Database models are never exposed directly as API schemas.

---

## 1. Conventions

| Aspect | Rule |
|---|---|
| Versioning | All public routes under `/api/v1/`. Breaking changes require a new version. |
| Content type | `application/json` |
| IDs | Opaque strings (UUID). Never client-generated. |
| Money | Integer **minor units** (e.g. cents) + ISO-4217 `currency`. Never floats. |
| Timestamps | RFC 3339 / ISO 8601 with timezone, UTC (`2026-09-25T14:03:00Z`). |
| Enums | Lowercase snake_case strings. |
| Idempotency | `POST` that creates state SHOULD accept an `Idempotency-Key` header. |
| Tracing | Every response echoes `X-Request-ID`; clients MAY supply one. |
| Failure injection | `X-Fake-Failure: <scenario>` (see `docs/failure-simulation.md`). |

### 1.1 Money representation

Floating point is never used for money. Amounts are integers in minor units:

```json
{ "amount": 2499, "currency": "USD" }
```

`amount: 2499` means $24.99. This is a deliberate correctness choice, not a style preference.

### 1.2 IDs and validation

* Path/query IDs MUST have a valid format; malformed IDs yield `422`, not `500`.
* Quantities MUST be positive integers where required (`ge=1`).
* Required fields MUST be explicit in the schema.

---

## 2. Error Format

Every error response uses one envelope. Error codes are stable identifiers.

```json
{
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Insufficient inventory for product",
    "details": [
      {
        "field": "quantity",
        "issue": "requested 5, available 2"
      }
    ],
    "request_id": "01J8Z9..."
  }
}
```

| Field | Required | Notes |
|---|---|---|
| `code` | yes | Stable, screaming snake case. Never localized, never reworded. |
| `message` | yes | Human-readable, safe to show a developer. |
| `details` | no | Field-level issues (validation, conflict specifics). |
| `request_id` | yes | Matches the `X-Request-ID` response header. |

Internal exception types and stack traces MUST NOT be exposed to clients. Domain, application,
infrastructure, and HTTP errors are distinguished internally and mapped to codes at the API
boundary only.

### 2.1 Error codes

| Code | HTTP | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Request failed schema/semantic validation |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Generic uniqueness/state conflict |
| `DUPLICATE_SKU` | 409 | SKU already taken |
| `DUPLICATE_EMAIL` | 409 | Email already registered |
| `EMPTY_CART` | 409 | Checkout attempted with no items |
| `INSUFFICIENT_INVENTORY` | 409 | Not enough stock to reserve |
| `PRODUCT_INACTIVE` | 409 | Product exists but is not purchasable |
| `INVALID_ORDER_TRANSITION` | 409 | Order state change is not allowed |
| `INVALID_PAYMENT_TRANSITION` | 409 | Payment state change is not allowed |
| `PAYMENT_DECLINED` | 402 | Provider declined the charge |
| `UNAUTHENTICATED` | 401 | Missing or invalid credentials |
| `FORBIDDEN` | 403 | Authenticated but not permitted |
| `SIMULATED_FAILURE` | varies | Injected via `X-Fake-Failure`; see failure-simulation doc |
| `INTERNAL_ERROR` | 500 | Unexpected server fault |

---

## 3. Status Codes

| Code | Used for |
|---|---|
| `200 OK` | Successful read or update returning a body |
| `201 Created` | Resource created (with `Location` header) |
| `204 No Content` | Successful delete or action with no body |
| `400 Bad Request` | Malformed request the schema layer cannot express |
| `401 Unauthorized` | Missing/invalid credentials |
| `403 Forbidden` | Authenticated but not allowed |
| `404 Not Found` | Unknown resource |
| `409 Conflict` | State or uniqueness conflict |
| `422 Unprocessable Entity` | Validation failure |
| `500 Internal Server Error` | Unexpected fault (no internal detail leaked) |

---

## 4. Pagination, Filtering, Sorting

### 4.1 List responses

```json
{
  "items": [ /* ... */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 137,
    "total_pages": 7
  }
}
```

| Query param | Default | Rules |
|---|---|---|
| `page` | `1` | `ge=1` |
| `page_size` | `20` | `1..100`; exceeding → `422` |
| `sort` | resource default | Field name, `-` prefix for descending |

### 4.2 Filtering

Filters are explicit query parameters per resource — never a free-form query language.

```text
GET /api/v1/products?category_id=...&is_active=true&min_price=1000&max_price=50000
GET /api/v1/products?q=wireless%20keyboard
```

* `q` performs a substring match on name (and description where useful).
* Unknown query parameters are ignored rather than rejected, to keep clients forward-compatible
  within a version.
* Enumerated filter values MUST be constrained; an invalid enum yields `422`.

---

## 5. Authentication and Authorization

Fake authentication only — never real credentials. Full behavior: `docs/failure-simulation.md`
and `specs/010-authentication`.

| Aspect | Rule |
|---|---|
| Scheme | `Authorization: Bearer <fake-token>` |
| Roles | `customer`, `admin`, `service` |
| Public routes | Product catalog reads, `/health`, `/docs` |
| Customer routes | Own cart, orders, payments, profile — enforced per-resource, never by trusting a body-supplied customer id |
| Admin routes | Product/inventory management, all-orders read |
| Service routes | Programmatic checkout, bulk reads |

A customer MUST NOT read or mutate another customer's cart, orders, or profile. Authorization is
evaluated in the application layer, never in the route body.

---

## 6. Resource Schemas

Representative shapes. Field-level details are finalized in each feature spec.

```jsonc
// Money
{ "amount": 2499, "currency": "USD" }

// Category
{
  "id": "uuid",
  "name": "Audio",
  "slug": "audio",
  "parent_id": null
}

// Product
{
  "id": "uuid",
  "sku": "AUD-0001",
  "name": "Wireless Earbuds",
  "description": "Synthetic product description.",
  "category_id": "uuid",
  "price": { "amount": 7999, "currency": "USD" },
  "is_active": true,
  "created_at": "2026-09-25T14:03:00Z",
  "updated_at": "2026-09-25T14:03:00Z"
}

// Customer
{
  "id": "uuid",
  "email": "customer1@example.invalid",
  "full_name": "Synthetic Customer One",
  "status": "active",            // active | inactive | suspended
  "address": {
    "line1": "1 Example Street",
    "city": "Springfield",
    "postal_code": "00000",
    "country_code": "US"
  }
}

// CartItem
{ "id": "uuid", "product_id": "uuid", "quantity": 2, "unit_price": { "amount": 7999, "currency": "USD" } }

// Cart
{
  "id": "uuid",
  "customer_id": "uuid",
  "status": "active",            // active | checked_out | abandoned
  "items": [ /* CartItem */ ],
  "subtotal": { "amount": 15998, "currency": "USD" },
  "created_at": "2026-09-25T14:03:00Z"
}

// OrderItem  (price is snapshotted at order time)
{ "id": "uuid", "product_id": "uuid", "quantity": 2, "unit_price": { "amount": 7999, "currency": "USD" }, "line_total": { "amount": 15998, "currency": "USD" } }

// Order
{
  "id": "uuid",
  "customer_id": "uuid",
  "status": "confirmed",         // pending|confirmed|processing|shipped|delivered|cancelled|failed
  "items": [ /* OrderItem */ ],
  "total": { "amount": 15998, "currency": "USD" },
  "created_at": "2026-09-25T14:03:00Z"
}

// Inventory
{
  "product_id": "uuid",
  "quantity_available": 40,
  "quantity_reserved": 2,
  "sku": "AUD-0001"
}

// Payment
{
  "id": "uuid",
  "order_id": "uuid",
  "status": "authorized",        // pending|authorized|captured|declined|failed|refunded
  "amount": { "amount": 15998, "currency": "USD" },
  "method": "fake_card",         // synthetic only
  "transaction_id": "faketxn_0001",
  "created_at": "2026-09-25T14:03:00Z"
}
```

> Order item prices are **snapshotted** at order time so that later catalog price changes never
> silently rewrite order history. Order totals are always recomputed server-side from these
> snapshots.

---

## 7. Endpoints

### 7.1 Health (unversioned)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | none | Liveness. `200` with `{"status":"ok"}` |
| `GET` | `/ready` | none | Readiness (planned, not required) |

### 7.2 Products — `/api/v1/products`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/products` | public | `200` | Paginated; filter/search/sort |
| `GET` | `/api/v1/products/{product_id}` | public | `200` | `404` if unknown |
| `POST` | `/api/v1/products` | admin | `201` | `409` on duplicate SKU |
| `PATCH` | `/api/v1/products/{product_id}` | admin | `200` | Partial update |
| `DELETE` | `/api/v1/products/{product_id}` | admin | `204` | Deactivates; never deletes referenced history |

Query: `category_id`, `is_active`, `min_price`, `max_price`, `q`, `page`, `page_size`, `sort`

### 7.3 Categories — `/api/v1/categories`

| Method | Path | Auth | Success |
|---|---|---|---|
| `GET` | `/api/v1/categories` | public | `200` |
| `GET` | `/api/v1/categories/{category_id}` | public | `200` |
| `POST` | `/api/v1/categories` | admin | `201` |
| `PATCH` | `/api/v1/categories/{category_id}` | admin | `200` |
| `DELETE` | `/api/v1/categories/{category_id}` | admin | `204` |

### 7.4 Customers — `/api/v1/customers`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `POST` | `/api/v1/customers` | public | `201` | `409` on duplicate email |
| `GET` | `/api/v1/customers/me` | customer | `200` | Current customer |
| `GET` | `/api/v1/customers/{customer_id}` | self/admin | `200` | `403` for other customers |
| `PATCH` | `/api/v1/customers/{customer_id}` | self/admin | `200` | |
| `GET` | `/api/v1/customers` | admin | `200` | Paginated |
| `DELETE` | `/api/v1/customers/{customer_id}` | self/admin | `204` | Deactivates |

### 7.5 Carts — `/api/v1/carts`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `POST` | `/api/v1/carts` | customer | `201` | |
| `GET` | `/api/v1/carts/{cart_id}` | owner/admin | `200` | Includes items + subtotal |
| `POST` | `/api/v1/carts/{cart_id}/items` | owner | `201` | Body: `{product_id, quantity}`; `409` if inactive |
| `PATCH` | `/api/v1/carts/{cart_id}/items/{item_id}` | owner | `200` | `quantity` must be `>= 1` |
| `DELETE` | `/api/v1/carts/{cart_id}/items/{item_id}` | owner | `204` | |
| `DELETE` | `/api/v1/carts/{cart_id}/items` | owner | `204` | Clear cart |

Adding an existing product increments quantity rather than creating a duplicate line.

### 7.6 Checkout — `/api/v1/checkout`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `POST` | `/api/v1/checkout` | customer | `201` | Body `{cart_id, payment_method}`; returns the created order |

Checkout reserves inventory, creates the order, authorizes payment, and confirms — or compensates.
See `docs/architecture.md` §6 and `docs/failure-simulation.md`.

### 7.7 Orders — `/api/v1/orders`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/orders` | customer/admin | `200` | Customers see only their own |
| `GET` | `/api/v1/orders/{order_id}` | owner/admin | `200` | |
| `POST` | `/api/v1/orders/{order_id}/cancel` | owner/admin | `200` | Only from cancellable states |

Lifecycle:

```text
pending ──> confirmed ──> processing ──> shipped ──> delivered
   │            │              │
   └────────────┴──────────────┴──────> cancelled
   └──────────────────────────────────> failed
```

Any transition not drawn above MUST be rejected with `409 INVALID_ORDER_TRANSITION`.

### 7.8 Inventory — `/api/v1/inventory`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/inventory` | admin | `200` | |
| `GET` | `/api/v1/inventory/{product_id}` | public | `200` | Availability only |
| `POST` | `/api/v1/inventory/{product_id}/stock` | admin | `200` | Add/restock; body `{quantity}` |
| `POST` | `/api/v1/inventory/{product_id}/reserve` | service | `200` | `409 INSUFFICIENT_INVENTORY` |
| `POST` | `/api/v1/inventory/{product_id}/release` | service | `200` | |

### 7.9 Payments — `/api/v1/payments`

| Method | Path | Auth | Success | Notes |
|---|---|---|---|---|
| `GET` | `/api/v1/payments/{payment_id}` | owner/admin | `200` | |
| `GET` | `/api/v1/orders/{order_id}/payment` | owner/admin | `200` | Payment for an order |
| `POST` | `/api/v1/payments/{payment_id}/capture` | admin | `200` | `authorized` → `captured` |
| `POST` | `/api/v1/payments/{payment_id}/refund` | admin | `200` | `captured` → `refunded` |

All payment data is synthetic. The server MUST NOT process real payment credentials.

---

## 8. Example Requests

```bash
BASE=http://127.0.0.1:8000

# Health
curl -s $BASE/health

# Browse the catalog
curl -s "$BASE/api/v1/products?is_active=true&page=1&page_size=5"

# Register a customer (synthetic data only)
curl -s -X POST $BASE/api/v1/customers \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev1@example.invalid","full_name":"Dev One"}'

# Create a cart and add a product
CART=$(curl -s -X POST $BASE/api/v1/carts -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST $BASE/api/v1/carts/$CART/items \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"product_id":"'"$PRODUCT_ID"'","quantity":2}'

# Checkout
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'

# Deterministic failure injection
curl -s -X POST $BASE/api/v1/checkout \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -H 'X-Fake-Failure: payment_declined' \
  -d '{"cart_id":"'"$CART"'","payment_method":"fake_card"}'
```

---

## 9. Backward Compatibility

Once published under `/api/v1/`, breaking changes MUST NOT be introduced casually. A breaking
change requires:

1. Documentation
2. Tests
3. A migration strategy
4. A new API version when appropriate (`/api/v2/...`)

Additive changes (new optional fields, new endpoints, new filter parameters) are non-breaking.
Removing a field, tightening validation, or changing an error code's meaning IS breaking.
