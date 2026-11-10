"""Application use cases for customer management."""

from __future__ import annotations

from ..domain.entities import Customer
from ..domain.exceptions import CustomerNotFound, DuplicateCustomer, StaleUpdate
from ..domain.repositories import CustomerRepository
from ..domain.value_objects import CustomerType
from ..infrastructure.logging import log_lifecycle
from .commands import (
    AddAddressCommand,
    AddContactCommand,
    ChangeCustomerTypeCommand,
    CreateCustomerCommand,
    DeactivateCustomerCommand,
    ReactivateCustomerCommand,
    RemoveAddressCommand,
    RemoveContactCommand,
    UpdateAddressCommand,
    UpdateContactCommand,
    UpdateCustomerCommand,
)
from .dto import (
    CustomerDetailsDTO,
    CustomerEligibilityDTO,
    CustomerListDTO,
    address_to_dto,
    contact_to_dto,
    customer_to_details,
    customer_to_summary,
)
from .queries import CustomerSearchQuery

_IDENTITY_FIELDS = (
    "display_name",
    "first_name",
    "last_name",
    "legal_name",
    "email",
    "registration_number",
)
_CONTACT_FIELDS = ("name", "contact_type", "value", "is_primary")
_ADDRESS_FIELDS = (
    "label",
    "line1",
    "line2",
    "city",
    "region",
    "postal_code",
    "country",
    "is_primary",
)


