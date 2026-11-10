"""Application-level ports exposed to other business modules."""

from __future__ import annotations

from typing import Protocol

from .dto import CustomerEligibilityDTO, CustomerSummaryDTO


class CustomerEligibilityPort(Protocol):
    """Read-only customer contract for Order, Shipment, and Billing modules."""

    def get_summary(self, customer_id: str) -> CustomerSummaryDTO | None:
        """Return the current customer summary, or ``None`` when not found."""
        ...

    def check_eligibility(self, customer_id: str) -> CustomerEligibilityDTO:
        """Return eligibility for new business activity.

        Raises:
            CustomerNotFound: When the customer does not exist.
        """
        ...
