from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import Announcement, Group

announcement_router = APIRouter()

@announcement_router.get("/groups/{group_id}/announcement", response_model=List[schemas.Announcement])
def get_announcements(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_group_ids = [g.id for g in current_user.groups]

    if current_user.role != models.UserRole.ADMIN:
        if group_id not in current_group_ids:
            raise HTTPException(status_code=403, detail="You can't access announcements from a group you're not part of")

    group_exist = db.query(Group).filter(models.User.groups.any(models.Group.id.in_(current_group_ids))).first()

    if not group_exist:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    return db.query(Announcement).filter(Announcement.group_id == group_id).all()

@announcement_router.post("/groups/{group_id}/announcement", response_model=schemas.Announcement)
def create_announcements(
    group_id: int,
    new_annoucement_data: schemas.NewAnnoucement,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_group_ids = [g.id for g in current_user.groups]

    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER, models.UserRole.DELEGATE]:
        raise HTTPException(status_code=403, detail="You are not allowed to create annoucements in this group")

    if group_id not in current_group_ids and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can't create announcements in a group you're not part of")

    group_exist = db.query(Group).filter(models.User.groups.any(models.Group.id.in_(current_group_ids))).first()

    if not group_exist:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    new_annoucement = models.Announcement(
        title = new_annoucement_data.title,
        content = new_annoucement_data.content,
        sent_at = datetime.now(timezone.utc),
        user_id = current_user.id,
        group_id = group_id,
        urgent = new_annoucement_data.urgent,
    )

    db.add(new_annoucement)
    db.commit()
    db.refresh(new_annoucement)

    return new_annoucement

@announcement_router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    annoucement = db.query(Announcement).filter(Announcement.id == announcement_id).first()

    if not annoucement:
        raise HTTPException(status_code=404, detail=f"Announcement {announcement_id} not found")

    current_group_ids = [g.id for g in current_user.groups]

    if annoucement.group_id not in current_group_ids and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can't delete an announcement in a group you're not part of")

    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER, models.UserRole.DELEGATE] and current_user.id != annoucement.user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete annoucements in this group")

    db.delete(annoucement)
    db.commit()

    return None
