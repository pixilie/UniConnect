import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# --- ENUMS DEFINITION ---
class UserRole(str, enum.Enum):
    ADMIN = "administrator"
    TEACHER = "teacher"
    DELEGATE = "delegate"
    STUDENT = "student"

class EventType(str, enum.Enum):
    STUDY = "study_session"
    ACTIVITY = "activity"

class ResourceCategory(str, enum.Enum):
    LECTURE = "lecture"
    EXERCISE = "exercise"
    PROJECT = "project"
    OTHER = "other"


# --- TABLES DEFINITION ---
user_groups_association = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    schedule_path: Mapped[str | None] = mapped_column()

    members = relationship("User", secondary=user_groups_association, back_populates="groups")
    messages = relationship("Message", back_populates="group")
    events = relationship("Event", back_populates="group")
    assignments = relationship("Assignment", back_populates="group")
    resources = relationship("Resource", back_populates="group")
    polls = relationship("Poll", back_populates="group")
    announcement = relationship("Announcement", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDENT)
    student_group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))

    groups = relationship("Group", secondary=user_groups_association, back_populates="members")
    messages = relationship("Message", back_populates="author")
    created_events = relationship("Event", back_populates="creator")
    created_assignments = relationship("Assignment", back_populates="creator")
    uploaded_resources = relationship("Resource", back_populates="uploader")
    votes = relationship("Vote", back_populates="voter")
    announcement = relationship("Announcement", back_populates="author")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))

    author = relationship("User", back_populates="messages")
    group = relationship("Group", back_populates="messages")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column()
    location: Mapped[str | None] = mapped_column()
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()
    type: Mapped[EventType] = mapped_column(default=EventType.STUDY)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))

    creator = relationship("User", back_populates="created_events")
    group = relationship("Group", back_populates="events")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    group = relationship("Group", back_populates="assignments")
    creator = relationship("User", back_populates="created_assignments")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column()
    file_type: Mapped[str | None] = mapped_column()
    category: Mapped[ResourceCategory] = mapped_column(default=ResourceCategory.OTHER)
    uploaded_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))

    uploader = relationship("User", back_populates="uploaded_resources")
    group = relationship("Group", back_populates="resources")


class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))

    group = relationship("Group", back_populates="polls")
    choices = relationship("Choice", back_populates="poll")
    votes = relationship("Vote", back_populates="poll")


class Choice(Base):
    __tablename__ = "choices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column()
    manifesto: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column()

    poll_id: Mapped[int | None] = mapped_column(ForeignKey("polls.id"))

    poll = relationship("Poll", back_populates="choices")
    votes = relationship("Vote", back_populates="choice")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    voted_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    poll_id: Mapped[int | None] = mapped_column(ForeignKey("polls.id"))
    choice_id: Mapped[int | None] = mapped_column(ForeignKey("choices.id"))

    voter = relationship("User", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")
    choice = relationship("Choice", back_populates="votes")

    __table_args__ = (
        UniqueConstraint('user_id', 'poll_id', name='unique_user_vote_per_poll'),
    )

class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    urgent: Mapped[bool] = mapped_column(Boolean)

    author = relationship("User", back_populates="announcement")
    group = relationship("Group", back_populates="announcement")
