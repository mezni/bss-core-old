"""Value objects for billing management."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

INVOICE_NUMBER_PATTERN = re.compile(r"^INV-\d{8}-\d{4}$")

PAYMENT_METHODS = ("card", "bank_transfer", "cash")


class InvoiceStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    TERMINAL = "terminal"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    TERMINAL = "terminal"


class InvoiceNumber:
    """Represents an invoice number with format ``INV-YYYYMMDD-####``."""

    def __init__(self, value: str) -> None:
        if not INVOICE_NUMBER_PATTERN.match(value):
            raise ValueError(f"Invalid invoice number format: {value!r}")
        self.value = value

    @classmethod
    def generate(cls, billing_date: datetime, sequence: int) -> InvoiceNumber:
        """Build a sequential invoice number for the given billing date."""
        return cls(f"INV-{billing_date:%Y%m%d}-{sequence:04d}")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InvoiceNumber):
            return self.value == other.value
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)
