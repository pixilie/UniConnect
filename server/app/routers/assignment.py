from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import assignment

assignment_router = APIRouter()

@assignment_router.get("/assignments/{assignment_id}", response_model=assignment.Assignment)
def get_assignment_detail(
    assignment_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if current_user.role == models.UserRole.STUDENT:
        if assignment.group_id != current_user.student_group_id:
             raise HTTPException(status_code=403, detail="You can't see this assignment")

    return assignment

@assignment_router.patch("/assignments/{assignment_id}", response_model=assignment.Assignment)
def update_assignment(
    assignment_id: int,
    update: assignment.UpdateAssignment,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission denied")

    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Devoir introuvable")

    if current_user.role in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value] and assignment.creator_id != current_user.id:
         raise HTTPException(status_code=403, detail="You can't modify this assignment")

    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(assignment, key, value)

    db.commit()
    db.refresh(assignment)
    return assignment

@assignment_router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission Denied")

    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment succesfuly deleted"}
