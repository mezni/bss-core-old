"""FastAPI application health check endpoint.

Provides a simple health check endpoint for the backend service,
used by developers and infrastructure to verify service status.
"""

from fastapi import FastAPI

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
