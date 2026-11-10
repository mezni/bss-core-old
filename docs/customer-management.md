# Customer Management (S02)

Customer Management owns customer identity, lifecycle, contacts, and addresses.
It exposes a REST API for the Streamlit frontend and an application-level port
for Order, Shipment, and Billing.

## Boundaries

- Other modules MUST NOT import `src.models.customer_management.infrastructure`
  or `src.models.customer_management.domain.entities`.
- Other modules read current customer state through `CustomerEligibilityPort`.
- The frontend communicates only over HTTP through
  `src/frontend/customer/api_client.py`.

## Permissions

| Permission | Grants |
|---|---|
| `customer:view` | List, retrieve, and check eligibility |
| `customer:manage` | Create, update, deactivate, reactivate, and manage contacts/addresses |

Permissions are read from the `permissions` claim of a signed bearer token.
Missing or invalid tokens return `401 UNAUTHENTICATED`; missing permissions
return `403 FORBIDDEN`.

## REST API

Base path: `/api/v1/customers`

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/` | Create an individual or business customer |
| `GET` | `/` | Search/filter with `q`, `customer_type`, `status`, `page`, `page_size` |
| `GET` | `/{id}` | Retrieve a customer with contacts and addresses |
| `PATCH` | `/{id}` | Update fields or change type; requires `version` |
| `POST` | `/{id}/deactivate` | Deactivate without deleting data |
| `POST` | `/{id}/reactivate` | Reactivate a customer |
| `GET` | `/{id}/eligibility` | Eligibility and reasons |
| `POST` | `/{id}/contacts` | Add a contact |
| `PATCH` | `/{id}/contacts/{contact_id}` | Update a contact; requires `version` |
| `DELETE` | `/{id}/contacts/{contact_id}` | Remove a contact; body `{ "version": n }` |
| `POST` | `/{id}/addresses` | Add an address |
| `PATCH` | `/{id}/addresses/{address_id}` | Update an address; requires `version` |
| `DELETE` | `/{id}/addresses/{address_id}` | Remove an address; body `{ "version": n }` |

Errors use the shared envelope:

```json
{"error": {"code": "STALE_UPDATE", "message": "...", "details": {}}}
```

`version` is the concurrency token for the whole customer aggregate. Every
mutation, including contact and address changes, increments it.

## Type rules

- `INDIVIDUAL` requires `first_name`, `last_name`, and a unique `email`.
- `BUSINESS` requires `legal_name` and a unique `registration_number`; an
  optional general `email` is allowed and does not participate in uniqueness.
- A type change must supply the required fields for the new type. Fields that
  no longer apply are cleared.

## Eligibility

A customer is eligible when it is `ACTIVE`, has at least one contact, and has at
least one address. All applicable reasons are returned:

- `INACTIVE`
- `NO_CONTACT`
- `NO_ADDRESS`

## Consumer port

```python
from src.models.customer_management.application.ports import CustomerEligibilityPort

summary = port.get_summary(customer_id)          # CustomerSummaryDTO | None
eligibility = port.check_eligibility(customer_id)  # CustomerEligibilityDTO
```

`check_eligibility` raises `CustomerNotFound` when the customer does not exist.
DTOs are immutable snapshots; callers must not cache them across business
transactions. The port never exposes contacts, addresses, ORM objects, or HTTP
concerns.

The composition root in `src/api/health.py` provides
`build_customer_eligibility_port(session)` for request-scoped sessions.

## Running

```bash
uv run alembic upgrade head
uv run uvicorn src.api.health:app --reload
BSS_API_URL=http://localhost:8000 BSS_API_TOKEN=<jwt> uv run streamlit run src/frontend/app.py
```

Set `BSS_JWT_SECRET` to the secret used by the identity service to sign tokens.
The development fallback is not suitable for production.
