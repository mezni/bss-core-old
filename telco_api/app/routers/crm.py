from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, require_role
from app.database import get_db

subscriber_router = APIRouter(prefix="/subscribers", tags=["crm"])
line_router = APIRouter(prefix="/lines", tags=["crm"])

WRITE_AUTH = require_role(models.UserRole.CSR)


# ==========================================
# SUBSCRIBERS
# ==========================================

def _attach_counts(subscriber: models.SubscriberModel) -> schemas.SubscriberRead:
    return schemas.SubscriberRead(
        id=subscriber.id,
        name=subscriber.name,
        email=subscriber.email,
        account_type=subscriber.account_type,
        line_count=len(subscriber.lines),
        device_count=len(subscriber.devices),
        invoice_count=len(subscriber.invoices),
    )


@subscriber_router.get("", response_model=list[schemas.SubscriberRead])
def list_subscribers(
    account_type: Optional[models.AccountType] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.SubscriberModel)
    if account_type:
        query = query.filter(models.SubscriberModel.account_type == account_type)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.SubscriberModel.name.ilike(like))
            | (models.SubscriberModel.email.ilike(like))
        )
    subscribers = query.offset(skip).limit(limit).all()
    return [_attach_counts(s) for s in subscribers]


@subscriber_router.post("", response_model=schemas.SubscriberRead, status_code=201)
def create_subscriber(
    payload: schemas.SubscriberCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    existing = (
        db.query(models.SubscriberModel)
        .filter(models.SubscriberModel.email == payload.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")

    subscriber = models.SubscriberModel(
        name=payload.name,
        email=payload.email,
        account_type=payload.account_type,
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return _attach_counts(subscriber)


@subscriber_router.get("/{subscriber_id}", response_model=schemas.SubscriberRead)
def get_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    subscriber = db.get(models.SubscriberModel, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return _attach_counts(subscriber)


@subscriber_router.patch("/{subscriber_id}", response_model=schemas.SubscriberRead)
def update_subscriber(
    subscriber_id: int,
    payload: schemas.SubscriberUpdate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    subscriber = db.get(models.SubscriberModel, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    if payload.email and payload.email != subscriber.email:
        conflict = (
            db.query(models.SubscriberModel)
            .filter(models.SubscriberModel.email == payload.email)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=409, detail="Email already in use")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(subscriber, field, value)
    db.commit()
    db.refresh(subscriber)
    return _attach_counts(subscriber)


@subscriber_router.delete("/{subscriber_id}", status_code=204)
def delete_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    subscriber = db.get(models.SubscriberModel, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    db.delete(subscriber)
    db.commit()


# ==========================================
# TELECOM LINES
# ==========================================

@line_router.get("", response_model=list[schemas.LineRead])
def list_lines(
    status: Optional[models.LineStatus] = None,
    subscriber_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.TelecomLineModel)
    if status:
        query = query.filter(models.TelecomLineModel.status == status)
    if subscriber_id:
        query = query.filter(models.TelecomLineModel.subscriber_id == subscriber_id)
    return query.offset(skip).limit(limit).all()


@line_router.post("", response_model=schemas.LineRead, status_code=201)
def create_line(
    payload: schemas.LineCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    subscriber = db.get(models.SubscriberModel, payload.subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    if db.query(models.TelecomLineModel).filter(
        models.TelecomLineModel.msisdn == payload.msisdn
    ).first():
        raise HTTPException(status_code=409, detail="MSISDN already exists")
    if db.query(models.TelecomLineModel).filter(
        models.TelecomLineModel.iccid == payload.iccid
    ).first():
        raise HTTPException(status_code=409, detail="ICCID already exists")

    line = models.TelecomLineModel(**payload.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@line_router.get("/stats/summary", response_model=dict)
def line_summary(
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    rows = (
        db.query(
            models.TelecomLineModel.status,
            func.count(models.TelecomLineModel.id),
            func.coalesce(func.sum(models.TelecomLineModel.data_usage_gb), 0.0),
        )
        .group_by(models.TelecomLineModel.status)
        .all()
    )
    return {
        row[0].value: {"lines": row[1], "data_usage_gb": round(row[2], 2)}
        for row in rows
    }


@line_router.get("/{line_id}", response_model=schemas.LineRead)
def get_line(
    line_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    line = db.get(models.TelecomLineModel, line_id)
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    return line


@line_router.patch("/{line_id}/status", response_model=schemas.LineRead)
def update_line_status(
    line_id: int,
    new_status: models.LineStatus,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    line = db.get(models.TelecomLineModel, line_id)
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    line.status = new_status
    db.commit()
    db.refresh(line)
    return line