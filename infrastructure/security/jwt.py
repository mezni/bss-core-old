from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import datetime
import os

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    scopes: Optional[list] = None
    sub: Optional[str] = None


def create_access_token(subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create a JWT access token."""
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            return None
        return TokenData(sub=sub)
    except JWTError:
        return None


def get_current_user(
    security_scopes: SecurityScopes = oauth2_scheme,
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHENTICATED,
            detail="Invalid authentication credentials",
        )
    return {"sub": user.sub}