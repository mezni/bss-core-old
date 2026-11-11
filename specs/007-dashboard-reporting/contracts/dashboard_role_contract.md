# Contract: Dashboard Role-Based Access Control

**Description**: Role-tiered access control for dashboard API and UI endpoints. Ensures appropriate data exposure per stakeholder role.

**Authentication**: JWT token with role claims. Permission checks evaluated at dashboard endpoint level.

**Role Tiers and Permissions**:

| Role Tier | Permission String | Access Level | Metric Visibility |
|-----------|------------------|--------------|-------------------|
| **Operator** | `user:view` | Read-only | Order metrics, shipment metrics, recent invoices, operational alerts |
| **Manager** | `user:billing` | Read + financial | All operator metrics plus billing metrics, revenue summaries, outstanding balances |
| **Admin** | `user:admin` | Full access | All metrics including sensitive financial data, system configuration, user management, audit logs |

**Permission Evaluation**:
- Permission checked at dashboard API `/api/v1/dashboard/metrics` endpoint
- Permission checked at dashboard UI `/dashboard` route
- If no role tier specified in request, default to operator-level visibility
- If role tier does not match required tier for requested metric, return 403 Forbidden
- Role tier can be specified via JWT `role_tier` claim or inferred from user's assigned role

**Role Hierarchy**:
- `user:admin` encompasses all permissions (`*`)
- `user:billing` includes operator metrics + billing metrics
- `user:view` includes operator-level metrics only
- Down-tier access cannot be upgraded without re-authentication with higher role

**Error Responses**:
- **403 FORBIDDEN**: User's role tier does not permit access to requested metric category or value
  - Example: Operator requesting billing-level revenue metrics → 403
  - Example: Manager requesting admin-level system configuration → 403