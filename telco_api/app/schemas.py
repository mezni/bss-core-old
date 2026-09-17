from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models import (
    AccountType,
    DeviceStatus,
    DeviceType,
    InvoiceStatus,
    LineStatus,
    UsageType,
    UserRole,
)


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# AUTH & USERS
# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(ORMBase):
    id: int
    username: str
    role: UserRole
    is_active: bool


class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.CSR


# ==========================================
# SUBSCRIBERS
# ==========================================

class SubscriberCreate(BaseModel):
    name: str
    email: str
    account_type: AccountType = AccountType.POSTPAID


class SubscriberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    account_type: Optional[AccountType] = None


class SubscriberRead(ORMBase):
    id: int
    name: str
    email: str
    account_type: AccountType
    line_count: int = 0
    device_count: int = 0
    invoice_count: int = 0


# ==========================================
# TELECOM LINES
# ==========================================

class LineCreate(BaseModel):
    msisdn: str
    iccid: str
    subscriber_id: int
    status: LineStatus = LineStatus.ACTIVE


class LineUpdate(BaseModel):
    status: Optional[LineStatus] = None
    data_usage_gb: Optional[float] = None


class LineRead(ORMBase):
    id: int
    msisdn: str
    iccid: str
    status: LineStatus
    data_usage_gb: float
    subscriber_id: int


# ==========================================
# DEVICES
# ==========================================

class DeviceCreate(BaseModel):
    imei_esn: str
    brand: str
    model_name: str
    subscriber_id: int
    device_type: DeviceType = DeviceType.SMARTPHONE
    status: DeviceStatus = DeviceStatus.ACTIVE
    assigned_msisdn: Optional[str] = None


class DeviceUpdate(BaseModel):
    status: Optional[DeviceStatus] = None
    assigned_msisdn: Optional[str] = None


class DeviceRead(ORMBase):
    id: int
    imei_esn: str
    brand: str
    model_name: str
    device_type: DeviceType
    status: DeviceStatus
    purchase_date: datetime
    subscriber_id: int
    assigned_msisdn: Optional[str]


# ==========================================
# INVOICES & PAYMENTS
# ==========================================

class InvoiceCreate(BaseModel):
    subscriber_id: int
    amount: float
    currency: str = "USD"
    status: InvoiceStatus = InvoiceStatus.UNPAID
    due_date: datetime


class InvoiceRead(ORMBase):
    id: int
    subscriber_id: int
    amount: float
    currency: str
    status: InvoiceStatus
    due_date: datetime
    created_at: datetime
    paid_total: float = 0.0


class PaymentCreate(BaseModel):
    amount_paid: float
    payment_method: str = "Credit Card"
    transaction_id: str


class PaymentRead(ORMBase):
    id: int
    invoice_id: int
    amount_paid: float
    payment_method: str
    transaction_id: str
    paid_at: datetime


# ==========================================
# USAGE & CDRs
# ==========================================

class UsageCreate(BaseModel):
    msisdn: str
    type: UsageType
    quantity: float
    unit: str
    timestamp: Optional[datetime] = None


class UsageRead(ORMBase):
    id: int
    msisdn: str
    type: UsageType
    quantity: float
    unit: str
    timestamp: datetime


class UsageSummary(BaseModel):
    msisdn: str
    data_gb: float
    voice_minutes: float
    sms_messages: float
    total_records: int


class MessageResponse(BaseModel):
    message: str