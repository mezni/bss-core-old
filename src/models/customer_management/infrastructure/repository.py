"""SQLAlchemy implementation of the customer repository port."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.entities import Address, Contact, Customer, normalize_datetime
from ..domain.exceptions import (
    CustomerNotFound,
    DuplicateCustomer,
    DuplicatePrimaryAddress,
    DuplicatePrimaryContact,
    StaleUpdate,
)
from ..domain.repositories import CustomerRepository
from ..domain.value_objects import (
    ContactType,
    CustomerStatus,
    CustomerType,
    normalize_email,
    normalize_registration_number,
)
from .orm import AddressORM, ContactORM, CustomerORM


class SQLAlchemyCustomerRepository(CustomerRepository):
    """Persist customer aggregates in SQLAlchemy-backed tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, customer: Customer) -> Customer:
        orm = self._to_orm(customer)
        self.session.add(orm)
        self._commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get(self, customer_id: str) -> Customer | None:
        orm = self.session.get(CustomerORM, customer_id)
        if orm is None:
            return None
        return self._to_domain(orm)

    def update(self, customer: Customer, expected_version: int) -> Customer:
        orm = self.session.get(CustomerORM, customer.id)
        if orm is None:
            raise CustomerNotFound(f"Customer {customer.id} was not found")
        if orm.version != expected_version:
            raise StaleUpdate(expected_version, orm.version)

        self._apply(orm, customer)
        orm.version = expected_version + 1
        self._commit()
        self.session.refresh(orm)
        customer.version = orm.version
        return self._to_domain(orm)

    def search(
        self,
        *,
        q: str | None = None,
        customer_type: CustomerType | None = None,
        status: CustomerStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Customer], int]:
        stmt = select(CustomerORM)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    CustomerORM.display_name.ilike(pattern),
                    CustomerORM.email.ilike(pattern),
                    CustomerORM.registration_number.ilike(pattern),
                )
            )
        if customer_type is not None:
            stmt = stmt.where(CustomerORM.customer_type == CustomerType(customer_type).value)
        if status is not None:
            stmt = stmt.where(CustomerORM.status == CustomerStatus(status).value)

        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        rows = self.session.scalars(
            stmt.order_by(CustomerORM.created_at.desc(), CustomerORM.id)
            .offset(offset)
            .limit(page_size)
        ).all()
        return [self._to_domain(row) for row in rows], int(total)

    def exists_identity(
        self,
        customer_type: CustomerType,
        *,
        email: str | None = None,
        registration_number: str | None = None,
        exclude_id: str | None = None,
    ) -> bool:
        stmt = select(CustomerORM.id)
        if CustomerType(customer_type) == CustomerType.INDIVIDUAL:
            if not email:
                return False
            try:
                normalized = normalize_email(email)
            except ValueError:
                normalized = email.strip().lower()
            stmt = stmt.where(
                CustomerORM.customer_type == CustomerType.INDIVIDUAL.value,
                CustomerORM.email == normalized,
            )
        else:
            if not registration_number:
                return False
            try:
                normalized = normalize_registration_number(registration_number)
            except ValueError:
                normalized = registration_number.strip().upper()
            stmt = stmt.where(
                CustomerORM.customer_type == CustomerType.BUSINESS.value,
                CustomerORM.registration_number == normalized,
            )
        if exclude_id is not None:
            stmt = stmt.where(CustomerORM.id != exclude_id)
        return self.session.scalar(stmt.limit(1)) is not None

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise self._translate_integrity_error(exc) from exc

    @staticmethod
    def _translate_integrity_error(exc: IntegrityError) -> Exception:
        message = str(exc.orig).lower()
        if "uq_customers_individual_email" in message or "customers.email" in message:
            return DuplicateCustomer("An individual customer with this email already exists")
        if (
            "uq_customers_business_registration" in message
            or "customers.registration_number" in message
        ):
            return DuplicateCustomer(
                "A business customer with this registration number already exists"
            )
        if "uq_customer_contacts_primary" in message or "customer_contacts" in message:
            return DuplicatePrimaryContact("A primary contact already exists")
        if "uq_customer_addresses_primary" in message or "customer_addresses" in message:
            return DuplicatePrimaryAddress("A primary address already exists")
        return DuplicateCustomer("Customer data violates a uniqueness constraint")

    @staticmethod
    def _to_orm(customer: Customer) -> CustomerORM:
        orm = CustomerORM(
            id=customer.id,
            customer_type=customer.customer_type.value,
            display_name=customer.display_name,
            first_name=customer.first_name,
            last_name=customer.last_name,
            legal_name=customer.legal_name,
            email=customer.email,
            registration_number=customer.registration_number,
            status=customer.status.value,
            version=customer.version,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        orm.contacts = [
            ContactORM(
                id=contact.id,
                customer_id=customer.id,
                name=contact.name,
                contact_type=contact.contact_type.value,
                value=contact.value,
                is_primary=contact.is_primary,
                created_at=contact.created_at,
                updated_at=contact.updated_at,
            )
            for contact in customer.contacts
        ]
        orm.addresses = [
            AddressORM(
                id=address.id,
                customer_id=customer.id,
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
            for address in customer.addresses
        ]
        return orm

    @staticmethod
    def _apply(orm: CustomerORM, customer: Customer) -> None:
        orm.customer_type = customer.customer_type.value
        orm.display_name = customer.display_name
        orm.first_name = customer.first_name
        orm.last_name = customer.last_name
        orm.legal_name = customer.legal_name
        orm.email = customer.email
        orm.registration_number = customer.registration_number
        orm.status = customer.status.value
        orm.updated_at = customer.updated_at

        existing_contacts = {contact.id: contact for contact in orm.contacts}
        for contact in customer.contacts:
            row = existing_contacts.pop(contact.id, None)
            if row is None:
                orm.contacts.append(
                    ContactORM(
                        id=contact.id,
                        customer_id=customer.id,
                        name=contact.name,
                        contact_type=contact.contact_type.value,
                        value=contact.value,
                        is_primary=contact.is_primary,
                        created_at=contact.created_at,
                        updated_at=contact.updated_at,
                    )
                )
            else:
                row.name = contact.name
                row.contact_type = contact.contact_type.value
                row.value = contact.value
                row.is_primary = contact.is_primary
                row.updated_at = contact.updated_at
        for removed in existing_contacts.values():
            orm.contacts.remove(removed)

        existing_addresses = {address.id: address for address in orm.addresses}
        for address in customer.addresses:
            row = existing_addresses.pop(address.id, None)
            if row is None:
                orm.addresses.append(
                    AddressORM(
                        id=address.id,
                        customer_id=customer.id,
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
                )
            else:
                row.label = address.label
                row.line1 = address.line1
                row.line2 = address.line2
                row.city = address.city
                row.region = address.region
                row.postal_code = address.postal_code
                row.country = address.country
                row.is_primary = address.is_primary
                row.updated_at = address.updated_at
        for removed in existing_addresses.values():
            orm.addresses.remove(removed)

    @staticmethod
    def _to_domain(orm: CustomerORM) -> Customer:
        return Customer(
            id=orm.id,
            customer_type=CustomerType(orm.customer_type),
            display_name=orm.display_name,
            status=CustomerStatus(orm.status),
            version=orm.version,
            first_name=orm.first_name,
            last_name=orm.last_name,
            legal_name=orm.legal_name,
            email=orm.email,
            registration_number=orm.registration_number,
            created_at=normalize_datetime(orm.created_at),
            updated_at=normalize_datetime(orm.updated_at),
            contacts=[
                Contact(
                    id=contact.id,
                    name=contact.name,
                    contact_type=ContactType(contact.contact_type),
                    value=contact.value,
                    is_primary=contact.is_primary,
                    created_at=normalize_datetime(contact.created_at),
                    updated_at=normalize_datetime(contact.updated_at),
                )
                for contact in orm.contacts
            ],
            addresses=[
                Address(
                    id=address.id,
                    label=address.label,
                    line1=address.line1,
                    line2=address.line2,
                    city=address.city,
                    region=address.region,
                    postal_code=address.postal_code,
                    country=address.country,
                    is_primary=address.is_primary,
                    created_at=normalize_datetime(address.created_at),
                    updated_at=normalize_datetime(address.updated_at),
                )
                for address in orm.addresses
            ],
        )
