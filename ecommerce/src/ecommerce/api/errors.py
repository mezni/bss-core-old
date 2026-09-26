"""The single error structure every failure returns, and the handlers that produce it.

Both handlers build the body through :func:`_envelope`, so the four fields and the
always-array ``details`` rule hold by construction rather than by convention (FR-008).
The catch-all handler logs the traceback server-side and returns a fixed message, so no
exception type, message, stack frame, or file system path reaches a client (FR-009).

See contracts/error-envelope.md.
"""

from __future__ import annotations

import logging
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ecommerce.observability.request_id import REQUEST_ID_KEY, resolve_request_id

logger = logging.getLogger(__name__)

#: Published error codes this feature can emit. See docs/API.md section 12.1 for the full
#: list; the remainder arrive with their own features and are deliberately not invented
#: here, because a code with no feature behind it is an undocumented promise.
CODE_NOT_FOUND = "NOT_FOUND"
CODE_VALIDATION_ERROR = "VALIDATION_ERROR"
CODE_INTERNAL_ERROR = "INTERNAL_ERROR"

#: Status code to published code. Only the codes this feature can raise are mapped.
_STATUS_TO_CODE: dict[int, str] = {
    HTTPStatus.NOT_FOUND: CODE_NOT_FOUND,
    HTTPStatus.UNPROCESSABLE_ENTITY: CODE_VALIDATION_ERROR,
}

#: Fixed message for an unanticipated fault. The real cause goes to the log, never here.
INTERNAL_ERROR_MESSAGE = "Internal server error"

NOT_FOUND_MESSAGE = "Resource not found"
VALIDATION_ERROR_MESSAGE = "Request validation failed"


class ErrorDetail(BaseModel):
    """One field-level issue. Empty on every response this feature can currently produce."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorBody(BaseModel):
    """The inner object of the envelope."""

    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: str


class ErrorEnvelope(BaseModel):
    """The complete error body: a single top-level ``error`` key."""

    error: ErrorBody


def _envelope(
    *,
    code: str,
    message: str,
    request: Request,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    """Build the error response. The only place the envelope shape is constructed."""
    request_id = getattr(request.state, REQUEST_ID_KEY, None) or resolve_request_id()
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or [],
            request_id=request_id,
        )
    )
    status = HTTPStatus.INTERNAL_SERVER_ERROR if code == CODE_INTERNAL_ERROR else _status_for(code)
    return JSONResponse(status_code=int(status), content=envelope.model_dump())


def _status_for(code: str) -> int:
    for status, mapped in _STATUS_TO_CODE.items():
        if mapped == code:
            return int(status)
    return int(HTTPStatus.INTERNAL_SERVER_ERROR)


def _code_for_status(status_code: int) -> str:
    """Map a status to its published code, defaulting to a generic client error."""
    return _STATUS_TO_CODE.get(status_code, CODE_INTERNAL_ERROR)


def register_error_handlers(app: FastAPI) -> None:
    """Attach both handlers to the application."""

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Map framework-raised HTTP errors, including routing 404s, onto the envelope."""
        code = _code_for_status(exc.status_code)
        if exc.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            # A framework 5xx is still an unanticipated fault: log it, answer generically.
            logger.error("http_exception status=%s detail=%s", exc.status_code, exc.detail, exc_info=exc)
            return _envelope(code=CODE_INTERNAL_ERROR, message=INTERNAL_ERROR_MESSAGE, request=request)
        message = exc.detail if isinstance(exc.detail, str) and exc.detail else NOT_FOUND_MESSAGE
        return _envelope(code=code, message=message, request=request)

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Report field-level issues, always as an array."""
        details = [
            ErrorDetail(
                field=".".join(str(part) for part in err.get("loc", ())) or None,
                message=str(err.get("msg", "invalid value")),
                code=str(err.get("type")) if err.get("type") else None,
            )
            for err in exc.errors()
        ]
        return _envelope(
            code=CODE_VALIDATION_ERROR,
            message=VALIDATION_ERROR_MESSAGE,
            request=request,
            details=details,
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all: log the cause, return a fixed message (FR-009)."""
        logger.exception("unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
        return _envelope(code=CODE_INTERNAL_ERROR, message=INTERNAL_ERROR_MESSAGE, request=request)
