"""Enums and value objects for the customer management domain."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s().-]{4,24}$")
_REGISTRATION_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9\-./]{1,63}$")


class CustomerType(StrEnum):
    """The legal classification of a customer."""

    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"


class CustomerStatus(StrEnum):
    """Lifecycle status of a customer."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ContactType(StrEnum):
    """Supported customer contact channels."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"


class EligibilityReason(StrEnum):
    """Reasons a customer is not eligible for downstream business activity."""

    INACTIVE = "INACTIVE"
    NO_CONTACT = "NO_CONTACT"
    NO_ADDRESS = "NO_ADDRESS"


@dataclass(frozen=True, slots=True)
class Email:
    """A validated, normalized email address."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_PATTERN.match(normalized):
            raise ValueError("Invalid email address")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class RegistrationNumber:
    """A validated, normalized business registration or tax identifier."""

    value: str

    def __post_init__(self) -> None:
        normalized = re.sub(r"\s+", "", self.value).upper()
        if not _REGISTRATION_PATTERN.match(normalized):
            raise ValueError("Invalid registration number")
        object.__setattr__(self, "value", normalized)


def normalize_email(value: str) -> str:
    """Return the normalized form of an email address or raise ``ValueError``."""
    return Email(value).value


def normalize_registration_number(value: str) -> str:
    """Return the normalized form of a registration number or raise ``ValueError``."""
    return RegistrationNumber(value).value


def normalize_phone(value: str) -> str:
    """Validate and normalize a phone number or raise ``ValueError``."""
    normalized = value.strip()
    if not _PHONE_PATTERN.match(normalized):
        raise ValueError("Invalid phone number")
    return normalized
