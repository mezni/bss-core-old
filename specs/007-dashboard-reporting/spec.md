# Feature Specification: Dashboard & Reporting (S06)

**Feature Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Created**: 2026-11-11

**Status**: Draft

**Input**: User description: "from docs/sprint-planning.md s06 — S06 Dashboard & Reporting: Provide operational visibility across business modules. Managers and operators need a consolidated view of business activities."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dashboard API (Priority: P1)
**Describe this user journey in plain language**:  
An authenticated user can retrieve aggregated operational metrics from the dashboard API, including customer, order, shipment, and billing statistics.

**Why this priority**:  
Dashboard is the primary operational visibility tool — without it, managers and operators lack awareness of business state. It's the gateway to all other metrics and enables data-driven decision-making.

**Independent Test**:  
Can be fully tested by calling the dashboard API endpoints and verifying returned metrics match expected values and aggregation rules. The test succeeds even if no other dashboard flows are exercised.

**Acceptance Scenarios**:
1. **Given** an authenticated user with appropriate permissions, **When** the dashboard API is called, **Then** the response includes aggregated metrics for customers, orders, shipments, and billing with correct aggregation and formatting. The test succeeds even if no other dashboard flows are exercised.
2. **Given** an unauthenticated user, **When** the dashboard API is called, **Then** the request is rejected with a 401 Unauthorized error.

---

### User Story 2 - Billing Metrics (Priority: P2)
**Describe this user journey in plain language**:  
An authenticated user can view billing statistics including invoice counts, payment totals, outstanding balances, and payment success rates.

**Why this priority**:  
Billing metrics are critical for financial oversight and revenue tracking. Operators need to understand the financial health of the business at a glance.

**Independent Test**:  
Can be fully tested by calling the billing metrics endpoint and verifying the returned statistics are correct, calculable from existing invoice/payment data. The test passes regardless of subsequent status changes.

**Acceptance Scenarios**:
1. **Given** invoices and payments exist in the system, **When** billing metrics are requested, **Then** the response includes invoice count, total volume, outstanding balance, and payment success rate calculated from the data. The test passes regardless of invoice ages or payment status distribution.
2. **Given** no invoices exist, **When** billing metrics are requested, **Then** the response shows zero counts and zero values with no error.

---

### User Story 3 - Dashboard UI (Priority: P3)
**Describe this user journey in plain language**:  
An authenticated user can access the Streamlit dashboard UI to visualize operational metrics through date-filtered charts and tables.

**Why this priority**:  
The UI provides an accessible, visual interface for non-technical stakeholders to explore business data. It extends the API capabilities with interactive filtering and visualization.

**Independent Test**:  
Can be fully tested by loading the Streamlit dashboard, applying date filters, and verifying the displayed metrics are consistent with API responses and correctly filtered by the selected date range. The test validates the boundary rules without requiring the full accounting workflow.

**Acceptance Scenarios**:
1. **Given** an authenticated user, **When** the dashboard UI is loaded, **Then** the page displays metrics widgets with correct aggregations and default date range (current month).
2. **Given** a user applies date filters, **When** the dashboard refreshes, **Then** all metrics are recalculated for the selected date period and ordered correctly (most recent first).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide dashboard API endpoints under `/api/v1/dashboard` for aggregated operational metrics
- **FR-002**: System MUST expose customer metrics (count, new users, active customers) through the dashboard API
- **FR-003**: System MUST expose order metrics (order count, volume, status distribution) through the dashboard API
- **FR-004**: System MUST expose shipment metrics (shipment count, delivery rate, average delivery time) through the dashboard API
- **FR-005**: System MUST expose billing metrics (invoice count, total revenue, outstanding balance, payment success rate) through the dashboard API
- **FR-006**: System MUST support date-based filtering for all dashboard metrics (start_date, end_date parameters)
- **FR-007**: System MUST enforce authentication and authorization for all dashboard endpoints (user:view for read, user:billing for certain views)
- **FR-008**: System MUST provide a Streamlit dashboard UI at `/dashboard` for operational data visualization
- **FR-009**: System MUST allow date range filtering in the dashboard UI (custom start/end dates, predefined periods: current month, current quarter, year-to-date)
- **FR-010**: System MUST cache dashboard metric results with appropriate TTL for performance optimization

### Key Entities *(include if feature involves data)*

