"""Structured lifecycle logging that deliberately excludes customer PII."""

from __future__ import annotations

import logging

logger = logging.getLogger("bss.customer_management")


def log_lifecycle(
    action: str,
    customer_id: str,
    *,
    status: str,
    version: int,
) -> None:
    """Emit a structured lifecycle event without names, emails, or addresses."""
    logger.info(
        "customer.lifecycle",
        extra={
            "customer_id": customer_id,
            "action": action,
            "status": status,
            "version": version,
        },
    )
