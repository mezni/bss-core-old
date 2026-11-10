"""FastAPI dependencies for customer management."""

from __future__ import annotations

import os

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.domain.database import get_db

from ..application.service import CustomerEligibilityAdapter
from ..application.use_cases import CustomerService
from ..infrastructure.repository import SQLAlchemyCustomerRepository

CUSTOMER_VIEW = "customer:view"
CUSTOMER_MANAGE = "customer:manage"
JWT_ALGORITHM = "HS256"
_DEV_SECRET = "bss-core-dev-secret"


def _jwt_secret() -> str:
    return os.environ.get("BSS_JWT_SECRET", _DEV_SECRET)


def get_permissions(authorization: str | None = Header(default=None)) -> set[str]:
    """Extract permissions from a signed bearer token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    permissions = payload.get("permissions", [])
    if not isinstance(permissions, (list, tuple, set)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {str(permission) for permission in permissions}


def require_customer_view(permissions: set[str] = Depends(get_permissions)) -> None:
    """Require read access to customers."""
    if CUSTOMER_VIEW not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing customer:view permission",
        )


def require_customer_manage(permissions: set[str] = Depends(get_permissions)) -> None:
    """Require write access to customers."""
    if CUSTOMER_MANAGE not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing customer:manage permission",
        )


def get_customer_repository(
    session: Session = Depends(get_db),
) -> SQLAlchemyCustomerRepository:
    return SQLAlchemyCustomerRepository(session)


def get_customer_service(
    repository: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    return CustomerService(repository)


def get_customer_eligibility_port(
    repository: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
) -> CustomerEligibilityAdapter:
    return CustomerEligibilityAdapter(repository)
