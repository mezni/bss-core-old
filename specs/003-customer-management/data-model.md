# Data Model: Customer Management (S02)

**Date**: 2026-11-09 | **Source**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

The Customer Management module owns three persisted entities: `Customer` (aggregate root), `Contact`, and `Address`. All identifiers are UUIDv4 strings. Persistence uses SQLAlchemy 2.x with Alembic-managed schema on SQLite.

## Entities

### Customer (aggregate root)

- **Description**: A person or organization the business serves. Owns contacts and addresses and enforces identity, uniqueness, lifecycle, and eligibility invariants.
- **Attributes**:
  - `id` (UUID string, PK): System identifier; immutable.
  - `customer_type` (enum `CustomerType`: `INDIVIDUAL` | `BUSINESS`): Chosen at registration.
  - `display_name` (string, required): Human-readable name used in lists and references.
  - `first_name` (string, nullable): Required when `customer_type = INDIVIDUAL`.
  - `last_name` (string, nullable): Required when `customer_type = INDIVIDUAL`.
  - `legal_name` (string, nullable): Required when `customer_type = BUSINESS`.
  - `email` (string, nullable): Required and unique when `customer_type = INDIVIDUAL`; may be used as a general contact for businesses but does not participate in business uniqueness.
  - `registration_number` (string, nullable): Required and unique when `customer_type = BUSINESS` (registration or tax identifier).
  - `status` (enum `CustomerStatus`: `ACTIVE` | `INACTIVE`): Defaults to `ACTIVE`.
  - `version` (integer, required, default 1): Optimistic concurrency token; increments on each successful customer-level update.
  - `created_at` (timestamp, required): Set on creation.
  - `updated_at` (timestamp, required): Updated on each change.
- **Identity**: `id` is the system identity. Type-specific business uniqueness is enforced by partial unique indexes (see Constraints).
- **Relationships**:
  - Has zero or more `Contact` entities (one-to-many, cascade delete-orphan within the aggregate).
  - Has zero or more `Address` entities (one-to-many, cascade delete-orphan within the aggregate).
  - Referenced by downstream Order, Shipment, and Billing modules through `id` (no direct repository access).

### Contact (child entity)

- **Description**: A way to reach a customer.
- **Attributes**:
  - `id` (UUID string, PK)
  - `customer_id` (UUID string, FK → `customers.id`, required, indexed)
  - `name` (string, required): Label or person for the contact.
  - `contact_type` (enum `ContactType`: `EMAIL` | `PHONE`): Required.
  - `value` (string, required): Validated against the contact type.
  - `is_primary` (boolean, default false): At most one primary contact per customer.
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
- **Identity**: `id`; belongs to exactly one customer.

### Address (child entity)

- **Description**: A physical or mailing location associated with a customer.
- **Attributes**:
  - `id` (UUID string, PK)
  - `customer_id` (UUID string, FK → `customers.id`, required, indexed)
  - `label` (string, nullable): e.g., billing, shipping.
  - `line1` (string, required)
  - `line2` (string, nullable)
  - `city` (string, required)
  - `region` (string, nullable)
  - `postal_code` (string, required)
  - `country` (string, required, ISO 3166-1 alpha-2)
  - `is_primary` (boolean, default false): At most one primary address per customer.
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
- **Identity**: `id`; belongs to exactly one customer.

### Value Objects

- **CustomerType**: `INDIVIDUAL` | `BUSINESS`. Determines required fields and uniqueness scope.
- **CustomerStatus**: `ACTIVE` | `INACTIVE`.
- **ContactType**: `EMAIL` | `PHONE`.
- **Email**: Normalized (trimmed, lower-cased) and format-validated.
- **RegistrationNumber**: Trimmed, normalized (upper-case, no whitespace) and non-empty.
- **Eligibility** (derived): `status == ACTIVE AND contact_count >= 1 AND address_count >= 1`.

## Relationships

### Customer ↔ Contact (One-to-Many)

- One customer has zero or more contacts.
- Each contact belongs to exactly one customer.
- Deleting a customer is not supported; deactivation preserves contacts.
- Removing a contact is allowed even if it is the last one; the customer simply becomes ineligible.

### Customer ↔ Address (One-to-Many)

- One customer has zero or more addresses.
- Each address belongs to exactly one customer.
- Removing an address is allowed even if it is the last one; the customer becomes ineligible.

## Constraints and Indexes

