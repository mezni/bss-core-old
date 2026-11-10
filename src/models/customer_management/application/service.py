"""Adapter implementing the customer eligibility port over the repository."""

from __future__ import annotations

from ..domain.exceptions import CustomerNotFound
from ..domain.repositories import CustomerRepository
from .dto import CustomerEligibilityDTO, CustomerSummaryDTO, customer_to_summary
from .ports import CustomerEligibilityPort


class CustomerEligibilityAdapter(CustomerEligibilityPort):
    """Read-only adapter for downstream modules."""

    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def get_summary(self, customer_id: str) -> CustomerSummaryDTO | None:
        customer = self.repository.get(customer_id)
        if customer is None:
            return None
        return customer_to_summary(customer)

    def check_eligibility(self, customer_id: str) -> CustomerEligibilityDTO:
        customer = self.repository.get(customer_id)
        if customer is None:
            raise CustomerNotFound(f"Customer {customer_id} was not found")
        return CustomerEligibilityDTO(
            customer_id=customer.id,
            eligible=customer.eligible,
            reasons=tuple(reason.value for reason in customer.eligibility_reasons()),
        )
