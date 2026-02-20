import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import group

group_router = APIRouter()

UPLOAD_DIR = "app/db/timetables"

@group_router.get("/groups/", response_model=List[group.Group])
def get_group(
    group_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Permission denied")

    if group_id:
        return db.query(models.Group).filter(group_id == models.Group.id)
    else:
        return db.query(models.Group).offset(skip).limit(limit).all()

@group_router.post("/groups/", response_model=group.Group)
def create_group(
    group_data: group.NewGroup,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    new_group = models.Group (
        name = group_data.name,
        schedule_path = group_data.schedule_path if group_data.schedule_path else None
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group

@group_router.patch("/groups/group_id={group_id}", response_model=group.Group)
def update_group(
    group_id: int,
    group_data: group.UpdateGroup,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    group = db.query(models.Group).filter(group_id == models.Group.id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group_data.name:
        group.name = group_data.name

    # TODO: Confusion with schedule_router logic
    if group_data.schedule_path:
        group.schedule_path = group_data.schedule_path

    db.commit()
    db.refresh(group)

    return group

@group_router.delete("/groups/group_id={group_id}")
def delete_group(
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.schedule_path and os.path.exists(f"{UPLOAD_DIR}/group_{group_id}.ics"):
        os.remove(f"{UPLOAD_DIR}/group_{group_id}.ics")

    events = db.query(models.Event).filter(models.Event.group_id == group_id).all()
    for event in events:
        print(event)
        db.delete(event)

    db.delete(group)
    db.commit()

    return {"message": "Group succesfuly deleted"}
