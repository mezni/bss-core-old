"""Customer aggregate and child entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .exceptions import (
    AddressNotFound,
    ContactNotFound,
    DuplicatePrimaryAddress,
    DuplicatePrimaryContact,
    InvalidCustomer,
)
from .value_objects import (
    ContactType,
    CustomerStatus,
    CustomerType,
    EligibilityReason,
    normalize_email,
    normalize_phone,
    normalize_registration_number,
)


class _Unset:
    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "UNSET"


UNSET: Any = _Unset()


def utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def normalize_datetime(value: datetime) -> datetime:
    """Attach UTC to naive datetimes returned by SQLite."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@dataclass
class Contact:
    """A customer contact channel (email or phone)."""

    id: str
    name: str
    contact_type: ContactType
    value: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise InvalidCustomer("Contact name is required")
        self.value = self.value.strip()
        if not self.value:
            raise InvalidCustomer("Contact value is required")
        if self.contact_type == ContactType.EMAIL:
            try:
                self.value = normalize_email(self.value)
            except ValueError as exc:
                raise InvalidCustomer(str(exc)) from exc
        elif self.contact_type == ContactType.PHONE:
            try:
                self.value = normalize_phone(self.value)
            except ValueError as exc:
                raise InvalidCustomer(str(exc)) from exc
        self.created_at = normalize_datetime(self.created_at)
        self.updated_at = normalize_datetime(self.updated_at)


@dataclass
class Address:
    """A customer postal address."""

    id: str
    line1: str
    city: str
    postal_code: str
    country: str
    label: str | None
    line2: str | None
    region: str | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        self.line1 = self.line1.strip()
        self.city = self.city.strip()
        self.postal_code = self.postal_code.strip()
        self.country = self.country.strip().upper()
        if not self.line1:
            raise InvalidCustomer("Address line1 is required")
        if not self.city:
            raise InvalidCustomer("Address city is required")
        if not self.postal_code:
            raise InvalidCustomer("Address postal_code is required")
        if len(self.country) != 2:
            raise InvalidCustomer("Address country must be a 2-letter ISO code")
        if self.label is not None:
            self.label = self.label.strip() or None
        if self.line2 is not None:
            self.line2 = self.line2.strip() or None
        if self.region is not None:
            self.region = self.region.strip() or None
        self.created_at = normalize_datetime(self.created_at)
        self.updated_at = normalize_datetime(self.updated_at)


