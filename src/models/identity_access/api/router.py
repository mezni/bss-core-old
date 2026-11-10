"""Status router for the identity_access module."""

from fastapi import APIRouter

MODULE_NAME = "identity_access"

router = APIRouter(prefix="/identity-access", tags=[MODULE_NAME])


@router.get("/status")
def status():
    """Module status endpoint."""
    return {"status": "ok", "module": MODULE_NAME}


@router.get("/health")
def health():
    """Module health endpoint."""
    return {"status": "healthy", "module": MODULE_NAME}
