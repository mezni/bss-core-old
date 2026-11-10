"""FastAPI application health check endpoint.

Provides a simple health check endpoint for the backend service,
used by developers and infrastructure to verify service status.
"""

from fastapi import FastAPI

from src.models.customer_management.api.router import router as customer_router
from src.models.order_management.api.router import router as order_router


app = FastAPI(title="BSS Core Backend", version="0.1.0")


@app.get("/health", summary="Health check endpoint", tags=["health"])
def health_check():
    """Health check endpoint that verifies the service is operational.

    Returns:
        dict: Status object indicating the service is operational.
    """
    return {"status": "ok", "service": "bss-core-backend"}


@app.get("/health/detailed", summary="Detailed health check", tags=["health"])
def health_check_detailed():
    """Detailed health check endpoint with additional metadata.

    Returns:
        dict: Detailed status object with service metadata.
    """
    return {
        "status": "ok",
        "service": "bss-core-backend",
        "version": "0.1.0",
        "environment": "development",
    }


def register_error_handlers(app: FastAPI) -> None:
    """Add consistent error handling middleware per BSS-Core Constitution Section 8."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle validation errors with clear messages."""
        from fastapi.responses import JSONResponse
        from starlette import status

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors with consistent format."""
        from fastapi.responses import JSONResponse
        from starlette import status

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "path": request.url.path,
            },
        )


app.include_router(customer_router)
app.include_router(order_router)