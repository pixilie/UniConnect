from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import user_schemas

admin_router = APIRouter()

@admin_router.delete("/admin/users={user_id}/classes={class_id}")
def remove_class_from_teacher(
    user_id: int,
    class_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    teacher = db.query(models.User).filter(models.User.id == user_id).first()
    class_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == class_id).first()

    if not teacher or not class_group:
        raise HTTPException(status_code=404, detail="Not found")

    if class_group in teacher.teaching_classes:
        teacher.teaching_classes.remove(class_group)
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="This user is not teaching to this class")

    return {"message": "Class succesfuly deleted"}

@admin_router.post("/admin/user_id={user_id}/group_id={group_id}")
def add_class_to_teacher(
    user_id: int,
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You need administrator privileges to do that")

    teacher = db.query(models.User).filter(models.User.id == user_id).first()
    class_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()

    if not teacher or not class_group:
        raise HTTPException(status_code=404, detail="Not found")

    if teacher.role != models.UserRole.TEACHER.value:
         raise HTTPException(status_code=400, detail="This user is not a teacher")

    if class_group not in teacher.teaching_classes:
        teacher.teaching_classes.append(class_group)
        db.commit()

    return {"message": "Succesfuly added class"}

@admin_router.patch("/admin/user_id={user_id}", response_model=user_schemas.User)
def update_user_status(
    user_id: int,
    updates: user_schemas.UserUpdateAdmin,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.role in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        if current_user.role != models.UserRole.ADMIN.value:
            raise HTTPException(status_code=403, detail="You need admin privileges to do that")
        else:
            if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
                 raise HTTPException(status_code=403, detail="Permission denied")

    if updates.role:
        target_user.role = updates.role

    if updates.student_class_id is not None:
        if updates.student_class_id > 0:
            cls = db.query(models.ClassGroup).filter(models.ClassGroup.id == updates.student_class_id).first()
            if not cls:
                 raise HTTPException(status_code=404, detail="Class not found")

        target_user.student_class_id = updates.student_class_id

    if updates.teaching_class_ids is not None:
        classes_to_teach = db.query(models.ClassGroup).filter(
            models.ClassGroup.id.in_(updates.teaching_class_ids)
        ).all()

        target_user.teaching_classes = classes_to_teach

    db.commit()
    db.refresh(target_user)
    return target_user
