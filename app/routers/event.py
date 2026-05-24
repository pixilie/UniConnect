from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user
from app.db.database import get_db
from app.services.geocoding import get_coordinates

events_router = APIRouter()


@events_router.get("/events", response_model=List[schemas.Event])
def get_event(
    event_id: Optional[int] = None,
    group_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        query = query.filter(models.Event.group_id.in_(current_group_ids))

    if event_id:
        query = query.filter(models.Event.id == event_id)
        if not query.first():
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    if group_id:
        query = query.filter(models.Event.group_id == group_id)
        if not query.first() and not event_id:
            pass

    return query.offset(skip).limit(limit).all()


@events_router.post("/groups/{group_id}/events", response_model=schemas.Event)
def create_event(
    group_id: int,
    event_data: schemas.NewEvent,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this group"
            )

    if (
        current_user.role == models.UserRole.STUDENT
        and current_user.role == models.UserRole.DELEGATE
        and event_data.type != models.EventType.ACTIVITY
    ):
        raise HTTPException(
            status_code=403, detail="Students can only create events of type ACTIVITY."
        )

    if event_data.title.strip() == "":
        raise HTTPException(
            status_code=422, detail="You can't create event with an empty title"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if event_data.location:
        address, latitude, longitude = get_coordinates(event_data.location)
    else:
        event_data.location = "TBD"

    new_event = models.Event(
        title=event_data.title,
        description=getattr(event_data, "description", None),
        start=event_data.start,
        end=event_data.end,
        location=event_data.location,
        type=event_data.type,
        creator_id=current_user.id,
        group_id=group_id,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@events_router.patch("/events/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int,
    event_data: schemas.UpdateEvent,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if (
        current_user.id != event.creator_id
        and current_user.role != models.UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=403, detail="You can only update events you created"
        )

    updated_data = event_data.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        if key != "location":
            setattr(event, key, value)

    if event_data.location:
        event.location = event_data.location

    db.commit()
    db.refresh(event)

    return event


@events_router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    if (
        current_user.id != event.creator_id
        and current_user.role != models.UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=403, detail="You can only delete events you created"
        )

    db.delete(event)
    db.commit()

    return None
