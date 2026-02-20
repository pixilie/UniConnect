import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models

schedule_router = APIRouter()

ALLOWED_EXTENSION = {'ics'}
UPLOAD_DIR = "app/db/timetables"

@schedule_router.get("/schedules/group={group_id}", response_class=FileResponse)
def get_schedule(
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if not group.schedule_path:
        raise HTTPException(status_code=404, detail="No schedule saved for this group")

    if not os.path.exists(group.schedule_path):
        raise HTTPException(status_code=404, detail="Schedule not found")

    return group.schedule_path

@schedule_router.post("/schedules/group={group_id}")
def upload_schedule(
    group_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission Denied")

    if not file.filename or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_ext = file.filename.split(".")[1]
    if file_ext not in ALLOWED_EXTENSION:
        raise HTTPException(status_code=415, detail="Unsupported file extension, should be .ics")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    file_path = f"{UPLOAD_DIR}/group_{group_id}.ics"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    group.schedule_path = file_path

    db.commit()
    db.refresh(group)

    return {"message": "Schedule succesfuly uploaded"}

@schedule_router.delete("/schedules/group={group_id}")
def remove_schedule(
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission Denied")

    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    os.remove(f"{UPLOAD_DIR}/group_{group_id}.ics")
    group.schedule_path = ""

    db.commit()
    db.refresh(group)

    return {"message": "Schedule succesfuly removed"}
