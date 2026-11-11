# Contract: Dashboard UI

**Endpoint**: GET /dashboard

**Description**: Streamlit dashboard UI for operational data visualization and metric exploration.

**Summary**: Provide an interactive web interface for viewing aggregated business metrics with date filtering, role-based access, and chart visualizations.

**Authentication**: JWT token required. Same permission model as dashboard API.

**Query Parameters (via URL state)**:
- `period`: string (optional) — predefined period: "current_month", "current_quarter", "year_to_date"
- `start_date`: string (optional) — ISO-8601 date filter start
- `end_date`: string (optional) — ISO-8601 date filter end
- `category`: string (optional) — metric category: "customer", "order", "shipment", "billing"
- `refresh`: boolean (optional) — force on-demand refresh (default: false)

**Response**: HTML streamlit application page

**Page Components**:
1. **Metric Summary Bar**: Top-row display of key metrics with "last updated" timestamp
2. **Category Tabs**: Four tabs for customer, order, shipment, billing metrics
3. **Date Range picker**: Calendar widget for custom date range selection; preset buttons for "Current Month", "Current Quarter", "Year to Date"
4. **Metric Widgets**: Per-category display of value, unit, aggregation type, and trend sparkline
5. **Role indicator**: Visible badge showing user's role tier (operator/manager/admin) and corresponding metric access level
6. **Refresh control**: Manual refresh button; auto-refresh every 5 minutes (aligning with batch refresh interval)

**Error States**:
- **401 Unauthorized**: JWT token missing or invalid — login page redirect
- **403 Forbidden**: User role does not have access to requested metrics — appropriate error message
- **503 Service Unavailable**: Dashboard metric cache stale or refresh task failed — "Data being refreshed, please wait" message

**Responsive Design**: Mobile-friendly layout; collapsible sidebar on narrow screens; touch-friendly chart interactions

**Rate Limiting**: 100 requests/minute per user for API calls; WebSocket connections for real-time updates limited to 10 per user