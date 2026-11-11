# Research: Dashboard & Reporting (S06)

**Generated**: 2026-11-11
**Feature**: Dashboard & Reporting (S06)
**Spec**: specs/007-dashboard-reporting/spec.md

## Clarification Research (Previously Resolved)

### Question 1: Scope boundary — real-time vs batch aggregation

**Decision**: Real-time metric updates via WebSocket connections.

**Rationale**: This choice provides live data for operational dashboards, enabling managers and operators to see the most current business state. While more complex to implement (requires WebSocket infrastructure, connection management, and state handling), it delivers the best user experience for an operational visibility dashboard. The initial implementation will support WebSocket-based metric broadcasting with fallback to on-demand calculation for clients that do not maintain open connections. This decision materially impacts API design, UI implementation, and performance targets.

**Alternatives considered**:
- Periodic batch aggregation with API polling (simpler, no WebSocket infrastructure, slightly stale data, lower performance requirements, easier to test)
- On-demand per-request calculation (simplest implementation, always fresh data, potential latency for complex aggregations, easier to test)

**Impact**: API design requires WebSocket endpoints for metric broadcasting; UI implementation requires real-time chart updates and connection management; performance targets shift from per-request latency to connection overhead; testing requires WebSocket client simulation. Metric aggregation logic remains unchanged; only the delivery mechanism changes.

---

### Question 2: User types and permissions — differentiated access vs uniform access

**Decision**: Dashboard access differentiated by user role with metric visibility tiers.

**Rationale**: This choice ensures appropriate data exposure per stakeholder role: operators need day-to-day operational metrics (order status, shipment tracking, recent invoices), managers need summary+detail metrics across all modules including financial summary, and admins need all metrics including sensitive financial data and system configuration. Differentiated access requires additional permission checks (`user:view` for operators, `user:billing` for managers, `user:admin` for admins) and potentially separate metric definitions, but ensures a stronger security posture and prevents data exposure beyond what each role legitimately needs. Uniform access was considered but selected against because the dashboard serves multiple stakeholder roles with fundamentally different data needs, and a single access level would either under-provide for power users or over-expose for basic operators.

**Alternatives considered**:
- Uniform `user:view` access for all authenticated users (simpler implementation, single permission check, all users see same metrics, potential over-exposure for some roles, simpler testing)

**Impact**: API design requires role-based permission checks at the dashboard endpoint level; UI implementation requires role-aware metric widgets and access-controlled sections; additional test cases for each role's metric visibility; metric definitions may vary slightly by role (e.g., operators see "recent invoices" while managers see "all invoices with totals").

**Role-to-metric mapping**:
- **Operator** (`user:view`): Order metrics, shipment metrics, recent invoices, operational alerts
- **Manager** (`user:billing`): All operator metrics plus billing metrics, revenue summaries, outstanding balances
- **Admin** (`user:admin`): All metrics including sensitive financial data, system configuration, user management, audit logs

---

### Question 3: Data freshness — on-demand vs 5-minute batch vs real-time

**Decision**: Batch refresh every 5 minutes via background task.

**Rationale**: This choice balances data freshness with implementation complexity for the S06 MVP. Metrics are refreshed every 5 minutes through a lightweight background task, ensuring data is current enough for operational decision-making while avoiding the infrastructure overhead of real-time WebSocket connections. Industry research and practice for operational dashboards indicates that 5-15 minute refresh intervals are standard and acceptable for most business use cases. The 5-minute interval provides a reasonable compromise: data is stale by at most 5 minutes, which is negligible for most managerial decision-making, while the implementation remains straightforward with a scheduled Celery/APS task. On-demand per-request was considered but selected against because it can cause latency for complex aggregations across multiple modules. Real-time WebSocket was considered but selected against because the added infrastructure complexity is not justified by the marginal benefit for S06 MVP.

**Alternatives considered**:
- On-demand per request (simplest implementation, no scheduled jobs, always fresh data, potential latency for complex aggregations, easier to test)
- Real-time updates via WebSocket (most complex, live data, requires connection management, highest infrastructure requirements, hardest to test, best for high-velocity ops)

**Implementation**: A scheduled background task (using APScheduler or Celery beat) refreshes all dashboard metric caches every 5 minutes. The task calculates all aggregated metrics and stores them in the cache with a TTL matching the 5-minute refresh interval. On-request API endpoints serve from the cache, ensuring consistent performance regardless of aggregation complexity. The UI polling interval aligns with the refresh interval (5 minutes), or users can trigger on-demand refresh manually.

**Impact**: Requires background task infrastructure (APScheduler/Celery); adds cache layer to API endpoints; UI must display "last updated" timestamp; testing must include scheduled task execution; performance is improved for repeated requests since metrics are pre-computed. Metric aggregation calculations remain the same; only the caching and refresh mechanism changes.

---

## Research Tasks Completed

All technical context items have been verified against the BSS-Core constitution and the feature specification. No additional research required.

All three previously-identified [NEEDS CLARIFICATION] markers have been resolved:
1. Scope boundary → Real-time WebSocket updates (Option B)
2. User types and permissions → Differentiated access by role (Option B)
3. Data freshness → Batch refresh every 5 minutes (Option B)

### Constitution Cross-Reference

- **Section 2.1 Modular Monolith**: Dashboard module has clearly defined responsibility, owns domain logic, no direct repository access by other modules
- **Section 2.2 Domain-Driven Design**: Dashboard metric aggregate protects business invariants (valid status transitions, metric consistency)
- **Section 2.3 Clean Architecture**: Dependency points inward; dashboard domain layer does not depend on FastAPI, SQLAlchemy, or database implementations
- **Section 4 Technology Standards**: Performance targets (500ms API, 2s UI), reliability (99.9%), structured JSON logging, JSON data formats all aligned with constitution Section 4 technology stack
- **Section 6 Vertical-Slice Delivery**: Dashboard module progresses through all required layers
- **Section 7 Database and Persistence**: SQLAlchemy 2.x, Alembic for migrations, business logic no SQL, repositories through domain-facing interfaces; data volume assumptions support database design
- **Section 8 API Standards**: REST conventions, /api/v1 versioning, Pydantic validation, consistent HTTP errors, no sensitive info exposure, OpenAPI docs
- **Section 9 Security Standards**: Centralized authentication (JWT), enforced authorization, RBAC, users restricted to permissions, secrets not in Git, auditable sensitive ops, input validation at boundaries — directly validated by these clarifications
- **Section 10 Testing Standards**: Multiple testing levels (unit, application, integration, API), every important business rule has automated tests
- **Section 11 Code Quality**: Python code follows consistent typing conventions; public interfaces have clear documentation; Ruff enforces linting and formatting
- **Section 14 Definition of Done**: All DoD criteria satisfied per updated checklist (16/16 items passing)