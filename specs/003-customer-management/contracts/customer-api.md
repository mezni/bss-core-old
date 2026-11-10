# Contract: Customer REST API

**Base path**: `/api/v1/customers` | **Version**: 1 | **Format**: JSON (OpenAPI 3.1)

All endpoints require authentication. Mutating endpoints require the `customer:manage` permission; read endpoints require `customer:view`. Errors use the shared error envelope defined below.

## Shared Error Envelope

```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human-readable message",
    "details": { "field": "reason" }
  }
}
```

| HTTP Status | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Malformed or missing fields |
| 401 | `UNAUTHENTICATED` | Missing/invalid credentials |
| 403 | `FORBIDDEN` | Missing required permission |
| 404 | `CUSTOMER_NOT_FOUND` / `CONTACT_NOT_FOUND` / `ADDRESS_NOT_FOUND` | Target does not exist |
| 409 | `DUPLICATE_CUSTOMER` | Type-specific identity already exists |
| 409 | `STALE_UPDATE` | `version` does not match current version |
| 409 | `DUPLICATE_PRIMARY_CONTACT` / `DUPLICATE_PRIMARY_ADDRESS` | More than one primary |
| 422 | `UNPROCESSABLE_ENTITY` | Structurally valid but semantically invalid |

## Customer Endpoints

### POST /api/v1/customers

Create a customer. Requires `customer:manage`.

**Request body**

```json
{
  "customer_type": "INDIVIDUAL",
  "display_name": "Jane Doe",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com"
}
```

Business variant:

```json
{
  "customer_type": "BUSINESS",
  "display_name": "Acme Corp",
  "legal_name": "Acme Corporation",
  "registration_number": "US-123456789",
  "email": "accounts@acme.example"
}
```

**Response 201**

```json
{
  "id": "5f0c2c1e-7a4b-4c1e-9d2a-1b2c3d4e5f60",
  "customer_type": "INDIVIDUAL",
  "display_name": "Jane Doe",
  "first_name": "Jane",
  "last_name": "Doe",
  "legal_name": null,
  "email": "jane.doe@example.com",
  "registration_number": null,
  "status": "ACTIVE",
  "eligible": false,
  "version": 1,
  "contacts": [],
  "addresses": [],
  "created_at": "2026-11-09T12:00:00Z",
  "updated_at": "2026-11-09T12:00:00Z"
}
```

`eligible` is `false` until at least one contact and one address exist.

### GET /api/v1/customers

List/search customers. Requires `customer:view`.

**Query parameters**

| Name | Type | Default | Notes |
|---|---|---|---|
| `q` | string | – | Matches display name, email, or registration number |
| `customer_type` | enum | – | `INDIVIDUAL` or `BUSINESS` |
| `status` | enum | – | `ACTIVE` or `INACTIVE` |
| `page` | integer | 1 | ≥ 1 |
| `page_size` | integer | 20 | 1–100 |

**Response 200**

```json
{
  "items": [ { "...": "CustomerSummary" } ],
  "page": 1,
  "page_size": 20,
  "total": 137
}
```

`CustomerSummary` fields: `id`, `customer_type`, `display_name`, `status`, `eligible`, `version`, `updated_at`.

### GET /api/v1/customers/{customer_id}

Retrieve a customer with contacts and addresses. Requires `customer:view`.

**Response 200**: `CustomerDetails` (the 201 shape above).

**Response 404**: `CUSTOMER_NOT_FOUND`.

### PATCH /api/v1/customers/{customer_id}

Update permitted fields. Requires `customer:manage`. Body must include the current `version`.

**Request body**

```json
{
  "version": 3,
  "display_name": "Jane A. Doe",
  "email": "jane.a.doe@example.com"
}
```

**Response 200**: updated `CustomerDetails` with `version` incremented.

**Response 409 `STALE_UPDATE`**

```json
{
  "error": {
    "code": "STALE_UPDATE",
    "message": "The customer was modified by another operation. Reload and retry.",
    "details": { "current_version": 4 }
  }
}
```

