from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.domain.models import Customer
from src.infrastructure.db.config import get_db

# OAuth2 password bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(token_url="token")

# JWT settings per BSS-Core Constitution Section 9
JWT_SECRET_KEY = "change-me-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        ) from e


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> Customer:
    """Get the current authenticated user from JWT token."""
    payload = decode_token(token)
    customer_id: int = payload.get("sub")
    if customer_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    # Look up customer from database
    from src.infrastructure.db import models as db_models

    customer = db.query(db_models.Customer).filter(db_models.Customer.id == customer_id).first()

    if customer is None:
        raise HTTPException(status_code=401, detail="User not found")

    return customer


async def get_optional_current_user(
    token: str | None = None,
    db=Depends(get_db),
) -> Customer | None:
    """Get current user if token provided, otherwise return None."""
    if token is None:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except HTTPException:
        return None
