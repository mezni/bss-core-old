"""Structured JSON logging for BSS-Core.

Constitution Section 11: logging MUST be structured and MUST NOT expose
secrets. This module extends basic logging setup with:

- ``workflow.started`` / ``workflow.completed`` / ``workflow.failed`` events
  for cross-module workflow actions (FR-008, SC-006)
- authorization denial events with the required permission (FR-005)
- a correlation-id request middleware so events can be tied to a request
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

WORKFLOW_LOGGER_NAME = "bss.workflow"

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def setup_logging(
    level: int = logging.INFO,
    log_file: str | None = None,
) -> logging.Logger:
    """Set up structured logging per BSS-Core Constitution Section 11."""

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # File handler if log_file specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        handlers.append(file_handler)

    # Formatter per constitution
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    return root_logger


def get_correlation_id() -> str:
    """Return the correlation id for the current request context, if any."""
    return correlation_id_var.get()


def _emit(payload: dict[str, object]) -> None:
    """Emit a structured JSON event on the workflow logger."""
    payload.setdefault("timestamp", datetime.now(UTC).isoformat())
    payload.setdefault("correlation_id", get_correlation_id() or None)
    logging.getLogger(WORKFLOW_LOGGER_NAME).info(json.dumps(payload, default=str))


def log_workflow_started(
    workflow: str,
    *,
    step: str | None = None,
    modules: list[str] | None = None,
) -> None:
    """Emit a ``workflow.started`` event (FR-008)."""
    _emit(
        {
            "event": "workflow.started",
            "workflow": workflow,
            "step": step,
            "modules": modules or [],
        }
    )


def log_workflow_completed(
    workflow: str,
    *,
    step: str | None = None,
    modules: list[str] | None = None,
    outcome: str = "success",
) -> None:
    """Emit a ``workflow.completed`` event (FR-008)."""
    _emit(
        {
            "event": "workflow.completed",
            "workflow": workflow,
            "step": step,
            "modules": modules or [],
            "outcome": outcome,
        }
    )


def log_workflow_failed(
    workflow: str,
    *,
    step: str | None = None,
    error: str,
    modules: list[str] | None = None,
) -> None:
    """Emit a ``workflow.failed`` event (FR-008). No stack traces or secrets."""
    _emit(
        {
            "event": "workflow.failed",
            "workflow": workflow,
            "step": step,
            "modules": modules or [],
            "error": error,
        }
    )


def log_authorization_denial(
    *,
    workflow: str | None,
    required_permission: str,
    result: str = "denied",
) -> None:
    """Emit a structured authorization denial event (FR-005).

    Never logs token material — only the workflow, required permission,
    result, and timestamp.
    """
    _emit(
        {
            "event": "authorization.denied",
            "workflow": workflow,
            "required_permission": required_permission,
            "result": result,
        }
    )


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagate or generate a correlation id for every request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        token = correlation_id_var.set(correlation_id)
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(token)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
