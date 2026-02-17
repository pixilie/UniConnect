from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import assignment_schemas

assignment_router = APIRouter()

@assignment_router.post("/new_assignements", response_model=assignment_schemas.Assignment)
def new_assignments(
    assignment_data: assignment_schemas.NewAssignment,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    print(f"MON ROLE EN DB: '{current_user.role}' (Type: {type(current_user.role)})")
    print(f"ROLE ATTENDU: '{models.UserRole.ADMIN.value}' (Type: {type(models.UserRole.ADMIN)})")
    if current_user.role not in [models.UserRole.ADMIN.value, models.UserRole.TEACHER.value]:
        raise HTTPException(status_code=403, detail="Permission Denied")

    new_assignment = models.Assignment(
        title = assignment_data.title,
        description = assignment_data.description,
        due_date = assignment_data.due_date,
        created_at = datetime.now(timezone.utc),
        class_id = assignment_data.class_id,
        creator_id = current_user.id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

@assignment_router.delete("/remove_assignements/{assignment_id}")
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

@assignment_router.patch("/assignments/{assignment_id}", response_model=assignment_schemas.Assignment)
def update_assignment(
    assignment_id: int,
    update: assignment_schemas.UpdateAssignment,
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

@assignment_router.get("/assignments", response_model=List[assignment_schemas.Assignment])
def get_assignments(
    class_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Assignment)

    if current_user.role == models.UserRole.STUDENT:
        if not current_user.student_class_id:
            return []
        query = query.filter(models.Assignment.class_id == current_user.student_class_id)
    else:
        if class_id:
            query = query.filter(models.Assignment.class_id == class_id)

    return query.order_by(models.Assignment.due_date.asc()).offset(skip).limit(limit).all()

@assignment_router.get("/assignments/{assignment_id}", response_model=assignment_schemas.Assignment)
def get_assignment_detail(
    assignment_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if current_user.role == models.UserRole.STUDENT:
        if assignment.class_id != current_user.student_class_id:
             raise HTTPException(status_code=403, detail="You can't see this assignment")

    return assignment
