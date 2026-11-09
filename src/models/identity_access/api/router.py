from fastapi import APIRouter

router = APIRouter(prefix=f"/{module.lower()}", tags=[{module}])


@router.get("/status")
def status():
    """Module status endpoint."""
    return {"status": "ok", "module": "{module}"}


@router.get("/health")
def health():
    """Module health endpoint."""
    return {"status": "healthy", "module": "{module}"}
