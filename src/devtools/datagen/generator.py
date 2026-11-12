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

from src.domain.database import SQLALCHEMY_DATABASE_URL, get_db

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
        """Composer stub — implemented in US1 (T020)."""
        return []

    def _generate_orders(self, session: Session, customer_ids: list[str]) -> list[str]:
        """Composer stub — implemented in US1 (T020)."""
        return []

    def _generate_shipments(self, session: Session, order_ids: list[str]) -> list[str]:
        """Composer stub — implemented in US2 (T030)."""
        return []

    def _generate_invoices(self, session: Session, order_ids: list[str]) -> list[str]:
        """Composer stub — implemented in US3 (T039)."""
        return []

    def _generate_payments(self, session: Session, invoice_ids: list[str]) -> list[str]:
        """Composer stub — implemented in US4 (T047)."""
        return []

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
        except Exception:
            session.rollback()
            raise
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
            "shipments": self.volumes.shipments if self.volumes.shipments is not None else counts.shipments,
            "invoices": self.volumes.invoices if self.volumes.invoices is not None else counts.invoices,
            "payments": self.volumes.payments if self.volumes.payments is not None else counts.payments,
        }


def override_get_db(generator: DataGenerator) -> Iterator[Session]:
    """Dependency override binding the consolidated app to the generator engine."""
    session = generator.session()
    try:
        yield session
    finally:
        session.close()
