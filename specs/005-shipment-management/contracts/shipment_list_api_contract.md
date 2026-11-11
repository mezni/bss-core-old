# Contract: List Shipments

**Endpoint**: GET /api/v1/shipments

**Description**: List shipments with optional filtering by order, status, and pagination. Follows S02 pattern for consistency.

**Query Parameters**:
- `q`: string (optional) — search term; matches against shipment ID, tracking reference, carrier, and status
- `status`: string (optional) — filter by shipment status: `pending`, `in-transit`, `delivered`, `exception`
- `order_id`: UUID v4 (optional) — filter by order reference
- `page`: integer (optional, default: 1) — page number; minimum 1
- `page_size`: integer (optional, default: 20; max: 100) — items per page

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "UUID v4 format",
      "status": "pending|in-transit|delivered|exception",
      "tracking_reference": "SHIP-[UUID v4 substring]",
      "carrier_name": "string",
      "order_id": "UUID v4 format",
      "customer_type": "INDIVIDUAL|BUSINESS",
      "version": integer
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": integer
}```

**Error Responses**:
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:view` permission