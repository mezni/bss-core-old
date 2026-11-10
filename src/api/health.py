"""FastAPI application health check endpoint.

Provides a simple health check endpoint for the backend service,
used by developers and infrastructure to verify service status.
"""

from fastapi import FastAPI
from sqlalchemy.orm import Session

from src.models.customer_management.api.errors import register_error_handlers
from src.models.customer_management.api.router import router as customer_router
from src.models.customer_management.application.service import CustomerEligibilityAdapter
from src.models.customer_management.infrastructure.repository import (
    SQLAlchemyCustomerRepository,
)

app = FastAPI(title="BSS Core Backend", version="0.1.0")
register_error_handlers(app)
app.include_router(customer_router)


def build_customer_eligibility_port(session: Session) -> CustomerEligibilityAdapter:
    """Composition-root factory for downstream modules.

    Callers supply their request-scoped session and receive the application port,
    never the repository or ORM.
    """
    return CustomerEligibilityAdapter(SQLAlchemyCustomerRepository(session))


app.state.customer_eligibility_port_factory = build_customer_eligibility_port


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
