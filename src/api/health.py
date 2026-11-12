"""Composition root for the consolidated BSS-Core FastAPI application.

This module wires every module router into a single application and owns
the standardized error-response envelope per
``specs/008-integration-mvp/contracts/error_response_contract.md``:

    {"error": "<type-slug>", "message": "<human-readable>", "code": "<CODE>"}

Status-to-code mapping: 400 VALIDATION_ERROR, 401 UNAUTHENTICATED,
403 FORBIDDEN, 404 NOT_FOUND, 409 CONFLICT, 422 UNPROCESSABLE_ENTITY,
500 INTERNAL_ERROR.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.infrastructure.logging import CorrelationIdMiddleware
from src.models.billing_management.api.invoices import router as invoice_router
from src.models.billing_management.api.payments import router as payment_router
from src.models.billing_management.domain.exceptions import BillingDomainError
from src.models.customer_management.api.router import router as customer_router
from src.models.customer_management.domain.exceptions import CustomerDomainError
from src.models.order_management.api.router import router as order_router
from src.models.order_management.domain.exceptions import OrderDomainError
from src.models.shipment_management.api.shipments import router as shipment_router
from src.models.shipment_management.domain.exceptions import ShipmentDomainError
from src.presentation.api.dashboard_endpoints import router as dashboard_router

logger = logging.getLogger(__name__)

STATUS_ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    500: "INTERNAL_ERROR",
}


def error_payload(error: str, message: str, code: str) -> dict[str, str]:
    """Build the standardized error envelope."""
    return {"error": error, "message": message, "code": code}


def standard_error_response(
    status_code: int, message: str, code: str | None = None
) -> JSONResponse:
    """Build a standardized error response for an HTTP status."""
    resolved_code = code or STATUS_ERROR_CODES.get(status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=status_code,
        content=error_payload(
            error=resolved_code.lower(),
            message=message,
            code=resolved_code,
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register the centralized standardized error handlers (constitution Section 8)."""

    @app.exception_handler(CustomerDomainError)
    @app.exception_handler(OrderDomainError)
    @app.exception_handler(ShipmentDomainError)
    @app.exception_handler(BillingDomainError)
    async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Map module domain errors to their stable code and HTTP status."""
        message = exc.message
        details = getattr(exc, "details", None)
        if details:
            suffix = "; ".join(f"{key}={value}" for key, value in details.items())
            message = f"{message} ({suffix})"
        return JSONResponse(
            status_code=exc.http_status,
            content=error_payload(
                error=exc.code.lower(),
                message=message,
                code=exc.code,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """No bare HTTPException bodies — everything uses the envelope."""
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        response = standard_error_response(exc.status_code, message)
        if exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
        return response

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Pydantic request validation failures -> 400 VALIDATION_ERROR."""
        summary = "; ".join(
            "{}: {}".format(
                ".".join(str(part) for part in error.get("loc", [])),
                error.get("msg", "invalid value"),
            )
            for error in exc.errors()
        )
        return standard_error_response(
            status.HTTP_400_BAD_REQUEST,
            f"Request validation failed: {summary}" if summary else "Request validation failed",
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Malformed input raised as ValueError -> 400 VALIDATION_ERROR."""
        return standard_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc) or "Invalid request payload"
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Unhandled errors -> 500 INTERNAL_ERROR without internals or secrets."""
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return standard_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "An internal error occurred"
        )


app = FastAPI(title="BSS Core Backend", version="0.1.0")
app.add_middleware(CorrelationIdMiddleware)

register_error_handlers(app)


@app.get("/health", summary="Health check endpoint", tags=["health"])
def health_check():
    """Health check endpoint that verifies the service is operational."""
    return {"status": "ok", "service": "bss-core-backend"}


@app.get("/health/detailed", summary="Detailed health check", tags=["health"])
def health_check_detailed():
    """Detailed health check endpoint with additional metadata."""
    return {
        "status": "ok",
        "service": "bss-core-backend",
        "version": "0.1.0",
        "environment": "development",
    }


app.include_router(customer_router)
app.include_router(order_router)
app.include_router(dashboard_router)
app.include_router(shipment_router)
app.include_router(invoice_router)
app.include_router(payment_router)