- **Dashboard Metric**: Represents a single aggregated metric value with metadata. Key attributes: metric name, value, unit, aggregation type, date range, timestamp. Responsibility: Owns its aggregation logic; provides consistent metric definitions across API and UI; documents calculation methodology; supports deterministic generation using seeds for testing.

- **Reporting Period**: Represents a time range for metric aggregation. Key attributes: period name (e.g., "current month", "current quarter", "year-to-date"), start date, end date. Responsibility: Provides standard period definitions; supports custom date ranges; respects business day conventions and holidays.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dashboard API responds in under 500ms for all metric endpoints (aligned with operational visibility performance goals)
- **SC-002**: Dashboard UI loads in under 2 seconds with all metric widgets displayed
- **SC-003**: Billing metrics are accurate within 0.01% of exact invoice/payment totals (exact equality comparison, no tolerance)
- **SC-004**: 95% of dashboard API requests succeed with valid authentication and authorized permissions
- **SC-005**: Date filtering returns correct results for all predefined periods (current month, current quarter, year-to-date) and custom ranges
- **SC-006**: Unauthorized access to dashboard endpoints is rejected with appropriate error (401/403)
- **SC-007**: Dashboard metrics are consistent across API and UI presentations of the same data
- **SC-008**: Dashboard provides at least 4 distinct metric categories (customer, order, shipment, billing) with measurable outcomes

### Qualitative Measures

- Users can understand business state at a glance without needing to interpret internal codes
- Error messages for invalid operations are descriptive and actionable
- The dashboard UI is consistent across dashboard views and respects user permissions
- Operational data is presented in a clear, actionable format

## Assumptions

- **Existing order management (S03) provides orders for shipment and billing metric aggregation.**
- **Existing invoice data (S05) provides invoice and payment records for billing metrics.**
- **Customer data (S02) is available for customer metrics calculation.**
- **Dashboard metrics are read-only; no mutation of business data through dashboard operations.**
- **Performance target of 500ms for API responses and 2s for UI loading are acceptable for operational dashboard use.**
- **Existing authentication (S01 JWT with RBAC) provides `user:view` for read operations and `user:billing` for billing-related views.**
- **Date filtering supports standard periods: current month (full current calendar month), current quarter (full current calendar quarter), year-to-date (January 1st to current date).**
- **Custom date ranges are supported with start_date and end_date parameters in ISO-8601 format.**
- **Structured JSON logging is used for all dashboard API operations; no secrets are exposed.**
- **Synthetic data generation (S07-06) supports deterministic dashboard metric testing with seeded generation.**

## Dependencies

- **S01 Identity & Access**: JWT authentication and permission checks must be available for dashboard API endpoints; endpoints use `user:view` for read operations and `user:billing` for billing-related views.
- **S02 Customer Management**: Customer data must be available for customer metrics calculation.
- **S03 Order Management**: Order data must be available for order metrics calculation.
- **S04 Shipment Management**: Shipment data must be available for shipment metrics calculation.
- **S05 Billing**: Invoice and payment data must be available for billing metrics calculation.
- **S07 Data Generator**: Synthetic data generation must support deterministic dashboard metric testing.

## Notes

- Dashboard metrics are read-only; no mutation of business data through dashboard operations.
- All endpoints under `/api/v1/dashboard` versioned v1.
- JWT authentication required for all operations.
- Invoice total must exactly match associated order/shipment total (constitution alignment).
- Performance targets (500ms API, 2s UI) are aligned with constitution Section 4 technology stack.
- Structured JSON logging for all dashboard API operations; must not expose secrets.
- Metric definitions should be consistent across API and UI; duplicates or contradictions must be avoided.
- Date period definitions should align with business day conventions and standard calendar periods.
- Dashboard provides a consolidated operational view; individual module metrics belong in their respective module specifications.

## Scope boundary: Real-time WebSocket updates

**Decision**: Real-time metric updates via WebSocket connections.

**Rationale**: This choice provides live data updates for operational dashboards, enabling managers and operators to see the most current business state. While more complex to implement (requires WebSocket infrastructure, connection management, and state handling), it delivers the best user experience for an operational visibility dashboard. The initial implementation will support WebSocket-based metric broadcasting with fallback to on-demand calculation for clients that do not maintain open connections. This decision materially impacts API design (WebSocket endpoints vs REST), UI implementation (real-time chart updates vs periodic refresh), and performance requirements (lower per-request latency but higher infrastructure overhead). Alternative Option A (periodic batch aggregation) was considered but selected against for S06 MVP because the primary value proposition of a dashboard is current-state visibility, and stale data undermines this purpose.

