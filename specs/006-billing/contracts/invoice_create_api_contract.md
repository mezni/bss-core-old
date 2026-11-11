# Contract: Create Invoice

**Endpoint**: POST /api/v1/invoices

**Description**: Create a new invoice for a completed order or shipment, initiating the billing cycle.

**Request**:
```json
{
  "reference_id": "UUID v4 format (ORD-550e8400-e29b-41d4-a716-446655440000)",
  "due_days": integer (optional, default: 30)
}```

**Response (201 Created)**:
```json
{
  "id": "UUID v4 format (INV-550e8400-e29b-41d4-a716-446655440000)",
  "invoice_number": "INV-20261110-0001",
  "status": "pending",
  "total_amount": decimal,
  "reference_id": "UUID v4 format",
  "billing_date": "ISO-8601 datetime",
  "due_date": "ISO-8601 datetime",
  "version": 1
}```

**Error Responses**:
- **400 Bad Request**: Reference not in billable status, missing required fields
- **401 UNAUTHENTICATED**: Missing or invalid bearer token
- **403 FORBIDDEN**: Token lacks `user:billing` permission