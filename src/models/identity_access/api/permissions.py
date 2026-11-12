"""Shared permission constants for cross-module authorization.

Per ``specs/008-integration-mvp/contracts/authorization_contract.md``:
- ``user:view`` grants the customer-to-order workflow
- ``user:billing`` grants the order-to-invoice and invoice-to-payment workflows
- ``user:admin`` grants all four workflows (full access)

Under this mapping, order-to-shipment is effectively ``user:admin``-only.
"""

from __future__ import annotations

USER_VIEW = "user:view"
USER_BILLING = "user:billing"
USER_ADMIN = "user:admin"

ALL_USER_PERMISSIONS = (USER_VIEW, USER_BILLING, USER_ADMIN)

WORKFLOW_CUSTOMER_TO_ORDER = "customer_to_order"
WORKFLOW_ORDER_TO_SHIPMENT = "order_to_shipment"
WORKFLOW_ORDER_TO_INVOICE = "order_to_invoice"
WORKFLOW_INVOICE_TO_PAYMENT = "invoice_to_payment"

# Workflow name -> the minimum dedicated permission that grants it
# (``user:admin`` additionally grants every workflow).
WORKFLOW_PERMISSIONS: dict[str, str] = {
    WORKFLOW_CUSTOMER_TO_ORDER: USER_VIEW,
    WORKFLOW_ORDER_TO_SHIPMENT: USER_ADMIN,
    WORKFLOW_ORDER_TO_INVOICE: USER_BILLING,
    WORKFLOW_INVOICE_TO_PAYMENT: USER_BILLING,
}
