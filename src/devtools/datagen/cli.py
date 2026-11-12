"""CLI entry point for the ``bss-datagen`` console script.

Options mirror ``specs/008-integration-mvp/contracts/data_generator_contract.md``.
"""

from __future__ import annotations

import argparse
import sys

from src.domain.database import SQLALCHEMY_DATABASE_URL

from .generator import DataGenerationError, DataGenerator
from .manifest import DEFAULT_MANIFEST_PATH, GenerationVolumes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bss-datagen",
        description=(
            "Generate deterministic, interconnected synthetic data across all "
            "business modules (customers -> orders -> shipments -> invoices -> payments)."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help=(
            "Deterministic seed (Faker + random); "
            "same seed + volumes -> identical data (default: 42)"
        ),
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help=f"Target database URL (defaults to BSS_DATABASE_URL / {SQLALCHEMY_DATABASE_URL})",
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=50,
        help="Number of customers to generate (default: 50)",
    )
    parser.add_argument(
        "--orders",
        type=int,
        default=100,
        help="Number of orders, each referencing a generated customer (default: 100)",
    )
    parser.add_argument(
        "--order-items-per-order",
        type=int,
        default=None,
        help="Items per order; omit for a random 1-3 range per order",
    )
    parser.add_argument(
        "--shipments",
        type=int,
        default=None,
        help="Shipments to generate, each referencing a generated confirmed order",
    )
    parser.add_argument(
        "--invoices",
        type=int,
        default=None,
        help="Invoices to generate, each referencing a generated confirmed order",
    )
    parser.add_argument(
        "--payments",
        type=int,
        default=None,
        help="Payments to generate, each referencing a generated pending invoice",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default=DEFAULT_MANIFEST_PATH,
        help=f"Manifest output location (default: {DEFAULT_MANIFEST_PATH})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    item_range: tuple[int, int] = (1, 3)
    if args.order_items_per_order is not None:
        item_range = (args.order_items_per_order, args.order_items_per_order)

    volumes = GenerationVolumes(
        customers=args.customers,
        orders=args.orders,
        order_items_per_order=item_range,
        shipments=args.shipments,
        invoices=args.invoices,
        payments=args.payments,
    )

    generator = DataGenerator(
        seed=args.seed,
        database_url=args.database_url,
        volumes=volumes,
        quiet=args.quiet,
    )

    try:
        manifest = generator.generate(manifest_path=args.manifest_path)
    except DataGenerationError as error:
        print(f"generation failed: {error}", file=sys.stderr)
        return 1

    print(
        "generated "
        f"{manifest.created.customers} customers, "
        f"{manifest.created.orders} orders, "
        f"{manifest.created.shipments} shipments, "
        f"{manifest.created.invoices} invoices, "
        f"{manifest.created.payments} payments "
        f"(seed={manifest.seed})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