class CustomerService:
    """Coordinates customer lifecycle and child-entity use cases."""

    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def create(self, command: CreateCustomerCommand) -> CustomerDetailsDTO:
        customer = Customer.create(
            command.customer_type,
            command.display_name,
            first_name=command.first_name,
            last_name=command.last_name,
            legal_name=command.legal_name,
            email=command.email,
            registration_number=command.registration_number,
        )
        self._ensure_unique(customer)
        saved = self.repository.add(customer)
        log_lifecycle(
            "create", saved.id, status=saved.status.value, version=saved.version
        )
        return customer_to_details(saved)

    def get(self, customer_id: str) -> CustomerDetailsDTO:
        return customer_to_details(self._get(customer_id))

    def update(self, command: UpdateCustomerCommand) -> CustomerDetailsDTO:
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        changes = {
            key: value
            for key, value in command.changes.items()
            if key in _IDENTITY_FIELDS or key == "customer_type"
        }
        customer_type = changes.pop("customer_type", None)
        if customer_type is not None:
            customer.change_type(customer_type, **changes)
        else:
            customer.update(**changes)
        self._ensure_unique(customer, exclude_id=customer.id)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "update", saved.id, status=saved.status.value, version=saved.version
        )
        return customer_to_details(saved)

    def change_type(self, command: ChangeCustomerTypeCommand) -> CustomerDetailsDTO:
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        changes = {
            key: value for key, value in command.changes.items() if key in _IDENTITY_FIELDS
        }
        customer.change_type(command.customer_type, **changes)
        self._ensure_unique(customer, exclude_id=customer.id)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "change_type", saved.id, status=saved.status.value, version=saved.version
        )
        return customer_to_details(saved)

    def deactivate(self, command: DeactivateCustomerCommand) -> CustomerDetailsDTO:
        customer = self._get(command.customer_id)
        customer.deactivate()
        saved = self.repository.update(customer, customer.version)
        log_lifecycle(
            "deactivate", saved.id, status=saved.status.value, version=saved.version
        )
        return customer_to_details(saved)

    def reactivate(self, command: ReactivateCustomerCommand) -> CustomerDetailsDTO:
        customer = self._get(command.customer_id)
        customer.reactivate()
        saved = self.repository.update(customer, customer.version)
        log_lifecycle(
            "reactivate", saved.id, status=saved.status.value, version=saved.version
        )
        return customer_to_details(saved)

    def add_contact(self, command: AddContactCommand):
        customer = self._get(command.customer_id)
        contact = customer.add_contact(
            command.name,
            command.contact_type,
            command.value,
            is_primary=command.is_primary,
        )
        saved = self.repository.update(customer, customer.version)
        log_lifecycle(
            "add_contact", saved.id, status=saved.status.value, version=saved.version
        )
        saved_contact = next(item for item in saved.contacts if item.id == contact.id)
        return contact_to_dto(saved_contact, saved.id)

    def update_contact(self, command: UpdateContactCommand):
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        changes = {
            key: value for key, value in command.changes.items() if key in _CONTACT_FIELDS
        }
        customer.update_contact(command.contact_id, **changes)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "update_contact", saved.id, status=saved.status.value, version=saved.version
        )
        saved_contact = next(
            item for item in saved.contacts if item.id == command.contact_id
        )
        return contact_to_dto(saved_contact, saved.id)

    def remove_contact(self, command: RemoveContactCommand) -> None:
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        customer.remove_contact(command.contact_id)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "remove_contact", saved.id, status=saved.status.value, version=saved.version
        )

    def add_address(self, command: AddAddressCommand):
        customer = self._get(command.customer_id)
        address = customer.add_address(
            command.line1,
            command.city,
            command.postal_code,
            command.country,
            label=command.label,
            line2=command.line2,
            region=command.region,
            is_primary=command.is_primary,
        )
        saved = self.repository.update(customer, customer.version)
        log_lifecycle(
            "add_address", saved.id, status=saved.status.value, version=saved.version
        )
        saved_address = next(item for item in saved.addresses if item.id == address.id)
        return address_to_dto(saved_address, saved.id)

    def update_address(self, command: UpdateAddressCommand):
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        changes = {
            key: value for key, value in command.changes.items() if key in _ADDRESS_FIELDS
        }
        customer.update_address(command.address_id, **changes)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "update_address", saved.id, status=saved.status.value, version=saved.version
        )
        saved_address = next(
            item for item in saved.addresses if item.id == command.address_id
        )
        return address_to_dto(saved_address, saved.id)

    def remove_address(self, command: RemoveAddressCommand) -> None:
        customer = self._get(command.customer_id)
        self._check_version(customer, command.version)
        customer.remove_address(command.address_id)
        saved = self.repository.update(customer, command.version)
        log_lifecycle(
            "remove_address", saved.id, status=saved.status.value, version=saved.version
        )

    def search(self, query: CustomerSearchQuery) -> CustomerListDTO:
        page = max(query.page, 1)
        page_size = min(max(query.page_size, 1), 100)
        customers, total = self.repository.search(
            q=query.q,
            customer_type=query.customer_type,
            status=query.status,
            page=page,
            page_size=page_size,
        )
        return CustomerListDTO(
            items=tuple(customer_to_summary(customer) for customer in customers),
            page=page,
            page_size=page_size,
            total=total,
        )

    def check_eligibility(self, customer_id: str) -> CustomerEligibilityDTO:
        customer = self._get(customer_id)
        return CustomerEligibilityDTO(
            customer_id=customer.id,
            eligible=customer.eligible,
            reasons=tuple(reason.value for reason in customer.eligibility_reasons()),
        )

    def _get(self, customer_id: str) -> Customer:
        customer = self.repository.get(customer_id)
        if customer is None:
            raise CustomerNotFound(f"Customer {customer_id} was not found")
        return customer

    @staticmethod
    def _check_version(customer: Customer, expected_version: int) -> None:
        if customer.version != expected_version:
            raise StaleUpdate(expected_version, customer.version)

    def _ensure_unique(
        self, customer: Customer, *, exclude_id: str | None = None
    ) -> None:
        if customer.customer_type == CustomerType.INDIVIDUAL:
            if self.repository.exists_identity(
                CustomerType.INDIVIDUAL,
                email=customer.email,
                exclude_id=exclude_id,
            ):
                raise DuplicateCustomer(
                    "An individual customer with this email already exists"
                )
        else:
            if self.repository.exists_identity(
                CustomerType.BUSINESS,
                registration_number=customer.registration_number,
                exclude_id=exclude_id,
            ):
                raise DuplicateCustomer(
                    "A business customer with this registration number already exists"
                )
