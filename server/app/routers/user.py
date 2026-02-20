from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import user_schemas

user_router = APIRouter()

@user_router.post("/register", response_model=user_schemas.User)
def register_user(user: user_schemas.RegistrationRequest, db: Session = Depends(get_db)):
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
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

@user_router.get("/users", response_model=List[user_schemas.User])
def search_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (models.User.first_name.ilike(search_fmt)) |
            (models.User.last_name.ilike(search_fmt)) |
            (models.User.email.ilike(search_fmt))
        )

    if role:
        query = query.filter(models.User.role == role)

    return query.offset(skip).limit(limit).all()

@user_router.patch("/users/me", response_model=user_schemas.User)
def update_my_profile(
    updates: user_schemas.UserUpdateProfile,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):

    if updates.first_name:
        current_user.first_name = updates.first_name
    if updates.last_name:
        current_user.last_name = updates.last_name
    if updates.email:
        current_user.email = updates.email

    db.commit()
    db.refresh(current_user)

    return current_user

@user_router.post("/users/me/password")
def change_password(
    passwords: user_schemas.UserUpdatePassword,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):

    if not security.verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incrorrect password")

    current_user.hashed_password = security.get_password_hash(passwords.new_password)

    db.commit()
    return {"message": "Password succesfuly updated"}
