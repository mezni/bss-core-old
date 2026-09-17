from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, require_role
from app.database import get_db

router = APIRouter(prefix="/usage", tags=["usage"])

WRITE_AUTH = require_role(models.UserRole.CSR)


@router.get("", response_model=list[schemas.UsageRead])
def list_usage_records(
    msisdn: Optional[str] = None,
    usage_type: Optional[models.UsageType] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.UsageRecordModel)
    if msisdn:
        query = query.filter(models.UsageRecordModel.msisdn == msisdn)
    if usage_type:
        query = query.filter(models.UsageRecordModel.type == usage_type)
    if start:
        query = query.filter(models.UsageRecordModel.timestamp >= start)
    if end:
        query = query.filter(models.UsageRecordModel.timestamp <= end)
    return (
        query.order_by(models.UsageRecordModel.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=schemas.UsageRead, status_code=201)
def record_usage(
    payload: schemas.UsageCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    line = (
        db.query(models.TelecomLineModel)
        .filter(models.TelecomLineModel.msisdn == payload.msisdn)
        .first()
    )
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    record = models.UsageRecordModel(
        msisdn=payload.msisdn,
        type=payload.type,
        quantity=payload.quantity,
        unit=payload.unit,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(record)

    # Data sessions accumulate into the line's aggregate usage counter.
    if payload.type == models.UsageType.DATA:
        line.data_usage_gb = round(line.data_usage_gb + payload.quantity, 2)

    db.commit()
    db.refresh(record)
    return record


@router.get("/lines/{msisdn}/summary", response_model=schemas.UsageSummary)
def usage_summary(
    msisdn: str,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    line = (
        db.query(models.TelecomLineModel)
        .filter(models.TelecomLineModel.msisdn == msisdn)
        .first()
    )
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    totals = (
        db.query(
            models.UsageRecordModel.type,
            func.coalesce(func.sum(models.UsageRecordModel.quantity), 0.0),
            func.count(models.UsageRecordModel.id),
        )
        .filter(models.UsageRecordModel.msisdn == msisdn)
        .group_by(models.UsageRecordModel.type)
        .all()
    )

    summary = schemas.UsageSummary(
        msisdn=msisdn,
        data_gb=0.0,
        voice_minutes=0.0,
        sms_messages=0.0,
        total_records=0,
    )
    for usage_type, qty, count in totals:
        if usage_type == models.UsageType.DATA:
            summary.data_gb = round(qty, 2)
        elif usage_type == models.UsageType.VOICE:
            summary.voice_minutes = round(qty, 2)
        else:
            summary.sms_messages = round(qty, 2)
        summary.total_records += count
    return summary