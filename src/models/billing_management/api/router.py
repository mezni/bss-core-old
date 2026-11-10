"""Status router for the billing_management module."""

from fastapi import APIRouter

MODULE_NAME = "billing_management"

router = APIRouter(prefix="/billing-management", tags=[MODULE_NAME])


@router.get("/status")
def status():
    """Module status endpoint."""
    return {"status": "ok", "module": MODULE_NAME}


@router.get("/health")
def health():
    """Module health endpoint."""
    return {"status": "healthy", "module": MODULE_NAME}
