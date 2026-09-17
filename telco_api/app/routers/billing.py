from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, require_role
from app.database import get_db

router = APIRouter(tags=["billing"])

WRITE_AUTH = require_role(models.UserRole.CSR)


def _invoice_read(invoice: models.InvoiceModel) -> schemas.InvoiceRead:
    paid_total = round(sum(p.amount_paid for p in invoice.payments), 2)
    return schemas.InvoiceRead(
        id=invoice.id,
        subscriber_id=invoice.subscriber_id,
        amount=invoice.amount,
        currency=invoice.currency,
        status=invoice.status,
        due_date=invoice.due_date,
        created_at=invoice.created_at,
        paid_total=paid_total,
    )


# ==========================================
# INVOICES
# ==========================================

@router.get("/invoices", response_model=list[schemas.InvoiceRead])
def list_invoices(
    subscriber_id: Optional[int] = None,
    invoice_status: Optional[models.InvoiceStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.InvoiceModel)
    if subscriber_id:
        query = query.filter(models.InvoiceModel.subscriber_id == subscriber_id)
    if invoice_status:
        query = query.filter(models.InvoiceModel.status == invoice_status)
    invoices = query.order_by(models.InvoiceModel.due_date.desc()).offset(skip).limit(limit).all()
    return [_invoice_read(i) for i in invoices]


@router.post("/invoices", response_model=schemas.InvoiceRead, status_code=201)
def create_invoice(
    payload: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    subscriber = db.get(models.SubscriberModel, payload.subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    invoice = models.InvoiceModel(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return _invoice_read(invoice)


@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    invoice = db.get(models.InvoiceModel, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _invoice_read(invoice)


# ==========================================
# PAYMENTS
# ==========================================

@router.get("/payments", response_model=list[schemas.PaymentRead])
def list_payments(
    invoice_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    query = db.query(models.PaymentModel)
    if invoice_id:
        query = query.filter(models.PaymentModel.invoice_id == invoice_id)
    return query.order_by(models.PaymentModel.paid_at.desc()).offset(skip).limit(limit).all()


@router.post("/invoices/{invoice_id}/payments", response_model=schemas.PaymentRead, status_code=201)
def create_payment(
    invoice_id: int,
    payload: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(WRITE_AUTH),
):
    invoice = db.get(models.InvoiceModel, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    existing_txn = (
        db.query(models.PaymentModel)
        .filter(models.PaymentModel.transaction_id == payload.transaction_id)
        .first()
    )
    if existing_txn:
        raise HTTPException(status_code=409, detail="Transaction ID already used")

    payment = models.PaymentModel(invoice_id=invoice_id, **payload.model_dump())
    db.add(payment)
    db.flush()

    # Auto-mark the invoice as Paid once aggregate payments cover the amount.
    paid_total = sum(p.amount_paid for p in invoice.payments) + payload.amount_paid
    if paid_total >= invoice.amount and invoice.status != models.InvoiceStatus.PAID:
        invoice.status = models.InvoiceStatus.PAID

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/payments/{payment_id}", response_model=schemas.PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    payment = db.get(models.PaymentModel, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


def _billing_overview(db: Session) -> dict:
    from sqlalchemy import func

    by_status = (
        db.query(
            models.InvoiceModel.status,
            func.count(models.InvoiceModel.id),
            func.coalesce(func.sum(models.InvoiceModel.amount), 0.0),
        )
        .group_by(models.InvoiceModel.status)
        .all()
    )
    return {
        str(row[0]): {"invoices": row[1], "total_amount": round(row[2], 2)}
        for row in by_status
    }


@router.get("/billing/overview", response_model=dict)
def billing_overview(
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(get_current_user),
):
    return _billing_overview(db)