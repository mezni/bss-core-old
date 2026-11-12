# Contract: Cross-Module Authorization

**Applies to**: All workflow entry points of the S07 integration feature, enforced by the backend.

**Description**: Defines the shared permission model, JWT claim format, and the role-to-workflow mapping clarified in the spec session. Authentication is centralized in the identity module's API dependencies (constitution Section 9); all module endpoints enforce their own permissions per their specs.

**Permission constants**:

| Permission | Constant | Granted Access |
|---|---|---|
| `user:view` | `USER_VIEW` | Customer-to-order workflow only |
| `user:billing` | `USER_BILLING` | Order-to-invoice and invoice-to-payment workflows |
| `user:admin` | `USER_ADMIN` | All four workflows (full access) |

**Note**: Under the clarified mapping, order-to-shipment is effectively `user:admin`-only. This is encoded as clarified; extending operator access to shipments is a documented follow-up, not a silent change.

**JWT claim format**:

```json
{
  "sub": "<subject-id>",
  "permissions": ["user:view", "user:billing"]
}
```

- Token: JWT HS256, signed with `BSS_JWT_SECRET` (environment-provided; dev fallback documented, never committed)
- Transport: `Authorization: Bearer <token>` header on every request
- Missing/invalid/expired token → `401 UNAUTHENTICATED` (standardized envelope)
- Valid token lacking required permission → `403 FORBIDDEN` (standardized envelope)

**Workflow-to-permission enforcement matrix**:

| Workflow | `user:view` | `user:billing` | `user:admin` |
|---|---|---|---|
| Customer-to-order | granted | denied | granted |
| Order-to-shipment | denied | denied | granted |
| Order-to-invoice | denied | granted | granted |
| Invoice-to-payment | denied | granted | granted |

**Enforcement behavior**:

1. Permission check runs before any business logic executes on the workflow entry point
2. Denials create no records and leave prior state untouched
3. Every denial emits a structured log event: workflow name, required permission, result, timestamp (no token material logged)
4. Module-level endpoint permissions (e.g., `customer:view`, `customer:manage`) remain per their module specs and compose with workflow permissions at the API layer

**Verification**: `tests/contract/integration/test_workflow_authorization_contract.py` asserts the full matrix — positive and negative cases per workflow and permission — plus 401 for missing/invalid tokens (SC: no critical authorization defects; security review sign-off gate).
