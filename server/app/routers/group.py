import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import group_schemas

group_router = APIRouter()

UPLOAD_DIR = "app/db/timetables"

@group_router.post("/group/", response_model=group_schemas.Group)
def create_group(
    group_data: group_schemas.NewGroup,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    new_group = models.ClassGroup (
        name = group_data.name,
        schedule_path = group_data.schedule_path if group_data.schedule_path else None
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group

@group_router.delete("/group/group_id={group_id}")
def delete_group(
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    class_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()

    if not class_group:
        raise HTTPException(status_code=404, detail="Class not found")

    os.remove(f"{UPLOAD_DIR}/group_{group_id}")

    db.commit()
    db.delete(class_group)
    return {"message": "Group succesfuly deleted"}


@group_router.get("/group/group_id={group_id}", response_model=List[group_schemas.Group])
def get_group(
    group_id: Optional[int],
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")

    if group_id:
        return db.query(models.ClassGroup).all()
    else:
        group = db.query(models.ClassGroup).filter(group_id = models.ClassGroup.id).first()

        if not group:
            raise HTTPException(status_code=404, detail="Class not found")

        return group

@group_router.patch("/group/group_id={group_id}", response_model=List[group_schemas.Group])
def update_group(
    group_id: int,
    group_data: group_schemas.UpdateGroup,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    group = db.query(models.ClassGroup).filter(group_id = models.ClassGroup.id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Class not found")

    if group_data.name:
        group.name = group_data.name

    # TODO: Confusion with schedule_router logic
    if group_data.schedule_path:
        group.schedule_path = group_data.schedule_path

    db.commit()
    db.refresh(group)

    return group
