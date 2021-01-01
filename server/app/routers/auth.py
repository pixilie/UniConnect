from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db

auth_router = APIRouter()

@auth_router.post("/register", response_model=schemas.User)
def register_user(user: schemas.RegistrationRequest, db: Session = Depends(get_db)):
    query = db.query(models.User)

    if query.filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = get_password_hash(user.password)

    new_user = models.User(
        email = user.email,
        hashed_password = hashed_pw,
        first_name = user.first_name,
        last_name = user.last_name,
        role = models.UserRole.ADMIN.value if query.count() == 0 else models.UserRole.STUDENT.value
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data = {
            "sub": str(user.id),
            "role": str(user.role)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user.role,
        "user_id": user.id
    }
