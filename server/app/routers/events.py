from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import event_schemas
from app.services import geocoding

events_router = APIRouter()

@events_router.post("/events/group_id={group_id}", response_model=event_schemas.Event)
def create_event(
    group_id: int,
    event_data: event_schemas.NewEvent,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    (address, latitude, longitude) = geocoding.get_coordinates(event_data.location)

    new_event = models.Event(
        title = event_data.title,
        description = event_data.desription,
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

@events_router.delete("/events/event_id={event_id}/")
def delete_event(
    event_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.id != event.creator_id and current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only delete the event you created")

    db.delete(event)
    db.commit()

    return {"message": "Event succesfully deleted"}

@events_router.patch("/events/event_id={event_id}", response_model=event_schemas.Event)
def update_event(
    event_id: int,
    event_data: event_schemas.UpdateEvent,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.id != event.creator_id and current_user.role != models.UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update the event you created")

    updated_data = event_data.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(event, key, value)

    if event_data.location:
        (address, latitude, longitude) = geocoding.get_coordinates(event_data.location)
        event.location = address
        event.latitude = latitude
        event.longitude = longitude

    db.commit()
    db.refresh(event)

    return event

@events_router.get("/events/event_id={event_id}", response_model=List[event_schemas.Event])
def get_event(
    event_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Event)

    if event_id:
        query = query.filter(models.Event.id == event_id)

    return query.offset(skip).limit(limit).all()
