# Contract: Retrieve Order

**Endpoint**: GET /api/v1/orders/{{order_id}}

**Description**: Retrieve a single order by its unique identifier.

**URL Parameters**:
- `order_id`: UUID v4 format (ORD-550e8400-e29b-41d4-a716-446655440000)

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "status": "draft|confirmed|shipped|delivered|cancelled",
  "subtotal": "decimal",
  "tax_amount": "decimal",
  "total": "decimal",
  "items": [
    {
      "description": "string",
      "quantity": integer,
      "unit_price": "decimal",
      "line_total": "decimal (quantity × unit_price)"
    }
  ],
  "customer_id": "string",
  "customer_type": "INDIVIDUAL|BUSINESS",
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime",
  "version": integer
}```

**Error Responses**:
- **404 NOT FOUND**: Order with given ID does not exist
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `customer:view` permission (for read) or `customer:manage` (for certain views)
