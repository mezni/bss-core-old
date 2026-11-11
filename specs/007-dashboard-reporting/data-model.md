# Data Model: Dashboard & Reporting (S06)

**Generated**: 2026-11-11
**Feature**: Dashboard & Reporting (S06)
**Spec**: specs/007-dashboard-reporting/spec.md

## Entity: Dashboard Metric

**Description**: Represents a single aggregated metric value with metadata. Dashboard metrics provide operational visibility across business modules (customer, order, shipment, billing) through the dashboard API and UI.

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `metric_name` | string | Name of the metric | Required; must be canonical name from dashboard metric registry; e.g., "active_orders", "revenue_this_quarter" |
| `value` | decimal | Current metric value | Required; precision: 2 decimal places; must be non-negative |
| `unit` | string | Unit of measurement | Required; e.g., "count", "currency", "percentage"; must be from canonical unit registry |
| `aggregation_type` | enum | Type of aggregation applied | Required; values: "count", "sum", "average", "minimum", "maximum", "percentage"; defaults to "count" |
| `date_range_start` | datetime | Start of aggregation period | Required; ISO-8601 format |
| `date_range_end` | datetime | End of aggregation period | Required; ISO-8601 format; must be >= date_range_start |
| `reporting_period` | string | Named reporting period | Required; values: "current_month", "current_quarter", "year_to_date", "custom"; defaults to "custom" |
| `category` | enum | Metric category | Required; values: "customer", "order", "shipment", "billing"; defines which business domain this metric belongs to |
| `category_specific_id` | string | Optional identifier for category-specific filtering | Optional; e.g., customer_id, order_id, shipment_id, invoice_id |
| `role_tier` | enum | Minimum role tier required to view this metric | Optional; values: "operator", "manager", "admin"; defines role-based visibility |
| `last_refreshed` | datetime | When metric data was last refreshed | Required; ISO-8601 format; auto-generated; indicates data freshness |
| `created_at` | datetime | When metric record was created | Required; ISO-8601 format; auto-generated |
| `updated_at` | datetime | When metric record was last updated | Required; ISO-8601 format; auto-generated; onupdate |

**Relationships**:
- Each metric belongs to exactly one category (customer, order, shipment, billing)
- Metrics with category_specific_id reference entities from S02 (customer), S03 (order), S04 (shipment), or S05 (billing)

**Business Invariants**:
- Metric value must be non-negative
- date_range_end must be >= date_range_start
- aggregation_type must be valid enum value
- category must be one of the four defined values
- role_tier, if specified, must be a valid role tier
- last_refreshed should not be older than the 5-minute refresh interval (per data freshness decision)

**Responsibility**: Owns its aggregation logic; provides consistent metric definitions across API and UI; documents calculation methodology; supports deterministic generation using seeds for testing; enforces role-based visibility constraints; ensures data freshness per 5-minute refresh interval.

---

## Entity: Reporting Period

**Description**: Represents a time range for metric aggregation. Provides standard period definitions and supports custom date ranges for dashboard metric calculations.

**Key Attributes**:

| Field | Type | Description | Constraints |
|---|---|---|---|
| `period_name` | string | Name of the reporting period | Required; must be canonical period name; values: "current_month", "current_quarter", "year_to_date", "custom" |
| `start_date` | datetime | Period start date | Required; ISO-8601 format; for "current_month": first day of current calendar month; for "current_quarter": first day of current calendar quarter; for "year_to_date": January 1st of current year; for "custom": start of custom range |
| `end_date` | datetime | Period end date | Required; ISO-8601 format; for "current_month": last day of current calendar month; for "current_quarter": last day of current calendar quarter; for "year_to_date": current date; for "custom": end of custom range |
| `is_custom` | boolean | Whether this is a custom period | Required; True for "custom" period, False for standard periods |
| `description` | string | Human-readable period description | Optional; e.g., "January 2026", "Q1 2026", "January 1 - January 31, 2026" |

**Relationships**:
- No direct relationships; period definitions are used as filter parameters for Dashboard Metric queries

**Business Invariants**:
- For standard periods, start_date and end_date must conform to the defined calendar conventions
- For custom periods, end_date must be >= start_date
- is_custom must be True iff period_name is "custom"
- end_date must be >= start_date for all period types

**Responsibility**: Provides standard period definitions; supports custom date ranges; respects business day conventions and holidays; enables consistent metric aggregation across API and UI.

## Validation Rules (from Requirements)

- **FR-006**: System MUST support date-based filtering for all dashboard metrics (start_date, end_date parameters)
- **FR-009**: System MUST allow date range filtering in the dashboard UI (custom start/end dates, predefined periods: current month, current quarter, year-to-date)
- Metrics outside the specified date range must be excluded from results
- Metrics within the specified date range must be included in results
- Custom date ranges must accept ISO-8601 start_date and end_date parameters
- Standard periods (current_month, current_quarter, year_to_date) must be supported without custom parameters