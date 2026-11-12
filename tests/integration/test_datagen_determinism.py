"""Determinism and failure-semantics tests for the synthetic data generator."""

from __future__ import annotations

import pytest
from sqlalchemy import MetaData, create_engine

from src.devtools.datagen.generator import DataGenerationError, DataGenerator
from src.devtools.datagen.manifest import GenerationVolumes, read_manifest
from src.models.billing_management.infrastructure.orm import Base as BillingBase
from src.models.customer_management.infrastructure.orm import Base as CustomerBase
from src.models.order_management.infrastructure.orm import Base as OrderBase
from src.models.shipment_management.infrastructure.orm import Base as ShipmentBase

ALL_BASES = (CustomerBase, OrderBase, ShipmentBase, BillingBase)


def _fresh_database(tmp_path, name: str) -> str:
    url = f"sqlite:///{tmp_path / name}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    combined = MetaData()
    for base in ALL_BASES:
        for table in base.metadata.tables.values():
            table.to_metadata(combined)
    combined.create_all(engine)
    engine.dispose()
    return url


def _volumes() -> GenerationVolumes:
    return GenerationVolumes(
        customers=5,
        orders=5,
        order_items_per_order=(1, 2),
        shipments=1,
        invoices=1,
        payments=1,
    )


def test_same_seed_produces_identical_manifests(tmp_path) -> None:
    """SC-003: same seed and volumes produce identical counts and FK chains."""
    manifests = []
    for index in range(2):
        url = _fresh_database(tmp_path, f"determinism-{index}.db")
        manifest_path = tmp_path / f"manifest-{index}.json"
        generator = DataGenerator(
            seed=1234, database_url=url, volumes=_volumes(), quiet=True
        )
        generator.generate(manifest_path=str(manifest_path))
        manifests.append(read_manifest(manifest_path))

    for key in ("seed", "volumes", "created", "fk_chains", "generator_version"):
        assert manifests[0][key] == manifests[1][key]

    assert manifests[0]["created"]["customers"] == 5
    assert manifests[0]["created"]["orders"] == 5
    assert manifests[0]["fk_chains"] == {
        "orders_to_customers": 5,
        "shipments_to_orders": 1,
        "invoices_to_orders": 1,
        "payments_to_invoices": 1,
    }


def test_orders_without_customers_fails_generation(tmp_path) -> None:
    """Invalid FK chains abort generation with a clear error."""
    url = _fresh_database(tmp_path, "invalid-fk.db")
    volumes = GenerationVolumes(
        customers=0, orders=3, order_items_per_order=(1, 1), shipments=0
    )
    generator = DataGenerator(seed=1, database_url=url, volumes=volumes, quiet=True)

    with pytest.raises(DataGenerationError, match="without customers"):
        generator.generate(manifest_path=str(tmp_path / "invalid.json"))


def test_requested_volumes_are_capped_by_available_parents(tmp_path) -> None:
    """Invoices never exceed the number of confirmed (unshipped) orders."""
    url = _fresh_database(tmp_path, "capped.db")
    volumes = GenerationVolumes(
        customers=3,
        orders=3,
        order_items_per_order=(1, 1),
        shipments=2,
        invoices=99,
        payments=99,
    )
    generator = DataGenerator(seed=2, database_url=url, volumes=volumes, quiet=True)
    manifest = generator.generate(manifest_path=str(tmp_path / "capped.json"))

    assert manifest.created.shipments == 2
    assert manifest.created.invoices <= 1
    assert manifest.created.payments <= manifest.created.invoices
