# Contract: List Invoices

**Endpoint**: GET /api/v1/invoices

**Description**: List invoices with optional filtering by customer, status, and pagination.

**Query Parameters**:
- `customer_id`: string (optional) — filter by customer identifier
- `status`: string (optional) — filter by invoice status: `pending`, `paid`
- `page`: integer (optional, default: 1) — page number; minimum 1
- `page_size`: integer (optional, default: 20; max: 100) — items per page

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "UUID v4 format",
      "invoice_number": "string",
      "status": "pending|paid",
      "total_amount": decimal,
      "reference_id": "UUID v4 format",
      "billing_date": "ISO-8601 datetime",
      "due_date": "ISO-8601 datetime",
      "payment_date": "ISO-8601 datetime (nullable)",
      "payment_method": "string (nullable)"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": integer
}```

**Error Responses**:
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `user:view` permission