**Impact**: API design requires WebSocket endpoints for metric broadcasting; UI implementation requires real-time chart updates and connection management; performance targets shift from per-request latency to connection overhead; testing requires WebSocket client simulation. Metric aggregation logic remains unchanged; only the delivery mechanism changes.

---

## User types and permissions: Differentiated access by role

**Decision**: Dashboard access differentiated by user role with metric visibility tiers.

**Rationale**: This choice ensures appropriate data exposure per stakeholder role: operators need day-to-day operational metrics (order status, shipment tracking, recent invoices), managers need summary+detail metrics across all modules including financial summary, and admins need all metrics including sensitive financial data and system configuration. Differentiated access requires additional permission checks (`user:view` for operators, `user:billing` for managers, `user:admin` for admins) and potentially separate metric definitions, but ensures a stronger security posture and prevents data exposure beyond what each role legitimately needs. Uniform access was considered but selected against because the dashboard serves multiple stakeholder roles with fundamentally different data needs, and a single access level would either under-provide for power users or over-expose for basic operators.

**Impact**: API design requires role-based permission checks at the dashboard endpoint level; UI implementation requires role-aware metric widgets and access-controlled sections; additional test cases for each role's metric visibility; metric definitions may vary slightly by role (e.g., operators see "recent invoices" while managers see "all invoices with totals"). Metric aggregation logic remains fundamentally the same; only the visibility filtering and permission checks differ.

**Role-to-metric mapping**:
- **Operator** (`user:view`): Order metrics, shipment metrics, recent invoices, operational alerts
- **Manager** (`user:billing`): All operator metrics plus billing metrics, revenue summaries, outstanding balances
- **Admin** (`user:admin`): All metrics including sensitive financial data, system configuration, user management, audit logs

---

## Data freshness: Batch refresh every 5 minutes

**Decision**: Batch refresh every 5 minutes via background task.

**Rationale**: This choice balances data freshness with implementation complexity for the S06 MVP. Metrics are refreshed every 5 minutes through a lightweight background task, ensuring data is current enough for operational decision-making while avoiding the infrastructure overhead of real-time WebSocket connections (Option C) or the potential latency of on-demand calculation (Option A). Industry research and practice for operational dashboards indicates that 5-15 minute refresh intervals are standard and acceptable for most business use cases. The 5-minute interval provides a reasonable compromise: data is stale by at most 5 minutes, which is negligible for most managerial decision-making, while the implementation remains straightforward with a scheduled Celery/APS task. Option A (on-demand per request) was considered but selected against because it can cause latency for complex aggregations across multiple modules. Option C (real-time WebSocket) was considered but selected against because the added infrastructure complexity is not justified by the marginal benefit for S06 MVP metrics.

**Implementation**: A scheduled background task (using APScheduler or Celery beat) refreshes all dashboard metric caches every 5 minutes. The task calculates all aggregated metrics and stores them in the cache with a TTL matching the 5-minute refresh interval. On-request API endpoints serve from the cache, ensuring consistent performance regardless of aggregation complexity. The UI polling interval aligns with the refresh interval (5 minutes), or users can trigger on-demand refresh manually.

**Impact**: Requires background task infrastructure (APScheduler/Celery); adds cache layer to API endpoints; UI must display "last updated" timestamp; testing must include scheduled task execution; performance is improved for repeated requests since metrics are pre-computed. Metric aggregation calculations remain the same; only the caching and refresh mechanism changes.

---

## Traceability

- **Feature**: S06 Dashboard & Reporting — Sprint 06, BSS Core Agile/Scrum project
- **Related specs**: S01 Identity & Access, S02 Customer Management, S03 Order Management, S04 Shipment Management, S05 Billing Management
- **Related entities**: Dashboard Metric, Reporting Period
- **Related requirements**: FR-001 to FR-010
- **Related success criteria**: SC-001 to SC-008
- **Related assumptions**: All assumptions listed above
- **Related dependencies**: S01, S02, S03, S04, S05, S07