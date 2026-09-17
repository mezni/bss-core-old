from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import require_role
from app.database import get_db
from app.seed import run_seed

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/generate-fake-data", response_model=schemas.MessageResponse, status_code=201)
def generate_fake_data(
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Drop all tables and reseed the database with the target dataset."""
    db.close()
    run_seed()
    return schemas.MessageResponse(message="Database reseeded with fake data")


@router.get("/health", response_model=dict)
def admin_health(
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
):
    from sqlalchemy import func, text

    counters = {
        "users": db.query(func.count(models.UserModel.id)).scalar(),
        "subscribers": db.query(func.count(models.SubscriberModel.id)).scalar(),
        "lines": db.query(func.count(models.TelecomLineModel.id)).scalar(),
        "devices": db.query(func.count(models.DeviceModel.id)).scalar(),
        "invoices": db.query(func.count(models.InvoiceModel.id)).scalar(),
        "payments": db.query(func.count(models.PaymentModel.id)).scalar(),
        "usage_records": db.query(func.count(models.UsageRecordModel.id)).scalar(),
    }
    db.execute(text("SELECT 1"))
    return {"status": "ok", "counts": counters}