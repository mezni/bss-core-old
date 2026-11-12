"""Shared error envelope for the customer management API.

Migrated to the standardized flat envelope per
``specs/008-integration-mvp/contracts/error_response_contract.md``:

    {"error": "<type-slug>", "message": "<human-readable>", "code": "<CODE>"}

Handler registration itself is owned by the composition root
(``src/api/health.py``); this module only builds payloads for backwards
compatibility with module-level consumers.
"""

from __future__ import annotations

from typing import Any


def error_payload(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build the standardized flat error envelope.

    ``details`` is accepted for backwards compatibility but folded into the
    human-readable message — the standard envelope has no separate details
    field.
    """
    if details:
        suffix = "; ".join(f"{key}={value}" for key, value in details.items())
        message = f"{message} ({suffix})"
    return {
        "error": code.lower(),
        "message": message,
        "code": code,
    }
