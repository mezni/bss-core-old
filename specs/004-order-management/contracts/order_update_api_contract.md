# Contract: Update Order (status and partial modifications)

**Endpoint**: PATCH /api/v1/orders/{{order_id}}

**Description**: Update an order's status or modify fields. Domain-layer enforcement of transition preconditions.

**URL Parameters**:
- `order_id`: UUID v4 format (ORD-550e8400-e29b-41d4-a716-446655440000)

**Request**:
```json
{
  "version": integer,  // must match current order version
  "status": "draft|confirmed|shipped|delivered|cancelled"  // optional; must follow valid transition rules
}```

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "status": "updated status",
  "version": new_version,
  "subtotal": "decimal",
  "total": "decimal",
  "updated_at": "ISO-8601 datetime"
}```

**Error Responses**:
- **400 Bad Request**: Invalid version, invalid status value, missing required fields
- **409 Conflict (STALE_UPDATE)**: Provided version does not match current order version; return `current_version` in response
- **409 Conflict (INVALID_TRANSITION)**: Status transition not permitted (e.g., cancelled order cannot be confirmed; draft→shipped without confirming); return detailed error
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:manage` permission
