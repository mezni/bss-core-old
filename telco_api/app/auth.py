from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
import app.models as models

# --- SECURITY CONFIGURATION ---
# In production, load this from an environment variable (e.g., via pydantic-settings)
SECRET_KEY = "SUPER_SECRET_TELECOM_CRM_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- PASSWORD UTILITIES ---

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against the stored hash."""
    return password_hash.verify(plain_password, hashed_password)


# --- JWT TOKEN UTILITIES ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- FASTAPI AUTH DEPENDENCIES ---

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.UserModel:
    """FastAPI dependency to extract and validate the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = (
        db.query(models.UserModel)
        .filter(models.UserModel.username == username)
        .first()
    )
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(required_role: models.UserRole):
    """FastAPI dependency factory for Role-Based Access Control (RBAC)."""
    def role_checker(current_user: models.UserModel = Depends(get_current_user)):
        # Admins automatically bypass role restriction checks
        if (
            current_user.role != required_role
            and current_user.role != models.UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your user role",
            )
        return current_user

    return role_checker