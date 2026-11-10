"""Order status enum and value objects for order management domain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    """Order lifecycle status transitions."""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Money:
    """A monetary value with 2 decimal precision."""
    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        self.amount = round(float(self.amount), 2)
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot subtract Money with different currencies")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, multiplier: float) -> Money:
        return Money(amount=round(self.amount * multiplier, 2), currency=self.currency)

    def __rmul__(self, multiplier: float) -> Money:
        return self.__mul__(multiplier)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency})"