**Response 409 `DUPLICATE_CUSTOMER`**: type-specific identity conflicts.

### POST /api/v1/customers/{customer_id}/deactivate

Requires `customer:manage`. No body.

**Response 200**: `CustomerDetails` with `status = INACTIVE` and incremented `version`. Contacts/addresses preserved.

### POST /api/v1/customers/{customer_id}/reactivate

Requires `customer:manage`. No body.

**Response 200**: `CustomerDetails` with `status = ACTIVE`. Eligibility is recomputed and may remain `false` if contacts/addresses are missing.

### GET /api/v1/customers/{customer_id}/eligibility

Requires `customer:view`.

**Response 200**

```json
{
  "customer_id": "5f0c2c1e-7a4b-4c1e-9d2a-1b2c3d4e5f60",
  "eligible": false,
  "reasons": ["NO_CONTACT", "NO_ADDRESS"]
}
```

`reasons` may contain `INACTIVE`, `NO_CONTACT`, `NO_ADDRESS`; empty when eligible.

## Contact Endpoints

### POST /api/v1/customers/{customer_id}/contacts

Requires `customer:manage`.

```json
{
  "name": "Jane Doe",
  "contact_type": "EMAIL",
  "value": "jane.doe@example.com",
  "is_primary": true
}
```

**Response 201**: `ContactDetails`.

### PATCH /api/v1/customers/{customer_id}/contacts/{contact_id}

Requires `customer:manage`. Body includes `version` of the contact's parent customer? No — contact updates use the contact's own `updated_at`; to keep the contract simple, contact and address mutations require the **customer** `version` to guard the aggregate. Include `"version": <customer_version>`.

**Response 200**: updated `ContactDetails`; customer `version` incremented.

### DELETE /api/v1/customers/{customer_id}/contacts/{contact_id}

Requires `customer:manage`. Body: `{ "version": <customer_version> }`.

**Response 204**: no content; customer `version` incremented.

## Address Endpoints

### POST /api/v1/customers/{customer_id}/addresses

Requires `customer:manage`.

```json
{
  "label": "Billing",
  "line1": "123 Main St",
  "line2": "Suite 400",
  "city": "Springfield",
  "region": "IL",
  "postal_code": "62701",
  "country": "US",
  "is_primary": true
}
```

**Response 201**: `AddressDetails`.

### PATCH /api/v1/customers/{customer_id}/addresses/{address_id}

Requires `customer:manage`; body includes `version`.

**Response 200**: updated `AddressDetails`; customer `version` incremented.

### DELETE /api/v1/customers/{customer_id}/addresses/{address_id}

Requires `customer:manage`; body includes `version`.

**Response 204**: no content; customer `version` incremented.

## ContactDetails

```json
{
  "id": "0a1b2c3d-4e5f-6071-8293-a4b5c6d7e8f9",
  "customer_id": "5f0c2c1e-7a4b-4c1e-9d2a-1b2c3d4e5f60",
  "name": "Jane Doe",
  "contact_type": "EMAIL",
  "value": "jane.doe@example.com",
  "is_primary": true,
  "created_at": "2026-11-09T12:05:00Z",
  "updated_at": "2026-11-09T12:05:00Z"
}
```

## AddressDetails

```json
{
  "id": "1b2c3d4e-5f60-7182-93a4-b5c6d7e8f901",
  "customer_id": "5f0c2c1e-7a4b-4c1e-9d2a-1b2c3d4e5f60",
  "label": "Billing",
  "line1": "123 Main St",
  "line2": "Suite 400",
  "city": "Springfield",
  "region": "IL",
  "postal_code": "62701",
  "country": "US",
  "is_primary": true,
  "created_at": "2026-11-09T12:06:00Z",
  "updated_at": "2026-11-09T12:06:00Z"
}
```

## Notes

- All timestamps are ISO 8601 UTC.
- `version` is the concurrency token for the **customer aggregate**. Any child mutation increments the customer `version`.
- Responses must never include secrets or internal ORM fields.
- Endpoints are registered on the existing FastAPI app and documented through OpenAPI.
