# Contract: Synthetic Data Generator (`bss-datagen`)

**Applies to**: The `src/devtools/datagen` package, exposed as the `bss-datagen` console script (uv-managed entry point).

**Description**: Generates deterministic, interconnected synthetic data across all business modules by composing module application services (constitution Section 12: realistic data, related records, FK respect, deterministic seeds, configurable volumes, no business-logic duplication, no production credentials).

**CLI interface**:

```bash
uv run bss-datagen [--seed SEED] [--database-url URL]
                   [--customers N] [--orders N] [--order-items-per-order N]
                   [--shipments N] [--invoices N] [--payments N]
                   [--manifest-path PATH] [--quiet]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--seed` | integer | `42` | Deterministic seed (Faker + random); same seed + same volumes → identical data |
| `--database-url` | string | canonical engine URL | Target database (defaults to `BSS_DATABASE_URL`) |
| `--customers` | integer | `50` | Number of customers to generate |
| `--orders` | integer | `100` | Number of orders (each references a generated customer) |
| `--order-items-per-order` | integer | `1–3` (random within range) | Items per order |
| `--shipments` | integer | proportional (≤ orders) | Shipments (each references a generated confirmed order) |
| `--invoices` | integer | proportional (≤ orders) | Invoices (each references a generated confirmed order; no duplicates) |
| `--payments` | integer | proportional (≤ invoices) | Payments (each references a generated pending invoice; marks it paid) |
| `--manifest-path` | string | `db/datagen-manifest.json` | Manifest output location |
| `--quiet` | flag | off | Suppress progress output |

**Generation order (FK dependency order)**:

```text
customers -> orders (+ order items) -> shipments -> invoices -> payments
```

**FK constraints (validated at generation time — invalid seeds fail the run)**:

- Every order references an existing customer
- Every shipment references an existing (confirmed) order
- Every invoice references an existing (confirmed) order, at most one per order
- Every payment references an existing (pending) invoice; payment marks it paid

**Manifest output** (Synthetic Data Set entity — see `data-model.md`):

```json
{
  "seed": 42,
  "generated_at": "2026-11-11T12:00:00Z",
  "volumes": {"customers": 50, "orders": 100, "order_items_per_order": 2,
              "shipments": 60, "invoices": 70, "payments": 55},
  "created": {"customers": 50, "orders": 100, "order_items": 210,
              "shipments": 60, "invoices": 70, "payments": 55},
  "fk_chains": {"orders_to_customers": 100, "shipments_to_orders": 60,
                "invoices_to_orders": 70, "payments_to_invoices": 55},
  "database_url": "sqlite:///./db/bss_core.db",
  "generator_version": "1.0.0"
}
```

**Behavioral guarantees**:

- **Determinism (SC-003)**: same `--seed` and volumes on a clean database produce byte-identical manifests and identical referential chains
- **Invariant safety**: all records pass module domain validation (realistic Faker values — names, addresses, prices, quantities within valid ranges; invoice numbers follow `INV-` format)
- **Failure semantics**: any FK violation or domain-validation failure aborts the run with a clear error before partial data is committed (per clarified constraint — no dangling references)
- **No secrets**: no real credentials or production data; dev-only tooling

**Integration test usage**: e2e journey tests invoke the generator programmatically with fixed seeds against a temporary database, then assert workflow outcomes on the generated data.
