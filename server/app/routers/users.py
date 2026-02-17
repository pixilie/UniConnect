from typing import List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import user_schemas

user_router = APIRouter()

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"

@user_router.post("/register", response_model=user_schemas.UserOut)
def register_user(user: user_schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = security.get_password_hash(user.password)

    new_user = models.User(
        email = user.email,
        hashed_password = hashed_pw,
        first_name = user.first_name,
        last_name = user.last_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.post("/login")
def login(user_credentials: user_schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user or not security.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user.role
    }

@user_router.get("/users", response_model=List[user_schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
