import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db

group_router = APIRouter()

@group_router.get("/groups/", response_model=List[schemas.Group])
def get_group(
    group_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only administrators/teachers can browse groups")

    if group_id:
        return db.query(models.Group).filter(models.Group.id == group_id)
    else:
        return db.query(models.Group).offset(skip).limit(limit).all()


@group_router.get("/groups/{group_id}/members", response_model=List[schemas.User])
def get_group_members(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(status_code=403, detail="Not authorized to access this group")

    if not db.query(models.Group).filter(models.Group.id == group_id).first():
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    return db.query(models.User).filter(models.User.groups.any(models.Group.id == group_id)).all()


@group_router.get("/groups/{group_id}/messages", response_model=List[schemas.Message])
def get_messages(
    group_id: int,
    skip: int = 0,
    limit: int = 999999,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(status_code=403, detail="Not authorized to access this group")

    return db.query(models.Message).filter(models.Message.group_id == group_id).offset(skip).limit(limit).all()


@group_router.post("/groups/", response_model=schemas.Group)
def create_group(
    group_data: schemas.NewGroup,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can create groups")

    new_group = models.Group (
        name = group_data.name,
        schedule_path = group_data.schedule_path if group_data.schedule_path else None
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


@group_router.patch("/groups/{group_id}", response_model=schemas.Group)
def update_group_name(
    group_id: int,
    group_data: schemas.UpdateGroup,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can modify a group")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if group_data.name:
        group.name = group_data.name

    db.commit()
    db.refresh(group)

    return group


@group_router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete a group")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if group.schedule_path and os.path.exists(f"{settings.SCHEDULES_PATH}/group_{group_id}.ics"):
        os.remove(f"{settings.SCHEDULES_PATH}/group_{group_id}.ics")

    events = db.query(models.Event).filter(models.Event.group_id == group_id).all()
    for e in events:
        db.delete(e)

    db.delete(group)
    db.commit()

    return {"message": "Group succesfuly deleted"}
