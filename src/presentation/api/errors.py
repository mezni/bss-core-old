from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


def add_error_handling(app: FastAPI) -> None:
    """Add consistent error handling middleware per BSS-Core Constitution Section 8."""

    @app.exception_handler(HttpError)
    async def http_error_handler(request: Request, exc: HttpError) -> JSONResponse:
        """Handle HTTP errors with consistent format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle validation errors with clear messages."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
                "path": request.url.path,
            },
        )


class HttpError(Exception):
    """Base class for HTTP errors per API Standards (Section 8 of constitution)."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
