# Contract: Dashboard API

**Endpoint**: GET /api/v1/dashboard/metrics

**Description**: Retrieve aggregated operational metrics for the dashboard, supporting date-based filtering and role-based visibility.

**Summary**: Get dashboard metrics across all categories (customer, order, shipment, billing) with optional date range filtering and role-tiered access control.

**Authentication**: JWT token required. Requires `user:view` for operator tier, `user:billing` for manager tier, `user:admin` for admin tier.

**Query Parameters**:
- `start_date`: string (optional) — ISO-8601 date filter start (e.g., "2026-01-01")
- `end_date`: string (optional) — ISO-8601 date filter end (e.g., "2026-11-11T23:59:59")
- `category`: string (optional) — filter by metric category: "customer", "order", "shipment", "billing"
- `role_tier`: string (optional) — filter by required role tier: "operator", "manager", "admin"
- `period`: string (optional) — predefined period: "current_month", "current_quarter", "year_to_date"
- `metric_name`: string (optional) — filter by specific metric name

**Response (200 OK)**:

```json
{
  "metrics": [
    {
      "metric_name": "string",
      "value": decimal,
      "unit": "string",
      "aggregation_type": "count|sum|average|minimum|maximum|percentage",
      "date_range_start": "ISO-8601 datetime",
      "date_range_end": "ISO-8601 datetime",
      "reporting_period": "current_month|current_quarter|year_to_date|custom",
      "category": "customer|order|shipment|billing",
      "category_specific_id": "string (nullable)",
      "role_tier": "operator|manager|admin (nullable)",
      "last_refreshed": "ISO-8601 datetime",
      "created_at": "ISO-8601 datetime",
      "updated_at": "ISO-8601 datetime"
    }
  ],
  "total": integer,
  "page": 1,
  "page_size": 50,
  "last_refreshed": "ISO-8601 datetime",
  "cache_ttl_seconds": 300
}
```

**Error Responses**:
- **400 Bad Request**: Invalid date format (start_date > end_date, non-ISO-8601 format)
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks required permission tier for requested metrics
  - Operator tier token required for operator-level metrics
  - Manager tier token required for manager-level metrics (billing, revenue)
  - Admin tier token required for admin-level metrics (all including sensitive financial data)
- **404 NOT FOUND**: No metrics found for given criteria

**Rate Limiting**: 100 requests/minute per user, 429 responses with Retry-A header