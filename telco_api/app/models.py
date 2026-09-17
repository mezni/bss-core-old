from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.database import Base


# ==========================================
# ENUMS
# ==========================================

class UserRole(str, Enum):
    ADMIN = "Admin"
    CSR = "CSR"  # Customer Service Representative


class AccountType(str, Enum):
    PREPAID = "Prepaid"
    POSTPAID = "Postpaid"


class LineStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    PENDING = "Pending"


class DeviceType(str, Enum):
    SMARTPHONE = "Smartphone"
    ROUTER = "Router/MiFi"
    TABLET = "Tablet"
    WEARABLE = "Wearable"
    SET_TOP_BOX = "SetTopBox"


class DeviceStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    BLACKLISTED = "Blacklisted"
    RETURNED = "Returned"


class InvoiceStatus(str, Enum):
    UNPAID = "Unpaid"
    PAID = "Paid"
    OVERDUE = "Overdue"


class UsageType(str, Enum):
    DATA = "Data"
    VOICE = "Voice"
    SMS = "SMS"


# ==========================================
# AUTHENTICATION & USERS
# ==========================================

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CSR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


# ==========================================
# CRM & TELECOM LINES
# ==========================================

class SubscriberModel(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(SQLEnum(AccountType), default=AccountType.POSTPAID, nullable=False)

    # Relationships
    lines = relationship("TelecomLineModel", back_populates="subscriber", cascade="all, delete-orphan")
    devices = relationship("DeviceModel", back_populates="subscriber", cascade="all, delete-orphan")
    invoices = relationship("InvoiceModel", back_populates="subscriber", cascade="all, delete-orphan")


class TelecomLineModel(Base):
    __tablename__ = "telecom_lines"

    id = Column(Integer, primary_key=True, index=True)
    msisdn = Column(String, unique=True, index=True, nullable=False)
    iccid = Column(String, unique=True, nullable=False)
    status = Column(SQLEnum(LineStatus), default=LineStatus.ACTIVE, nullable=False)
    data_usage_gb = Column(Float, default=0.0, nullable=False)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)

    # Relationships
    subscriber = relationship("SubscriberModel", back_populates="lines")
    device = relationship("DeviceModel", back_populates="line", uselist=False)
    usage_records = relationship("UsageRecordModel", back_populates="line", cascade="all, delete-orphan")


# ==========================================
# DEVICES & EQUIPMENT
# ==========================================

class DeviceModel(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    imei_esn = Column(String, unique=True, index=True, nullable=False)
    brand = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    device_type = Column(SQLEnum(DeviceType), default=DeviceType.SMARTPHONE, nullable=False)
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.ACTIVE, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    assigned_msisdn = Column(String, ForeignKey("telecom_lines.msisdn"), nullable=True)

    # Relationships
    subscriber = relationship("SubscriberModel", back_populates="devices")
    line = relationship("TelecomLineModel", back_populates="device")


# ==========================================
# BILLING & PAYMENTS
# ==========================================

class InvoiceModel(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UNPAID, nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subscriber = relationship("SubscriberModel", back_populates="invoices")
    payments = relationship("PaymentModel", back_populates="invoice", cascade="all, delete-orphan")


class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String, default="Credit Card", nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    invoice = relationship("InvoiceModel", back_populates="payments")


# ==========================================
# USAGE & CDRs
# ==========================================

class UsageRecordModel(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    msisdn = Column(String, ForeignKey("telecom_lines.msisdn"), nullable=False, index=True)
    type = Column(SQLEnum(UsageType), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Relationships
    line = relationship("TelecomLineModel", back_populates="usage_records")