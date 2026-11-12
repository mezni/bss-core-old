from __future__ import annotations

from datetime import UTC, datetime

from src.domain.models import Order, OrderItem


class OrderTransitionService:
    """Domain-layer service: enforce transition sequence and validate preconditions."""

    # Valid transition sequences per BSS-Core Constitution Section 2.2 (DDD)
    # and Section 7 (Database and Persistence)
    VALID_TRANSITIONS = {
        "draft": ["confirmed", "cancelled"],
        "confirmed": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": [],  # Terminal state
    }

    # Precondition rules per spec.md
    TRANSITION_RULES = {
        "confirm": {
            "requires_item": True,
            "description": "Order must have at least one item before confirmation",
        },
        "cancel": {
            "allowed_in_draft": True,
            "allowed_elsewhere": False,
            "description": "Cancellation is terminal; orders in cancelled state cannot be restored",
        },
    }

    def validate_transition(self, from_status: str, to_status: str) -> tuple[bool, str]:
        """Validate if a status transition is allowed.

        Returns (is_allowed, error_message).
        """
        allowed_targets = self.VALID_TRANSITIONS.get(from_status, [])
        if to_status not in allowed_targets:
            allowed_list = ", ".join(self.VALID_TRANSITIONS.get(from_status, []))
            return (
                False,
                f"Invalid transition from {from_status} to {to_status}. Allowed: {allowed_list}",
            )

        return True, ""

    def confirm_order(self, order: Order, db_session) -> bool:
        """Validate and execute order confirmation.

        Requires: order in draft status AND has at least one item.
        """
        # Check transition is valid
        is_allowed, error = self.validate_transition(order.status, "confirmed")
        if not is_allowed:
            return False, error

        # Check precondition: at least one item
        item_count = db_session.query(OrderItem).filter(OrderItem.order_id == order.id).count()

        if item_count < 1:
            return False, "Cannot confirm order: at least one item is required"

        # Execute transition
        order.status = "confirmed"
        order.updated_at = datetime.now(UTC)  # noqa: F821

        db_session.add(order)
        db_session.commit()

        return True, ""

    def cancel_order(self, order: Order, db_session) -> bool:
        """Validate and execute order cancellation.

        Rules:
        - Cancellation is only permitted in draft status
        - Cancellation is terminal; orders in cancelled state cannot be restored
        """
        # Check transition is valid
        is_allowed, error = self.validate_transition(order.status, "cancelled")
        if not is_allowed:
            return False, error

        # Check precondition: only draft orders can be cancelled
        if order.status != "draft":
            return (
                False,
                f"Cannot cancel order in {order.status} status. "
                "Only draft orders can be cancelled.",
            )

        # Execute transition
        order.status = "cancelled"
        order.updated_at = datetime.now(UTC)  # noqa: F821

        db_session.add(order)
        db_session.commit()

        return True, ""
