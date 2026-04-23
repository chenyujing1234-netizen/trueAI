from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import AuthResponse, UserLogin, UserOut, UserRegister

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    exists = db.query(User).filter_by(username=payload.username).first()
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已被占用")
    if payload.email:
        exists = db.query(User).filter_by(email=payload.email).first()
        if exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "邮箱已被占用")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    return AuthResponse(token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