@dataclass
class Customer:
    """Aggregate root for customer identity, lifecycle, contacts, and addresses."""

    id: str
    customer_type: CustomerType
    display_name: str
    status: CustomerStatus
    version: int
    first_name: str | None
    last_name: str | None
    legal_name: str | None
    email: str | None
    registration_number: str | None
    created_at: datetime
    updated_at: datetime
    contacts: list[Contact] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.created_at = normalize_datetime(self.created_at)
        self.updated_at = normalize_datetime(self.updated_at)
        self.validate()

    @classmethod
    def create(
        cls,
        customer_type: CustomerType | str,
        display_name: str,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        legal_name: str | None = None,
        email: str | None = None,
        registration_number: str | None = None,
        customer_id: str | None = None,
    ) -> Customer:
        """Create a new active customer at version 1."""
        now = utcnow()
        return cls(
            id=customer_id or str(uuid4()),
            customer_type=CustomerType(customer_type),
            display_name=display_name,
            status=CustomerStatus.ACTIVE,
            version=1,
            first_name=first_name,
            last_name=last_name,
            legal_name=legal_name,
            email=email,
            registration_number=registration_number,
            created_at=now,
            updated_at=now,
        )

    def validate(self) -> None:
        """Validate type-specific required fields and normalize identity values."""
        self.display_name = (self.display_name or "").strip()
        if not self.display_name:
            raise InvalidCustomer("display_name is required")

        if self.customer_type == CustomerType.INDIVIDUAL:
            self.first_name = (self.first_name or "").strip() or None
            self.last_name = (self.last_name or "").strip() or None
            if not self.first_name:
                raise InvalidCustomer("first_name is required for individual customers")
            if not self.last_name:
                raise InvalidCustomer("last_name is required for individual customers")
            if not self.email:
                raise InvalidCustomer("email is required for individual customers")
            try:
                self.email = normalize_email(self.email)
            except ValueError as exc:
                raise InvalidCustomer(str(exc)) from exc
            self.legal_name = None
            self.registration_number = None
        else:
            self.legal_name = (self.legal_name or "").strip() or None
            if not self.legal_name:
                raise InvalidCustomer("legal_name is required for business customers")
            if not self.registration_number:
                raise InvalidCustomer(
                    "registration_number is required for business customers"
                )
            try:
                self.registration_number = normalize_registration_number(
                    self.registration_number
                )
            except ValueError as exc:
                raise InvalidCustomer(str(exc)) from exc
            if self.email:
                try:
                    self.email = normalize_email(self.email)
                except ValueError as exc:
                    raise InvalidCustomer(str(exc)) from exc
            else:
                self.email = None
            self.first_name = None
            self.last_name = None

    def update(
        self,
        *,
        display_name: str | None | _Unset = UNSET,
        first_name: str | None | _Unset = UNSET,
        last_name: str | None | _Unset = UNSET,
        legal_name: str | None | _Unset = UNSET,
        email: str | None | _Unset = UNSET,
        registration_number: str | None | _Unset = UNSET,
    ) -> None:
        """Update mutable identity fields and revalidate the aggregate."""
        if display_name is not UNSET:
            self.display_name = display_name  # type: ignore[assignment]
        if first_name is not UNSET:
            self.first_name = first_name  # type: ignore[assignment]
        if last_name is not UNSET:
            self.last_name = last_name  # type: ignore[assignment]
        if legal_name is not UNSET:
            self.legal_name = legal_name  # type: ignore[assignment]
        if email is not UNSET:
            self.email = email  # type: ignore[assignment]
        if registration_number is not UNSET:
            self.registration_number = registration_number  # type: ignore[assignment]
        self.validate()
        self.updated_at = utcnow()

    def change_type(
        self,
        new_type: CustomerType | str,
        *,
        first_name: str | None | _Unset = UNSET,
        last_name: str | None | _Unset = UNSET,
        legal_name: str | None | _Unset = UNSET,
        email: str | None | _Unset = UNSET,
        registration_number: str | None | _Unset = UNSET,
    ) -> None:
        """Change the customer type, clearing fields that no longer apply."""
        target = CustomerType(new_type)
        if target == self.customer_type:
            return
        self.customer_type = target
        if first_name is not UNSET:
            self.first_name = first_name  # type: ignore[assignment]
        if last_name is not UNSET:
            self.last_name = last_name  # type: ignore[assignment]
        if legal_name is not UNSET:
            self.legal_name = legal_name  # type: ignore[assignment]
        if email is not UNSET:
            self.email = email  # type: ignore[assignment]
        if registration_number is not UNSET:
            self.registration_number = registration_number  # type: ignore[assignment]
        self.validate()
        self.updated_at = utcnow()

    def deactivate(self) -> None:
        """Deactivate the customer while preserving all related data."""
        if self.status != CustomerStatus.INACTIVE:
            self.status = CustomerStatus.INACTIVE
            self.updated_at = utcnow()

    def reactivate(self) -> None:
        """Reactivate an inactive customer."""
        if self.status != CustomerStatus.ACTIVE:
            self.status = CustomerStatus.ACTIVE
            self.updated_at = utcnow()

    def add_contact(
        self,
        name: str,
        contact_type: ContactType | str,
        value: str,
        *,
        is_primary: bool = False,
    ) -> Contact:
        """Add a contact, enforcing at most one primary contact."""
        if is_primary and any(contact.is_primary for contact in self.contacts):
            raise DuplicatePrimaryContact("A primary contact already exists")
        now = utcnow()
        contact = Contact(
            id=str(uuid4()),
            name=name,
            contact_type=ContactType(contact_type),
            value=value,
            is_primary=is_primary,
            created_at=now,
            updated_at=now,
        )
        self.contacts.append(contact)
        self.updated_at = now
        return contact

    def get_contact(self, contact_id: str) -> Contact:
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        raise ContactNotFound(f"Contact {contact_id} was not found")

    def update_contact(
        self,
        contact_id: str,
        *,
        name: str | _Unset = UNSET,
        contact_type: ContactType | str | _Unset = UNSET,
        value: str | _Unset = UNSET,
        is_primary: bool | _Unset = UNSET,
    ) -> Contact:
        """Update a contact and revalidate its values."""
        contact = self.get_contact(contact_id)
        if is_primary is True and any(
            other.is_primary for other in self.contacts if other.id != contact_id
        ):
            raise DuplicatePrimaryContact("A primary contact already exists")
        if name is not UNSET:
            contact.name = name  # type: ignore[assignment]
        if contact_type is not UNSET:
            contact.contact_type = ContactType(contact_type)  # type: ignore[arg-type]
        if value is not UNSET:
            contact.value = value  # type: ignore[assignment]
        if is_primary is not UNSET:
            contact.is_primary = bool(is_primary)
        contact.updated_at = utcnow()
        contact.__post_init__()
        self.updated_at = contact.updated_at
        return contact

    def remove_contact(self, contact_id: str) -> None:
        """Remove a contact from the aggregate."""
        contact = self.get_contact(contact_id)
        self.contacts.remove(contact)
        self.updated_at = utcnow()

    def add_address(
        self,
        line1: str,
        city: str,
        postal_code: str,
        country: str,
        *,
        label: str | None = None,
        line2: str | None = None,
        region: str | None = None,
        is_primary: bool = False,
    ) -> Address:
        """Add an address, enforcing at most one primary address."""
        if is_primary and any(address.is_primary for address in self.addresses):
            raise DuplicatePrimaryAddress("A primary address already exists")
        now = utcnow()
        address = Address(
            id=str(uuid4()),
            line1=line1,
            city=city,
            postal_code=postal_code,
            country=country,
            label=label,
            line2=line2,
            region=region,
            is_primary=is_primary,
            created_at=now,
            updated_at=now,
        )
        self.addresses.append(address)
        self.updated_at = now
        return address

    def get_address(self, address_id: str) -> Address:
        for address in self.addresses:
            if address.id == address_id:
                return address
        raise AddressNotFound(f"Address {address_id} was not found")

    def update_address(
        self,
        address_id: str,
        *,
        line1: str | _Unset = UNSET,
        city: str | _Unset = UNSET,
        postal_code: str | _Unset = UNSET,
        country: str | _Unset = UNSET,
        label: str | None | _Unset = UNSET,
        line2: str | None | _Unset = UNSET,
        region: str | None | _Unset = UNSET,
        is_primary: bool | _Unset = UNSET,
    ) -> Address:
        """Update an address and revalidate its values."""
        address = self.get_address(address_id)
        if is_primary is True and any(
            other.is_primary for other in self.addresses if other.id != address_id
        ):
            raise DuplicatePrimaryAddress("A primary address already exists")
        if line1 is not UNSET:
            address.line1 = line1  # type: ignore[assignment]
        if city is not UNSET:
            address.city = city  # type: ignore[assignment]
        if postal_code is not UNSET:
            address.postal_code = postal_code  # type: ignore[assignment]
        if country is not UNSET:
            address.country = country  # type: ignore[assignment]
        if label is not UNSET:
            address.label = label  # type: ignore[assignment]
        if line2 is not UNSET:
            address.line2 = line2  # type: ignore[assignment]
        if region is not UNSET:
            address.region = region  # type: ignore[assignment]
        if is_primary is not UNSET:
            address.is_primary = bool(is_primary)
        address.updated_at = utcnow()
        address.__post_init__()
        self.updated_at = address.updated_at
        return address

    def remove_address(self, address_id: str) -> None:
        """Remove an address from the aggregate."""
        address = self.get_address(address_id)
        self.addresses.remove(address)
        self.updated_at = utcnow()

    def eligibility_reasons(self) -> tuple[EligibilityReason, ...]:
        """Return every reason the customer is ineligible for business activity."""
        reasons: list[EligibilityReason] = []
        if self.status != CustomerStatus.ACTIVE:
            reasons.append(EligibilityReason.INACTIVE)
        if not self.contacts:
            reasons.append(EligibilityReason.NO_CONTACT)
        if not self.addresses:
            reasons.append(EligibilityReason.NO_ADDRESS)
        return tuple(reasons)

    @property
    def eligible(self) -> bool:
        """Whether the customer may participate in downstream business activity."""
        return not self.eligibility_reasons()
