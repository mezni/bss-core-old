# Contract: Create Shipment

**Endpoint**: POST /api/v1/shipments

**Description**: Create a new shipment for a confirmed order, initiating the delivery process.

**Request**:
```json
{
  "order_id": "UUID v4 format (ORD-550e8400-e29b-41d4-a716-446655440000)",
  "carrier_name": "string (optional; required for pending status)"
}```

**Response (201 Created)**:
```json
{
  "id": "UUID v4 format (SHIP-550e8400-e29b-41d4-a716-446655440000)",
  "status": "pending",
  "tracking_reference": "SHIP-[UUID v4 substring]",
  "carrier_name": "string",
  "order_id": "UUID v4 format",
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime",
  "version": 1
}```

**Error Responses**:
- **400 Bad Request**: Order not in confirmed status, invalid order_id, missing required fields
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:manage` permission