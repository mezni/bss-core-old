"""Application factory and ASGI entry point.

Exposes ``create_app()`` for testing and ``app`` at module level for ``uvicorn
ecommerce.main:app`` to resolve. All application wiring lives here: the reserved router,
both error handlers, and the conditional registration of the API descriptions.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from ecommerce.api.errors import register_error_handlers
from ecommerce.api.health import HealthStatus
from ecommerce.api.router import build_versioned_router
from ecommerce.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Return a configured ASGI application.

    If ``settings`` is ``None``, the settings object is built from the environment. This
    is the entry point for ``uvicorn`` and for integration tests that require a fully
    configured application. The application factory builds the configured object once
    at startup.
    """
    if settings is None:
        settings = get_settings()
        logger.info(
            "application starting in %s mode (version %s) at %s:%s",
            settings.app_env,
            settings.app_version,
            settings.host,
            settings.port,
        )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Phase 1 foundation. Liveness only; no business endpoints yet.",
        docs_url="/docs" if settings.api_docs_enabled else None,
        redoc_url="/redoc" if settings.api_redoc_enabled else None,
        openapi_url="/openapi.json" if settings.api_docs_enabled else None,
    )

    register_error_handlers(app)

    # The liveness check is unversioned and sits outside the reserved router.
    # It has its own file in api/health.py (see T027).
    # The reserved router itself is built below and mounted with no routes:
    # a later feature will add routes to it.
    app.include_router(build_versioned_router(settings))

    # Unversioned liveness check — sits outside the reserved namespace.
    # Returns exactly {"status": "ok"} (FR-002, FR-003).
    # The two description switches (API_DOCS_ENABLED, API_REDOC_ENABLED) are
    # independently controllable convenience controls; they are NOT a security
    # boundary. Turning one off does not make the other's schema retrievable
    # at an alternate path (FR-004, research D-05).
    @app.get("/health", include_in_schema=False)
    async def health() -> HealthStatus:
        return HealthStatus(status="ok")

    return app


app = create_app()
