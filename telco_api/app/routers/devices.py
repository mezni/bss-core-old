from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, require_role
from app.database import get_db

router = APIRouter(prefix="/devices", tags=["devices"])

WRITE_AUTH = require_role(models.UserRole.CSR)


@router.get("", response_model=list[schemas.DeviceRead])
def list_devices(
    device_type: Optional[models.DeviceType] = None,
    device_status: Optional[models.DeviceStatus] = None,
    subscriber_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.DeviceModel)
    if device_type:
        query = query.filter(models.DeviceModel.device_type == device_type)
    if device_status:
        query = query.filter(models.DeviceModel.status == device_status)
    if subscriber_id:
        query = query.filter(models.DeviceModel.subscriber_id == subscriber_id)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=schemas.DeviceRead, status_code=201)
def create_device(
    payload: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    subscriber = db.get(models.SubscriberModel, payload.subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    if db.query(models.DeviceModel).filter(
        models.DeviceModel.imei_esn == payload.imei_esn
    ).first():
        raise HTTPException(status_code=409, detail="IMEI/ESN already exists")

    if payload.assigned_msisdn:
        line = (
            db.query(models.TelecomLineModel)
            .filter(models.TelecomLineModel.msisdn == payload.assigned_msisdn)
            .first()
        )
        if not line:
            raise HTTPException(status_code=404, detail="Assigned MSISDN not found")

    device = models.DeviceModel(
        imei_esn=payload.imei_esn,
        brand=payload.brand,
        model_name=payload.model_name,
        device_type=payload.device_type,
        status=payload.status,
        purchase_date=datetime.utcnow(),
        subscriber_id=payload.subscriber_id,
        assigned_msisdn=payload.assigned_msisdn,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/{device_id}", response_model=schemas.DeviceRead)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    device = db.get(models.DeviceModel, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}/status", response_model=schemas.DeviceRead)
def update_device_status(
    device_id: int,
    new_status: models.DeviceStatus,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    device = db.get(models.DeviceModel, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.status = new_status
    db.commit()
    db.refresh(device)
    return device


@router.patch("/{device_id}/assign", response_model=schemas.DeviceRead)
def assign_device_to_line(
    device_id: int,
    assigned_msisdn: str,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    device = db.get(models.DeviceModel, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    line = (
        db.query(models.TelecomLineModel)
        .filter(models.TelecomLineModel.msisdn == assigned_msisdn)
        .first()
    )
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    device.assigned_msisdn = line.msisdn
    db.commit()
    db.refresh(device)
    return device