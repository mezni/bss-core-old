"""Status router for the shipment_management module."""

from fastapi import APIRouter

MODULE_NAME = "shipment_management"

router = APIRouter(prefix="/shipment-management", tags=[MODULE_NAME])


@router.get("/status")
def status():
    """Module status endpoint."""
    return {"status": "ok", "module": MODULE_NAME}


@router.get("/health")
def health():
    """Module health endpoint."""
    return {"status": "healthy", "module": MODULE_NAME}
