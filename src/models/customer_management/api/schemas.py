"""Pydantic request and response schemas for the customer API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..domain.value_objects import ContactType, CustomerStatus, CustomerType


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _ResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(_StrictModel):
    customer_type: CustomerType
    display_name: str = Field(min_length=1, max_length=255)
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    legal_name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    registration_number: str | None = Field(default=None, max_length=64)


class CustomerUpdate(_StrictModel):
    version: int = Field(ge=1)
    customer_type: CustomerType | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    legal_name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    registration_number: str | None = Field(default=None, max_length=64)


class ContactCreate(_StrictModel):
    name: str = Field(min_length=1, max_length=120)
    contact_type: ContactType
    value: str = Field(min_length=1, max_length=320)
    is_primary: bool = False


class ContactUpdate(_StrictModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    contact_type: ContactType | None = None
    value: str | None = Field(default=None, min_length=1, max_length=320)
    is_primary: bool | None = None


class AddressCreate(_StrictModel):
    label: str | None = Field(default=None, max_length=80)
    line1: str = Field(min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    postal_code: str = Field(min_length=1, max_length=32)
    country: str = Field(min_length=2, max_length=2)
    is_primary: bool = False


class AddressUpdate(_StrictModel):
    version: int = Field(ge=1)
    label: str | None = Field(default=None, max_length=80)
    line1: str | None = Field(default=None, min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, min_length=1, max_length=32)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    is_primary: bool | None = None


class VersionRequest(_StrictModel):
    version: int = Field(ge=1)


class ContactResponse(_ResponseModel):
    id: str
    customer_id: str
    name: str
    contact_type: ContactType
    value: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class AddressResponse(_ResponseModel):
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


class CustomerResponse(_ResponseModel):
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
    contacts: list[ContactResponse]
    addresses: list[AddressResponse]
    created_at: datetime
    updated_at: datetime


class CustomerSummaryResponse(_ResponseModel):
    id: str
    customer_type: CustomerType
    display_name: str
    status: CustomerStatus
    eligible: bool
    version: int
    updated_at: datetime


class CustomerListResponse(_ResponseModel):
    items: list[CustomerSummaryResponse]
    page: int
    page_size: int
    total: int


class EligibilityResponse(_ResponseModel):
    customer_id: str
    eligible: bool
    reasons: list[str]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail
