"""Application commands for customer management use cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..domain.value_objects import ContactType, CustomerType


@dataclass(frozen=True)
class CreateCustomerCommand:
    customer_type: CustomerType
    display_name: str
    first_name: str | None = None
    last_name: str | None = None
    legal_name: str | None = None
    email: str | None = None
    registration_number: str | None = None


@dataclass(frozen=True)
class UpdateCustomerCommand:
    customer_id: str
    version: int
    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChangeCustomerTypeCommand:
    customer_id: str
    version: int
    customer_type: CustomerType
    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeactivateCustomerCommand:
    customer_id: str


@dataclass(frozen=True)
class ReactivateCustomerCommand:
    customer_id: str


@dataclass(frozen=True)
class AddContactCommand:
    customer_id: str
    name: str
    contact_type: ContactType
    value: str
    is_primary: bool = False


@dataclass(frozen=True)
class UpdateContactCommand:
    customer_id: str
    contact_id: str
    version: int
    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RemoveContactCommand:
    customer_id: str
    contact_id: str
    version: int


@dataclass(frozen=True)
class AddAddressCommand:
    customer_id: str
    line1: str
    city: str
    postal_code: str
    country: str
    label: str | None = None
    line2: str | None = None
    region: str | None = None
    is_primary: bool = False


@dataclass(frozen=True)
class UpdateAddressCommand:
    customer_id: str
    address_id: str
    version: int
    changes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RemoveAddressCommand:
    customer_id: str
    address_id: str
    version: int
