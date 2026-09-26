"""Health status — the body of GET /health.

The liveness check returns exactly ``{"status": "ok"}`` with no version, timestamp,
uptime, or dependency status (FR-002, FR-003).
"""

from __future__ import annotations

from pydantic import BaseModel

StatusLiteral = str


class HealthStatus(BaseModel):
    """The payload returned by the liveness check.

    Constraints:
    - ``status`` MUST be the literal string ``"ok"``.
    - No other fields are permitted (additionalProperties: false).
    - This schema is the only place the literal ``"ok"`` is assigned.
    """

    status: StatusLiteral = "ok"
