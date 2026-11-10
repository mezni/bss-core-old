# Contract: List Orders

**Endpoint**: GET /api/v1/orders

**Description**: List orders with optional search, filtering, and pagination. Follows S02 pattern for consistency.

**Query Parameters**:
- `q`: string (optional) — search term; matches against order ID, customer reference, and status
- `status`: string (optional) — filter by order status: `draft`, `confirmed`, `shipped`, `delivered`, `cancelled`
- `page`: integer (optional, default: 1) — page number; minimum 1
- `page_size`: integer (optional, default: 20; max: 100) — items per page

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "UUID v4 format",
      "status": "draft|confirmed|shipped|delivered|cancelled",
      "subtotal": "decimal",
      "total": "decimal",
      "customer_id": "string",
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