| Name | Definition | Purpose |
|---|---|---|
| `pk_customers` | `PRIMARY KEY (id)` | System identity |
| `uq_customers_individual_email` | `UNIQUE (email) WHERE customer_type = 'INDIVIDUAL'` | FR-002 individual uniqueness |
| `uq_customers_business_registration` | `UNIQUE (registration_number) WHERE customer_type = 'BUSINESS'` | FR-002 business uniqueness |
| `ix_customers_type_status` | `INDEX (customer_type, status)` | Search/filter (FR-010, FR-011, SC-003) |
| `ix_customers_display_name` | `INDEX (display_name)` | Name search |
| `pk_customer_contacts` | `PRIMARY KEY (id)` | Contact identity |
| `fk_customer_contacts_customer` | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` | Referential integrity |
| `ix_customer_contacts_customer` | `INDEX (customer_id)` | Aggregate loading |
| `uq_customer_contacts_primary` | `UNIQUE (customer_id) WHERE is_primary = true` | At most one primary contact |
| `pk_customer_addresses` | `PRIMARY KEY (id)` | Address identity |
| `fk_customer_addresses_customer` | `FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE` | Referential integrity |
| `ix_customer_addresses_customer` | `INDEX (customer_id)` | Aggregate loading |
| `uq_customer_addresses_primary` | `UNIQUE (customer_id) WHERE is_primary = true` | At most one primary address |

> SQLite supports partial indexes; the two type-scoped unique indexes and the two primary-flag indexes rely on this. The `is_primary` indexes are enforced at the application level as well for clear error messages.

## Validation Rules (from Functional Requirements)

| Rule | Source | Enforcement |
|---|---|---|
| `display_name` non-empty | FR-001, FR-009 | Domain |
| Individual requires `first_name`, `last_name`, valid unique `email` | FR-006, FR-002 | Domain + partial unique index |
| Business requires `legal_name`, non-empty unique `registration_number` | FR-006, FR-002 | Domain + partial unique index |
| Customer type is `INDIVIDUAL` or `BUSINESS`; type change allowed only when new type's required fields are supplied and uniqueness holds | FR-006, US3 | Domain |
| Contact `contact_type` valid and `value` matches the type | FR-009 | Domain |
| Address requires `line1`, `city`, `postal_code`, `country` | FR-009 | Domain |
| At most one primary contact and one primary address per customer | FR-007, FR-008 | Domain + partial unique index |
| Customer identifiers are unique | FR-002 | PK |
| Duplicate type-specific identity rejected with clear error | FR-002, edge cases | Domain + index |
| Deactivated customers ineligible for new business activity | FR-012 | Domain (eligibility) |
| Customer with no contact or no address ineligible | FR-012, Q5 | Domain (eligibility) |
| Stale update rejected with conflict | FR-016, Q4 | Repository conditional update |
| Missing customer returns not-found | FR-015 | Use case + API |
| Authorization: `view` vs `manage` | FR-013 | API dependencies |

## State Transitions

### Customer Lifecycle

```text
(create) ──> ACTIVE
ACTIVE ──deactivate──> INACTIVE
INACTIVE ──reactivate──> ACTIVE
```

- No transition to a deleted state; records are retained.
- Deactivation and reactivation do not remove contacts, addresses, or history.
- Eligibility is derived, not stored: `ACTIVE && contacts >= 1 && addresses >= 1`.

### Contact/Address Lifecycle

```text
(create) ──> present
present ──update──> present
present ──remove──> removed
```

- Removing the last contact or address leaves the customer valid but ineligible.

## Application DTOs (cross-module)

- **CustomerSummary**: `id`, `customer_type`, `display_name`, `status`, `eligible`, `version`, `updated_at`.
- **CustomerDetails**: summary fields plus `first_name`, `last_name`, `legal_name`, `email`, `registration_number`, contacts, addresses.
- **CustomerEligibility**: `customer_id`, `eligible`, `reasons` (e.g., `INACTIVE`, `NO_CONTACT`, `NO_ADDRESS`).

DTOs are plain data and must not expose ORM objects across module boundaries.

## Migration Notes

- Create `customers`, `customer_contacts`, and `customer_addresses` in one Alembic revision.
- Wire `target_metadata` in `migrations/env.py` to the customer declarative `Base` (and future module metadata) so autogeneration works.
- Seed no data in migrations; synthetic data is a separate S07 concern.
