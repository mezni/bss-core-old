"""Status router for the order_management module."""

from fastapi import APIRouter

MODULE_NAME = "order_management"

router = APIRouter(prefix="/order-management", tags=[MODULE_NAME])


@router.get("/status")
def status():
    """Module status endpoint."""
    return {"status": "ok", "module": MODULE_NAME}


@router.get("/health")
def health():
    """Module health endpoint."""
    return {"status": "healthy", "module": MODULE_NAME}
