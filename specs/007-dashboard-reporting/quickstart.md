# Quickstart: Dashboard & Reporting Validation

**Generated**: 2026-11-11
**Feature**: Dashboard & Reporting (S06)
**Spec**: specs/007-dashboard-reporting/spec.md
**Research**: specs/007-dashboard-reporting/research.md
**Contracts**: contracts/

## Prerequisites

- Python 3.12+ installed
- UV package manager configured
- BSS-Core repository cloned and dependencies installed (`uv sync`)
- SQLite3 available (comes with Python)
- JWT authentication token for API tests (obtain via S01 auth flow with appropriate role tier)

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Apply database migrations
cd src
alembic upgrade head

# 3. Start the backend server
uv run uvicorn main:app --reload

# 4. (Optional) Run tests
uv run pytest tests/ -v
```

## Validation Scenarios

### Scenario 1: Dashboard API - Retrieve Metrics (P1 - Core Flow)

**Goal**: Verify an authenticated operator can retrieve dashboard metrics.

**Steps**:
1. Obtain a valid JWT token for an operator-tier user (from S01 auth flow with `user:view` scope)
2. GET `/api/v1/dashboard/metrics` with no filters
3. Verify response status: `200 OK`
4. Verify response contains `metrics` array with items having: `metric_name`, `value`, `unit`, `aggregation_type`, `category`, `last_refreshed`
5. Verify at least one metric from each category (customer, order, shipment, billing) is present
6. Verify `last_refreshed` timestamp is recent (within 5-minute window)

**Expected outcome**: Metrics are returned across all four categories with valid values, units, and recent refresh timestamps.

---

### Scenario 2: Dashboard API - Date Range Filtering (P2 - Date Filtering)

**Goal**: Verify date-based filtering works correctly for dashboard metrics.

**Steps**:
1. Obtain a valid JWT token for an operator-tier user
2. GET `/api/v1/dashboard/metrics?start_date=2026-11-01&end_date=2026-11-11`
3. Verify response status: `200 OK`
4. Verify all returned metrics have `date_range_start` >= `2026-11-01` and `date_range_end` <= `2026-11-11`
5. Verify metrics outside the date range are excluded

**Expected outcome**: Only metrics within the specified date range are returned; metrics outside the range are excluded.

---

### Scenario 3: Dashboard API - Predefined Period (P2 - Period Filtering)

**Goal**: Verify predefined period filtering works correctly.

**Steps**:
1. Obtain a valid JWT token for an operator-tier user
2. GET `/api/v1/dashboard/metrics?period=current_month`
3. Verify response status: `200 OK`
4. Verify `reporting_period` field in metrics is `"current_month"`
5. Verify metrics correspond to current calendar month (November 2026)

**Steps**:
1. GET `/api/v1/dashboard/metrics?period=current_quarter`
2. Verify `reporting_period` field is `"current_quarter"`

**Steps**:
1. GET `/api/v1/dashboard/metrics?period=year_to_date`
2. Verify `reporting_period` field is `"year_to_date"`

**Expected outcome**: Predefined periods are correctly recognized and metrics are filtered accordingly.

---

### Scenario 4: Dashboard UI - Access by Role Tier (P2 - Role Differentiation)

**Goal**: Verify role-based access control works in the dashboard UI.

**Steps**:
1. Log in with operator-tier user (JWT `user:view` scope) and access `/dashboard`
2. Verify dashboard loads with operator-level metrics (order, shipment, recent invoices)
3. Verify "operator" role badge is displayed
4. Verify billing-level metrics (revenue, outstanding balances) are NOT visible to operator
5. Log in with manager-tier user (JWT `user:billing` scope) and access `/dashboard`
6. Verify dashboard loads with manager-level metrics (all operator metrics + billing)
7. Verify "manager" role badge is displayed
8. Log in with admin-tier user (JWT `user:admin` scope) and access `/dashboard`
9. Verify dashboard loads with full metric access (all categories including sensitive financial data)
10. Verify "admin" role badge is displayed

**Expected outcome**: Each role tier sees only the metrics appropriate for their access level, with corresponding role badge displayed.

---

### Scenario 5: Dashboard API - Role Tier Access Control (P2 - Permission Enforcement)

**Goal**: Verify that role tier enforcement correctly rejects unauthorized metric access.

**Steps**:
1. Obtain a valid JWT token for an operator-tier user ( `user:view` scope)
2. GET `/api/v1/dashboard/metrics` with a query that would require manager tier (e.g., include billing metrics)
3. Verify response status: `403 Forbidden`
4. Verify error response contains clear message about insufficient permissions

**Steps**:
1. Obtain a valid JWT token for a manager-tier user ( `user:billing` scope)
2. GET `/api/v1/dashboard/metrics` with a query that would require admin tier (e.g., include system configuration metrics)
3. Verify response status: `403 Forbidden`
4. Verify error response contains clear message about insufficient permissions

**Expected outcome**: Unauthorized role tier access is rejected with 403 and clear error message.

---

### Scenario 6: Dashboard API - Metric Freshness (P3 - Data Freshness)

**Goal**: Verify that metric freshness is enforced per the 5-minute batch refresh interval.

**Steps**:
1. Obtain a valid JWT token for an operator-tier user
2. GET `/api/v1/dashboard/metrics` - note the `last_refreshed` timestamp
3. Wait approximately 5+ minutes (or manually set a metric's `last_refreshed` to an old timestamp via database admin)
4. GET `/api/v1/dashboard/metrics` again
5. Verify the `last_refreshed` timestamp has been updated to the new refresh time

**Alternative Step** (without waiting):
1. GET `/api/v1/dashboard/metrics?force_refresh=true` (if endpoint supports it)
2. Verify `last_refreshed` is updated to current time

**Expected outcome**: Metric data freshness is maintained per the 5-minute refresh interval; cache is refreshed on schedule or on-demand.

---

## Expected Outcomes Summary

| Scenario | Pass Criteria |
|---|---|
| 1. Retrieve Metrics | 200; metrics across all 4 categories; recent refresh |
| 2. Date Range Filtering | 200; metrics within range only; out-of-range excluded |
| 3. Predefined Period | 200; reporting_period matches requested period |
| 4. UI Role Access | Each role sees appropriate metrics; role badge correct |
| 5. Role Enforcement | 403 for unauthorized tier; clear error message |
| 6. Metric Freshness | `last_refreshed` updates within 5-min interval |

## Notes

- All dashboard API endpoints are under `/api/v1/dashboard` versioned v1
- JWT authentication required for all operations
- Role-based access control: operator (`user:view`), manager (`user:billing`), admin (`user:admin`)
- Metrics are read-only; no mutation of business data through dashboard operations
- Performance target: API responds in under 500ms; UI loads in under 2 seconds
- Data freshness: batch refresh every 5 minutes via background task
- Metric definitions should be consistent across API and UI; duplicates or contradictions must be avoided
- Structured JSON logging for all dashboard API operations; must not expose secrets
- Metric categories: customer, order, shipment, billing — aligned with S02, S03, S04, S05 module specifications
- Invoice total must exactly match associated order/shipment total (constitution alignment)