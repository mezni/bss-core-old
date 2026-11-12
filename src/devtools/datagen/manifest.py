"""Manifest schema for the synthetic data generator.

Mirrors the Synthetic Data Set entity from
``specs/008-integration-mvp/contracts/data_generator_contract.md``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

GENERATOR_VERSION = "1.0.0"

DEFAULT_MANIFEST_PATH = "db/datagen-manifest.json"


@dataclass
class GenerationVolumes:
    """Requested generation volumes (requested counts and ranges)."""

    customers: int = 50
    orders: int = 100
    order_items_per_order: tuple[int, int] = (1, 3)
    shipments: int | None = None
    invoices: int | None = None
    payments: int | None = None

    def resolved(self) -> dict[str, int | None]:
        return {
            "customers": self.customers,
            "orders": self.orders,
            "order_items_per_order": self.order_items_per_order,
            "shipments": self.shipments,
            "invoices": self.invoices,
            "payments": self.payments,
        }


@dataclass
class GenerationCounts:
    """Actually created record counts, populated during generation."""

    customers: int = 0
    orders: int = 0
    order_items: int = 0
    shipments: int = 0
    invoices: int = 0
    payments: int = 0


@dataclass
class FKChains:
    """Validated referential chain counts, populated during generation."""

    orders_to_customers: int = 0
    shipments_to_orders: int = 0
    invoices_to_orders: int = 0
    payments_to_invoices: int = 0


@dataclass
class GenerationManifest:
    """The Synthetic Data Set manifest emitted after each run."""

    seed: int
    volumes: dict[str, Any] = field(default_factory=dict)
    created: GenerationCounts = field(default_factory=GenerationCounts)
    fk_chains: FKChains = field(default_factory=FKChains)
    database_url: str = ""
    generator_version: str = GENERATOR_VERSION
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "generated_at": self.generated_at,
            "volumes": self.volumes,
            "created": vars(self.created),
            "fk_chains": vars(self.fk_chains),
            "database_url": self.database_url,
            "generator_version": self.generator_version,
        }


def write_manifest(manifest: GenerationManifest, path: str | Path) -> Path:
    """Persist the manifest as JSON, creating parent directories."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n")
    return target


def read_manifest(path: str | Path) -> dict[str, Any]:
    """Load a manifest from disk (used by determinism tests)."""
    return json.loads(Path(path).read_text())
