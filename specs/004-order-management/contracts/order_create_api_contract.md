# Contract: Create Order

**Endpoint**: POST /api/v1/orders

**Description**: Create a new order in draft status for an eligible customer.

**Request**:
```json
{
  "customer_id": "string (customer identifier from S02)",
  "items": [
    {
      "description": "string",
      "quantity": "integer (>0)",
      "unit_price": "decimal (>0)"
    }
  ]
}```

**Response (201 Created)**:
```json
{
  "id": "UUID v4 format (ORD-550e8400-e29b-41d4-a716-446655440000)",
  "status": "draft",
  "subtotal": "decimal",
  "tax_amount": "decimal",
  "total": "decimal",
  "customer_id": "string",
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime",
  "version": 1
}```

**Error Responses**:
- **400 Bad Request**: Missing required fields, invalid item quantities/prices, customer not eligible, no items provided
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:manage` permission
