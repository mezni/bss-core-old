"""Synthetic data generator core (skeleton).

Wires deterministic seeding (Faker + ``random.Random``) and canonical
engine/session handling per
``specs/008-integration-mvp/contracts/data_generator_contract.md``.

Module composers are filled in by user stories US1-US4:
- customers + orders + order items (T020)
- shipments (T030)
- invoices (T039)
- payments (T047)
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Any

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.database import SQLALCHEMY_DATABASE_URL
from src.models.billing_management.application.service import (
    BillingService as InvoiceBillingService,
)
from src.models.billing_management.domain.value_objects import PAYMENT_METHODS
from src.models.billing_management.infrastructure.order_adapter import (
    OrderModuleAdapter as BillingOrderAdapter,
)
from src.models.billing_management.infrastructure.repository import (
    InvoiceRepository,
    PaymentRepository,
)
from src.models.customer_management.application.commands import CreateCustomerCommand
from src.models.customer_management.application.service import CustomerEligibilityAdapter
from src.models.customer_management.application.use_cases import CustomerService
from src.models.customer_management.domain.value_objects import CustomerType
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)
from src.models.order_management.application.service import OrderService
from src.models.order_management.infrastructure.repository import (
    SQLAlchemyOrderRepository,
)
from src.models.shipment_management.application.service import ShipmentService
from src.models.shipment_management.infrastructure.order_adapter import (
    OrderModuleAdapter as ShipmentOrderAdapter,
)
from src.models.shipment_management.infrastructure.repository import ShipmentRepository

from .manifest import (
    DEFAULT_MANIFEST_PATH,
    FKChains,
    GenerationCounts,
    GenerationManifest,
    GenerationVolumes,
    write_manifest,
)


class DataGenerationError(Exception):
    """Raised when generation would violate an FK or domain constraint."""


class DataGenerator:
    """Generates interconnected synthetic data by composing module services."""

    def __init__(
        self,
        *,
        seed: int = 42,
        database_url: str | None = None,
        volumes: GenerationVolumes | None = None,
        quiet: bool = False,
    ) -> None:
        self.seed = seed
        self.database_url = database_url or SQLALCHEMY_DATABASE_URL
        self.volumes = volumes or GenerationVolumes()
        self.quiet = quiet
        self.faker = Faker()
        self.faker.seed_instance(seed)
        self.rng = random.Random(seed)
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None
        self._order_item_count = 0
        self._shipped_order_ids: set[str] = set()
        self._invoice_totals: dict[str, float] = {}

    def _progress(self, message: str) -> None:
        if not self.quiet:
            print(message)

    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self.database_url, connect_args={"check_same_thread": False}
            )
        return self._engine

    def session(self) -> Session:
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine(), autocommit=False, autoflush=False
            )
        return self._session_factory()

    def _generate_customers(self, session: Session) -> list[str]:
        """Create individual and business customers through the customer service."""
        service = CustomerService(SQLAlchemyCustomerRepository(session))
        customer_ids: list[str] = []
        for index in range(self.volumes.customers):
            customer_type = (
                CustomerType.INDIVIDUAL if index % 2 == 0 else CustomerType.BUSINESS
            )
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            display_name = f"{first_name} {last_name}"
            command = CreateCustomerCommand(
                customer_type=customer_type,
                display_name=display_name,
                first_name=first_name,
                last_name=last_name,
                legal_name=display_name if customer_type == CustomerType.BUSINESS else None,
                registration_number=(
                    f"REG-{index:08d}"
                    if customer_type == CustomerType.BUSINESS
                    else None
                ),
                email=self.faker.unique.email(),
            )
            customer = service.create(command)
            customer_ids.append(customer.id)
        return customer_ids

    def _generate_orders(self, session: Session, customer_ids: list[str]) -> list[str]:
        """Create and confirm orders that reference existing customers."""
        if not customer_ids:
            raise DataGenerationError("Cannot generate orders without customers")
        service = OrderService(
            repository=SQLAlchemyOrderRepository(session),
            eligibility=CustomerEligibilityAdapter(SQLAlchemyCustomerRepository(session)),
        )
        min_items, max_items = self.volumes.order_items_per_order
        order_ids: list[str] = []
        for index in range(self.volumes.orders):
            item_count = self.rng.randint(min_items, max_items)
            items = [
                {
                    "description": f"{self.faker.word()} {item_number}",
                    "quantity": self.rng.randint(1, 5),
                    "unit_price": round(self.rng.uniform(5, 500), 2),
                }
                for item_number in range(item_count)
            ]
            order = service.create(
                customer_id=customer_ids[index % len(customer_ids)], items=items
            )
            confirmed = service.confirm_order(order.id)
            order_ids.append(confirmed.id)
            self._order_item_count += item_count
        return order_ids

    def _generate_shipments(self, session: Session, order_ids: list[str]) -> list[str]:
        """Create shipments for distinct confirmed orders."""
        if not order_ids:
            return []
        requested = (
            self.volumes.shipments
            if self.volumes.shipments is not None
            else max(1, len(order_ids) // 3)
        )
        count = min(requested, len(order_ids))
        service = ShipmentService(
            repository=ShipmentRepository(session),
            orders=ShipmentOrderAdapter(
                OrderService(
                    repository=SQLAlchemyOrderRepository(session),
                    eligibility=CustomerEligibilityAdapter(
                        SQLAlchemyCustomerRepository(session)
                    ),
                )
            ),
        )
        shipment_ids: list[str] = []
        for order_id in order_ids[:count]:
            shipment = service.create_shipment(
                order_id=order_id, carrier_name=self.faker.company()
            )
            shipment_ids.append(shipment.id)
            self._shipped_order_ids.add(order_id)
        return shipment_ids

    def _generate_invoices(self, session: Session, order_ids: list[str]) -> list[str]:
        """Create at most one invoice per remaining confirmed order."""
        candidates = [
            order_id
            for order_id in order_ids
            if order_id not in self._shipped_order_ids
        ]
        if not candidates:
            return []
        requested = (
            self.volumes.invoices
            if self.volumes.invoices is not None
            else max(1, len(candidates) // 2)
        )
        count = min(requested, len(candidates))
        service = InvoiceBillingService(
            invoices=InvoiceRepository(session),
            payments=PaymentRepository(session),
            orders=BillingOrderAdapter(
                OrderService(
                    repository=SQLAlchemyOrderRepository(session),
                    eligibility=CustomerEligibilityAdapter(
                        SQLAlchemyCustomerRepository(session)
                    ),
                )
            ),
        )
        invoice_ids: list[str] = []
        for order_id in candidates[:count]:
            invoice = service.generate_invoice(order_id=order_id)
            invoice_ids.append(invoice.id)
            self._invoice_totals[invoice.id] = invoice.total_amount
        return invoice_ids

    def _generate_payments(self, session: Session, invoice_ids: list[str]) -> list[str]:
        """Create payments for pending invoices and mark them paid."""
        if not invoice_ids:
            return []
        requested = (
            self.volumes.payments
            if self.volumes.payments is not None
            else max(1, len(invoice_ids) // 2)
        )
        count = min(requested, len(invoice_ids))
        service = InvoiceBillingService(
            invoices=InvoiceRepository(session),
            payments=PaymentRepository(session),
            orders=BillingOrderAdapter(
                OrderService(
                    repository=SQLAlchemyOrderRepository(session),
                    eligibility=CustomerEligibilityAdapter(
                        SQLAlchemyCustomerRepository(session)
                    ),
                )
            ),
        )
        payment_ids: list[str] = []
        for invoice_id in invoice_ids[:count]:
            payment = service.process_payment(
                invoice_id=invoice_id,
                amount=self._invoice_totals[invoice_id],
                payment_method=self.rng.choice(PAYMENT_METHODS),
            )
            payment_ids.append(payment.id)
        return payment_ids

    def generate(self, manifest_path: str | None = None) -> GenerationManifest:
        """Run the full generation in FK dependency order and emit a manifest."""
        counts = GenerationCounts()
        fk_chains = FKChains()
        session = self.session()
        try:
            customer_ids = self._generate_customers(session)
            counts.customers = len(customer_ids)
            self._progress(f"generated {counts.customers} customers")

            order_ids = self._generate_orders(session, customer_ids)
            counts.orders = len(order_ids)
            counts.order_items = self._order_item_count
            fk_chains.orders_to_customers = len(order_ids)
            self._progress(f"generated {counts.orders} orders")

            shipment_ids = self._generate_shipments(session, order_ids)
            counts.shipments = len(shipment_ids)
            fk_chains.shipments_to_orders = len(shipment_ids)
            self._progress(f"generated {counts.shipments} shipments")

            invoice_ids = self._generate_invoices(session, order_ids)
            counts.invoices = len(invoice_ids)
            fk_chains.invoices_to_orders = len(invoice_ids)
            self._progress(f"generated {counts.invoices} invoices")

            payment_ids = self._generate_payments(session, invoice_ids)
            counts.payments = len(payment_ids)
            fk_chains.payments_to_invoices = len(payment_ids)
            self._progress(f"generated {counts.payments} payments")

            session.commit()
        except DataGenerationError:
            session.rollback()
            raise
        except Exception as error:
            session.rollback()
            raise DataGenerationError(str(error)) from error
        finally:
            session.close()

        manifest = GenerationManifest(
            seed=self.seed,
            volumes=self._resolved_volumes(counts),
            created=counts,
            fk_chains=fk_chains,
            database_url=self.database_url,
        )
        target = manifest_path or DEFAULT_MANIFEST_PATH
        write_manifest(manifest, target)
        self._progress(f"manifest written to {target}")
        return manifest

    def _resolved_volumes(self, counts: GenerationCounts) -> dict[str, Any]:
        return {
            "customers": self.volumes.customers,
            "orders": self.volumes.orders,
            "order_items_per_order": self.volumes.order_items_per_order,
            "shipments": (
                self.volumes.shipments
                if self.volumes.shipments is not None
                else counts.shipments
            ),
            "invoices": (
                self.volumes.invoices
                if self.volumes.invoices is not None
                else counts.invoices
            ),
            "payments": (
                self.volumes.payments
                if self.volumes.payments is not None
                else counts.payments
            ),
        }


def override_get_db(generator: DataGenerator) -> Iterator[Session]:
    """Dependency override binding the consolidated app to the generator engine."""
    session = generator.session()
    try:
        yield session
    finally:
        session.close()
