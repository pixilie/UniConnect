import os
import shutil
from pickle import INT
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import assignment, event, group, message, user

group_router = APIRouter()

ALLOWED_EXTENSION = {'ics'}
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

@group_router.get("/groups/{group_id}/members", response_model=List[user.User])
def get_group_members(
    group_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if not db.query(models.Group).first():
        raise HTTPException(status_code=404, detail="Group not found")

    return db.query(models.User).filter(models.User.student_group_id == group_id or models.User.teaching_groups == group_id).all()


@group_router.get("/groups/{group_id}/assignments", response_model=List[assignment.Assignment])
def get_assignments(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Assignment)

    if current_user.role == models.UserRole.STUDENT:
        if not current_user.student_group_id:
            return []
        query = query.filter(models.Assignment.group_id == current_user.student_group_id)
    else:
        query = query.filter(models.Assignment.group_id == group_id)

    return query.order_by(models.Assignment.due_date.asc()).offset(skip).limit(limit).all()

@group_router.get("/groups/{group_id}/schedules", response_class=FileResponse)
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

@group_router.get("/groups/{group_id}/messages", response_model=List[message.Message])
def get_messages(
    group_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Message).filter(models.Message.group_id == group_id).offset(skip).limit(limit).all()

@group_router.post("/groups/{group_id}/assignments", response_model=assignment.Assignment)
def new_assignments(
    group_id: int,
    assignment_data: assignment.NewAssignment,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission Denied")

    new_assignment = models.Assignment(
        title = assignment_data.title,
        description = assignment_data.description,
        due_date = assignment_data.due_date,
        created_at = datetime.now(timezone.utc),
        group_id = group_id,
        creator_id = current_user.id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

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

@group_router.post("/groups/{group_id}/events", response_model=event.Event)
def create_event(
    group_id: int,
    event_data: event.NewEvent,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    (address, latitude, longitude) = geocoding.get_coordinates(event_data.location)

    new_event = models.Event(
        title = event_data.title,
        description = event_data.description,
        date = event_data.date,
        location = address,
        latitude = latitude,
        longitude = longitude,
        type = event_data.type,
        creator_id = current_user.id,
        group_id = group_id
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

@group_router.post("/groups/{group_id}/schedules")
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

@group_router.patch("/groups/{group_id}", response_model=group.Group)
def update_group_name(
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

    db.commit()
    db.refresh(group)

    return group

@group_router.delete("/groups/{group_id}")
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

@group_router.delete("/groups/{group_id}/schedules")
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
