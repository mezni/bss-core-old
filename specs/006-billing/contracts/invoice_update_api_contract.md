# Contract: Update Invoice

**Endpoint**: PATCH /api/v1/invoices/{{invoice_id}}

**Description**: Update an invoice's payment status. Domain-layer enforcement of transition preconditions.

**URL Parameters**:
- `invoice_id`: UUID v4 format (INV-550e8400-e29b-41d4-a716-446655440000)

**Request**:
```json
{
  "version": integer,  // must match current invoice version
  "status": "pending|paid optional; must follow valid transition rules"
}```

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "status": "updated status",
  "version": new_version,
  "payment_date": "ISO-8601 datetime (nullable)",
  "updated_at": "ISO-8601 datetime"
}```

**Error Responses**:
- **400 Bad Request**: Invalid version, invalid status value, missing required fields
- **409 Conflict (STALE_UPDATE)**: Provided version does not match current invoice version; return `current_version` in response
- **409 Conflict (INVALID_TRANSITION)**: Status transition not permitted (e.g., paid invoice cannot be set to pending); return detailed error
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `user:billing` permission