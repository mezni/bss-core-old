# Contract: Customer Eligibility Port

**Module boundary**: Customer Management → Order, Shipment, Billing
**Type**: Application-level port (in-process Python interface)
**Version**: 1

## Purpose

Other business modules must not access the customer repository, ORM models, or database tables directly (constitution Sections 2.1 and 5). This port is the only supported way for another module to read current customer data and determine whether a customer may participate in new business activity.

## Interface

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CustomerSummaryDTO:
    id: str
    customer_type: str          # "INDIVIDUAL" | "BUSINESS"
    display_name: str
    status: str                 # "ACTIVE" | "INACTIVE"
    eligible: bool
    version: int


@dataclass(frozen=True)
class CustomerEligibilityDTO:
    customer_id: str
    eligible: bool
    reasons: tuple[str, ...]    # subset of ("INACTIVE", "NO_CONTACT", "NO_ADDRESS")


class CustomerEligibilityPort(Protocol):
    def get_summary(self, customer_id: str) -> CustomerSummaryDTO | None:
        """Return the current customer summary, or None when not found."""

    def check_eligibility(self, customer_id: str) -> CustomerEligibilityDTO:
        """Return eligibility for new business activity.

        Raises CustomerNotFound when the customer does not exist.
        """
```

## Semantics

- `get_summary` returns a snapshot of the current customer; callers must not cache it across business transactions.
- `check_eligibility` evaluates `status == ACTIVE AND contact_count >= 1 AND address_count >= 1` at call time.
- A customer may be `eligible = false` for multiple reasons; all applicable reasons are returned.
- `CustomerNotFound` is a module-level exception translated by the caller's own error handling; it must not leak HTTP concerns into the application layer.
- DTOs are immutable and contain no ORM references.

## Usage Rules

- Callers depend on the port interface, not the concrete implementation.
- The port is wired through dependency injection at the composition root.
- No caller may import `src.models.customer_management.infrastructure` or `...domain.entities`.
- The port must not expose contact or address details; callers needing full details use the REST API or a future explicit read contract.

## Compatibility

- Adding fields to DTOs is backward compatible; removing or renaming fields requires a version bump.
- The port is internal to the deployment; it is not an HTTP contract.
