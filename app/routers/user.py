from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user, get_password_hash, verify_password
from app.db.database import get_db

user_router = APIRouter()


@user_router.get("/users", response_model=List[schemas.User])
def search_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.User)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (models.User.first_name.ilike(search_fmt))
            | (models.User.last_name.ilike(search_fmt))
            | (models.User.email.ilike(search_fmt))
        )

    if role:
        query = query.filter(models.User.role == role)

    if (
        current_user.role == models.UserRole.STUDENT
        or current_user.role == models.UserRole.DELEGATE
    ):
        current_group_ids = [g.id for g in current_user.groups]
        query = query.filter(
            models.User.groups.any(models.Group.id.in_(current_group_ids))
        )

    query = query.offset(skip).limit(limit).all()

    if len(query) == 0:
        raise HTTPException(status_code=404, detail=f"No user matching {search} found")
    else:
        return query


@user_router.get("/users/me", response_model=schemas.User)
def get_my_profile(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.query(models.User).filter(models.User.id == current_user.id).first()


@user_router.post("/users/me/password")
def change_password(
    passwords: schemas.UserUpdatePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incrorrect password")

    current_user.hashed_password = get_password_hash(passwords.new_password)

    db.commit()

    return {"message": "Password succesfuly updated"}


@user_router.patch("/users/{user_id}/groups/{group_id}", response_model=schemas.User)
def toggle_user_group(
    user_id: int,
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only administrators can assign groups"
        )

    target_user = db.query(models.User).filter(models.User.id == user_id).first()

    if target_user == current_user:
        raise HTTPException(status_code=403, detail="You can't kick yourself")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if target_user.role in [models.UserRole.STUDENT, models.UserRole.DELEGATE]:
        if group in target_user.groups:
            target_user.groups = []
        else:
            target_user.groups = [group]
    else:
        if group in target_user.groups:
            target_user.groups.remove(group)
        else:
            target_user.groups.append(group)

    db.commit()
    db.refresh(target_user)

    return target_user


@user_router.patch("/users/me", response_model=schemas.User)
def update_my_profile(
    updates: schemas.UserUpdateProfile,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
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


@user_router.patch("/users/{user_id}/role", response_model=schemas.User)
def update_user_role(
    user_id: int,
    role: models.UserRole,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if current_user == target_user:
        raise HTTPException(status_code=403, detail="You can't change your own role")

    if target_user.role in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
        if current_user.role != models.UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can modify administrator/teacher roles",
            )
    else:
        if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
            raise HTTPException(
                status_code=403,
                detail="Only administrators/teachers can modify user roles",
            )

    target_user.role = role

    if role == models.UserRole.ADMIN:
        all_groups = db.query(models.Group).all()
        target_user.groups = all_groups

    db.commit()
    db.refresh(target_user)
    return target_user


@user_router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only administators can delete a user"
        )

    db.delete(target_user)
    db.commit()

    return {"message": "User succesfuly deleted"}
