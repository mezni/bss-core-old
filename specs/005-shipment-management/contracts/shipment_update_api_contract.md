# Contract: Update Shipment

**Endpoint**: PATCH /api/v1/shipments/{{shipment_id}}

**Description**: Update an shipment's carrier, tracking number, or status. Domain-layer enforcement of transition preconditions.

**URL Parameters**:
- `shipment_id`: UUID v4 format (SHIP-550e8400-e29b-41d4-a716-446655440000)

**Request**:
```json
{
  "version": integer,  // must match current shipment version
  "status": "pending|in-transit|delivered" optional; must follow valid transition rules
}```

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "status": "updated status",
  "version": new_version,
  "updated_at": "ISO-8601 datetime"
}```

**Error Responses**:
- **400 Bad Request**: Invalid version, invalid status value, missing required fields
- **409 Conflict (STALE_UPDATE)**: Provided version does not match current shipment version; return `current_version` in response
- **409 Conflict (INVALID_TRANSITION)**: Status transition not permitted (e.g., delivered order cannot be set to in-transit; pending→delivered without confirming); return detailed error
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:manage` permission