from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user
from app.db.database import get_db

poll_router = APIRouter(tags=["Polls"])


@poll_router.get("/groups/{group_id}/polls", response_model=List[schemas.PollResponse])
def get_polls(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this group"
            )

    polls = db.query(models.Poll).filter(models.Poll.group_id == group_id).all()

    if not polls:
        return []

    poll_ids = [poll.id for poll in polls]

    user_votes = (
        db.query(models.Vote.poll_id, models.Vote.choice_id)
        .filter(
            models.Vote.user_id == current_user.id, models.Vote.poll_id.in_(poll_ids)
        )
        .all()
    )

    voted_polls_map = {vote[0]: vote[1] for vote in user_votes}

    response_polls = []
    for poll in polls:
        poll_dict = {
            "id": poll.id,
            "title": poll.title,
            "is_active": poll.is_active,
            "choices": poll.choices,
            "expires_at": poll.expires_at,
            "created_at": poll.created_at,
            "group_id": poll.group_id,
            "has_voted": poll.id in voted_polls_map,
            "choice_selected": voted_polls_map.get(poll.id, -1),
        }
        response_polls.append(poll_dict)

    return response_polls


@poll_router.post("/groups/{group_id}/polls", response_model=schemas.PollResponse)
def create_poll(
    group_id: int,
    poll_data: schemas.PollCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role is models.UserRole.STUDENT:
        raise HTTPException(
            status_code=403, detail="You're not allowed to create polls"
        )

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this group"
            )

    if poll_data.title.strip() == "":
        raise HTTPException(
            status_code=422, detail="You can't create a poll with an empty title"
        )

    if poll_data.end_datetime < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=422, detail="You can't create a poll with an expired end date"
        )

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    new_poll = models.Poll(
        title=poll_data.title,
        group_id=group_id,
        user_id=current_user.id,
        expires_at=poll_data.end_datetime,
    )

    db.add(new_poll)
    db.commit()
    db.refresh(new_poll)

    new_poll.has_voted = False
    new_poll.choice_selected = -1

    return new_poll


@poll_router.post("/polls/{poll_id}/choices", response_model=schemas.ChoiceResponse)
def add_choice_to_poll(
    poll_id: int,
    choice_data: schemas.ChoiceBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=f"Poll {poll_id} not found")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if poll.group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this poll"
            )

    if not poll.is_active:
        raise HTTPException(
            status_code=400, detail="Cannot add choices to a closed poll"
        )

    if choice_data.text.strip() == "":
        raise HTTPException(status_code=422, detail="Cannot add empty choice to a poll")

    new_choice = models.Choice(**choice_data.model_dump(), poll_id=poll_id)
    db.add(new_choice)
    db.commit()
    db.refresh(new_choice)
    return new_choice


@poll_router.post("/polls/{poll_id}/vote", status_code=status.HTTP_201_CREATED)
def vote_for_choice(
    poll_id: int,
    choice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=f"Poll {poll_id} not found")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if poll.group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this poll"
            )

    if not poll.is_active:
        raise HTTPException(status_code=400, detail="This poll is closed")

    choice = (
        db.query(models.Choice)
        .filter(models.Choice.id == choice_id, models.Choice.poll_id == poll_id)
        .first()
    )
    if not choice:
        raise HTTPException(status_code=404, detail="Choice not found in this poll")

    existing_vote = (
        db.query(models.Vote)
        .filter(models.Vote.poll_id == poll_id, models.Vote.user_id == current_user.id)
        .first()
    )

    if existing_vote:
        raise HTTPException(
            status_code=400, detail="You have already voted in this poll"
        )

    new_vote = models.Vote(
        user_id=current_user.id, poll_id=poll_id, choice_id=choice_id
    )
    db.add(new_vote)
    db.commit()

    return {"message": "Vote recorded successfully"}


@poll_router.get("/polls/{poll_id}/results", response_model=schemas.PollResultResponse)
def get_poll_results(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    poll = db.query(models.Poll).filter(models.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if poll.group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this poll"
            )

    total_votes = db.query(models.Vote).filter(models.Vote.poll_id == poll_id).count()

    results = []
    for choice in poll.choices:
        vote_count = (
            db.query(models.Vote).filter(models.Vote.choice_id == choice.id).count()
        )

        choice_data = schemas.ChoiceResult(
            id=choice.id,
            text=choice.text,
            manifesto=choice.manifesto,
            photo_url=choice.photo_url,
            vote_count=vote_count,
        )
        results.append(choice_data)

    return schemas.PollResultResponse(
        poll_id=poll.id,
        title=poll.title,
        is_active=poll.is_active,
        total_votes=total_votes,
        results=results,
    )
