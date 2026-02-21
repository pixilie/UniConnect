from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import user

user_router = APIRouter()

@user_router.get("/users", response_model=List[user.User])
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

@user_router.get("/users/me", response_model=user.User)
def get_my_profile(
    updates: user.UserUpdateProfile,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.User).filter(models.User.id == current_user.id).first()

@user_router.post("/users/me/password")
def change_password(
    passwords: user.UserUpdatePassword,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if not security.verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incrorrect password")

    current_user.hashed_password = security.get_password_hash(passwords.new_password)

    db.commit()

    return {"message": "Password succesfuly updated"}

@user_router.patch("/users/{user_id}/teacher-group/{group_id}")
def update_teacher_group(
    user_id: int,
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    teacher = db.query(models.User).filter(models.User.id == user_id).first()
    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not teacher or not group:
        raise HTTPException(status_code=404, detail="Group or teacher not found")

    if teacher.role != models.UserRole.TEACHER.value:
         raise HTTPException(status_code=400, detail="This user is not a teacher")

    if group not in teacher.teaching_groups:
        teacher.teaching_groups.append(group)
    else:
        teacher.teaching_groups.remove(group)

    db.commit()

    return {"message": "Succesfuly added group"}

@user_router.patch("/users/me", response_model=user.User)
def update_my_profile(
    updates: user.UserUpdateProfile,
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

@user_router.patch("/users/{user_id}/role", response_model=user.User)
def update_user_role(
    user_id: int,
    role_data: user.UserRoleUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.role in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        if current_user.role != models.UserRole.ADMIN.value:
            raise HTTPException(status_code=403, detail="Only Admins can modify other Admins/Teachers")
    else:
        if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
             raise HTTPException(status_code=403, detail="Permission denied")

    target_user.role = role_data.role

    db.commit()
    db.refresh(target_user)
    return target_user

@user_router.patch("/users/{user_id}/student-group/{group_id}", response_model=user.User)
def update_user_student_group(
    user_id: int,
    group_id: Optional[int],
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Only Teachers or Admins can assign groups")

    if group_id is not None:
        group = db.query(models.Group).filter(models.Group.id == group_id).first()
        if not group:
             raise HTTPException(status_code=404, detail="Group not found")

    target_user.student_group_id = group_id

    db.commit()
    db.refresh(target_user)
    return target_user

@user_router.delete("/users/{user_id}", response_model=user.User)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You need admin privileges to do that")

    db.delete(target_user)
    db.commit()

    return {"message": "User succesfuly deleted"}
