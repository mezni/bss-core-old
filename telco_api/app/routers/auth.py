from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import create_access_token, get_current_user, require_role, verify_password
from app.database import get_db

router = APIRouter(tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 password flow: exchange username/password for a JWT."""
    user = (
        db.query(models.UserModel)
        .filter(models.UserModel.username == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated"
        )

    access_token = create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token, token_type="bearer")


@users_router.get("", response_model=list[schemas.UserRead])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
):
    return db.query(models.UserModel).offset(skip).limit(limit).all()


@users_router.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.UserModel = Depends(get_current_user)):
    return current_user


@users_router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
):
    user = db.get(models.UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.post("", response_model=schemas.UserRead, status_code=201)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
):
    from app.auth import hash_password

    existing = (
        db.query(models.UserModel)
        .filter(models.UserModel.username == payload.username)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = models.UserModel(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@users_router.patch("/{user_id}/status", response_model=schemas.UserRead)
def set_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    _: models.UserModel = Depends(require_role(models.UserRole.ADMIN)),
):
    user = db.get(models.UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user