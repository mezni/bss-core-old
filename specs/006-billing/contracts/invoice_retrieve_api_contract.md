# Contract: Retrieve Invoice

**Endpoint**: GET /api/v1/invoices/{{invoice_id}}

**Description**: Retrieve a single invoice by its unique identifier.

**URL Parameters**:
- `invoice_id`: UUID v4 format (INV-550e8400-e29b-41d4-a716-446655440000)

**Response (200 OK)**:
```json
{
  "id": "UUID v4 format",
  "invoice_number": "string",
  "status": "pending|paid",
  "total_amount": decimal,
  "reference_id": "UUID v4 format",
  "billing_date": "ISO-8601 datetime",
  "due_date": "ISO-8601 datetime",
  "payment_date": "ISO-8601 datetime (nullable)",
  "payment_method": "string (nullable)",
  "customer_id": "string"
}```

**Error Responses**:
- **404 NOT FOUND**: Invoice with given ID does not exist
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `user:view` permission (for read) or `user:billing` (for certain views)