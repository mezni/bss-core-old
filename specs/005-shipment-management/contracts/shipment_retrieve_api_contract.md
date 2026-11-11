# Contract: Retrieve Shipment

**Endpoint**: GET /api/v1/shipments/{{shipment_id}}

**Description**: Retrieve a single shipment by its unique identifier.

**URL Parameters**:
- `shipment_id`: UUID v4 format (SHIP-550e8400-e29b-41d4-a716-446655440000)

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "status": "pending|in-transit|delivered|exception",
  "tracking_reference": "SHIP-[UUID v4 substring]",
  "carrier_name": "string",
  "order_id": "UUID v4 format",
  "customer_id": "string",
  "customer_type": "INDIVIDUAL|BUSINESS",
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime",
  "delivered_at": "ISO-8601 datetime (nullable)",
  "version": integer
}```

**Error Responses**:
- **404 NOT FOUND**: Shipment with given ID does not exist
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:view` permission (for read) or `customer:manage` (for certain views)