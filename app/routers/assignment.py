from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user
from app.db.database import get_db

assignment_router = APIRouter()

@assignment_router.get("/groups/{group_id}/assignments", response_model=List[schemas.Assignment])
def get_assignments(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(status_code=403, detail="You can't access assignments from a group you're not part of")

    query = db.query(models.Assignment).filter(models.Assignment.group_id == group_id)

    return query.order_by(models.Assignment.due_date.asc()).offset(skip).limit(limit).all()


@assignment_router.get("/assignments/{assignment_id}", response_model=schemas.Assignment)
def get_assignment_detail(
    assignment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if assignment.group_id not in current_group_ids:
             raise HTTPException(status_code=403, detail="You don't belong the group this assignment has been assigned to")

    return assignment


@assignment_router.post("/groups/{group_id}/assignments", response_model=schemas.Assignment)
def new_assignments(
    group_id: int,
    assignment_data: schemas.NewAssignment,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only administrators/teachers can post new assignments")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(status_code=403, detail="Not authorized to access this group")

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


@assignment_router.patch("/assignments/{assignment_id}", response_model=schemas.Assignment)
def update_assignment(
    assignment_id: int,
    update: schemas.UpdateAssignment,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only administrators/teachers can update an assignment")

    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if current_user.role != models.UserRole.ADMIN and assignment.creator_id != current_user.id:
         raise HTTPException(status_code=403, detail="You can't modify this assignment because you don't created it")

    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(assignment, key, value)

    db.commit()
    db.refresh(assignment)

    return assignment


@assignment_router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only administrator/teachers can delete an assigment")

    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if current_user.role != models.UserRole.ADMIN and assignment.creator_id != current_user.id:
         raise HTTPException(status_code=403, detail="You can't remove this assignment because you don't created it")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment succesfuly deleted"}
