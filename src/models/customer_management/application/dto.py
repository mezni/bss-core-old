"""Immutable application DTOs for customer management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain.entities import Address, Contact, Customer
from ..domain.value_objects import ContactType, CustomerStatus, CustomerType


@dataclass(frozen=True)
class ContactDTO:
    id: str
    customer_id: str
    name: str
    contact_type: ContactType
    value: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AddressDTO:
    id: str
    customer_id: str
    label: str | None
    line1: str
    line2: str | None
    city: str
    region: str | None
    postal_code: str
    country: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CustomerSummaryDTO:
    id: str
    customer_type: CustomerType
    display_name: str
    status: CustomerStatus
    eligible: bool
    version: int
    updated_at: datetime


@dataclass(frozen=True)
class CustomerDetailsDTO:
    id: str
    customer_type: CustomerType
    display_name: str
    first_name: str | None
    last_name: str | None
    legal_name: str | None
    email: str | None
    registration_number: str | None
    status: CustomerStatus
    eligible: bool
    version: int
    contacts: tuple[ContactDTO, ...]
    addresses: tuple[AddressDTO, ...]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CustomerListDTO:
    items: tuple[CustomerSummaryDTO, ...]
    page: int
    page_size: int
    total: int


@dataclass(frozen=True)
class CustomerEligibilityDTO:
    customer_id: str
    eligible: bool
    reasons: tuple[str, ...]


def contact_to_dto(contact: Contact, customer_id: str) -> ContactDTO:
    return ContactDTO(
        id=contact.id,
        customer_id=customer_id,
        name=contact.name,
        contact_type=contact.contact_type,
        value=contact.value,
        is_primary=contact.is_primary,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


def address_to_dto(address: Address, customer_id: str) -> AddressDTO:
    return AddressDTO(
        id=address.id,
        customer_id=customer_id,
        label=address.label,
        line1=address.line1,
        line2=address.line2,
        city=address.city,
        region=address.region,
        postal_code=address.postal_code,
        country=address.country,
        is_primary=address.is_primary,
        created_at=address.created_at,
        updated_at=address.updated_at,
    )


def customer_to_summary(customer: Customer) -> CustomerSummaryDTO:
    return CustomerSummaryDTO(
        id=customer.id,
        customer_type=customer.customer_type,
        display_name=customer.display_name,
        status=customer.status,
        eligible=customer.eligible,
        version=customer.version,
        updated_at=customer.updated_at,
    )


def customer_to_details(customer: Customer) -> CustomerDetailsDTO:
    return CustomerDetailsDTO(
        id=customer.id,
        customer_type=customer.customer_type,
        display_name=customer.display_name,
        first_name=customer.first_name,
        last_name=customer.last_name,
        legal_name=customer.legal_name,
        email=customer.email,
        registration_number=customer.registration_number,
        status=customer.status,
        eligible=customer.eligible,
        version=customer.version,
        contacts=tuple(contact_to_dto(contact, customer.id) for contact in customer.contacts),
        addresses=tuple(
            address_to_dto(address, customer.id) for address in customer.addresses
        ),
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
