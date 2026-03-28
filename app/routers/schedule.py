import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db

schedule_router = APIRouter()

os.makedirs(settings.SCHEDULES_PATH, exist_ok=True)

@schedule_router.get("/groups/{group_id}/schedules", response_class=FileResponse)
def get_schedule(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if current_user.role not in [models.UserRole.ADMIN] and group not in current_user.groups:
        raise HTTPException(status_code=403, detail="You do not have access to this group's schedule")

    if not group.schedule_path == "":
        raise HTTPException(status_code=404, detail=f"No schedule saved for the group {group_id}")

    if not os.path.exists(group.schedule_path):
        raise HTTPException(status_code=404, detail="An error occured while fecthing the schedule for this group")

    return group.schedule_path


@schedule_router.post("/groups/{group_id}/schedules", status_code=status.HTTP_201_CREATED)
def upload_schedule(
    group_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can upload a new group's schedule")

    if not file.filename or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_ext = file.filename.split(".")[-1]
    if file_ext != "ics":
        raise HTTPException(status_code=415, detail=f"Unsupported file extension ({file_ext}), should be .ics")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    file_path = f"{settings.SCHEDULES_PATH}/group_{group_id}.ics"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    group.schedule_path = file_path

    db.commit()
    db.refresh(group)

    return None


@schedule_router.delete("/groups/{group_id}/schedules", status_code=status.HTTP_204_NO_CONTENT)
def remove_schedule(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete a group's schedule")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    os.remove(f"{settings.SCHEDULES_PATH}/group_{group_id}.ics")
    group.schedule_path = ""

    db.commit()
    db.refresh(group)

    return None
