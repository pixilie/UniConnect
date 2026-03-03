import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
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

class MessageType(str, enum.Enum):
    STANDARD = "standard"
    ANNOUNCEMENT = "announcement"

class EventType(str, enum.Enum):
    STUDY = "study_session"
    ACTIVITY = "activity"

class ResourceCategory(str, enum.Enum):
    LECTURE = "lecture"
    EXERCISE = "exercise"
    PROJECT = "project"
    OTHER = "other"


# --- TABLES DEFINITION ---
teacher_groups_association = Table(
    "teacher_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    schedule_path: Mapped[str | None] = mapped_column()

    students = relationship("User", back_populates="student_group")
    teachers = relationship("User", secondary=teacher_groups_association, back_populates="teaching_groups")
    messages = relationship("Message", back_populates="group")
    events = relationship("Event", back_populates="group")
    assignments = relationship("Assignment", back_populates="group")
    resources = relationship("Resource", back_populates="group")
    elections = relationship("Election", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDENT)
    student_group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))

    student_group = relationship("Group", back_populates="students", foreign_keys=[student_group_id])
    teaching_groups = relationship("Group", secondary=teacher_groups_association, back_populates="teachers")
    messages = relationship("Message", back_populates="author")
    created_events = relationship("Event", back_populates="creator")
    created_assignments = relationship("Assignment", back_populates="creator")
    uploaded_resources = relationship("Resource", back_populates="uploader")
    votes = relationship("Vote", back_populates="voter")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(default=MessageType.STANDARD)
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


class Election(Base):
    __tablename__ = "elections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))

    group = relationship("Group", back_populates="elections")
    candidates = relationship("Candidate", back_populates="election")
    votes = relationship("Vote", back_populates="election")


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    manifesto: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column()

    election_id: Mapped[int | None] = mapped_column(ForeignKey("elections.id"))

    election = relationship("Election", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    voted_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    election_id: Mapped[int | None] = mapped_column(ForeignKey("elections.id"))
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"))

    voter = relationship("User", back_populates="votes")
    election = relationship("Election", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

    __table_args__ = (
        UniqueConstraint('user_id', 'election_id', name='unique_user_vote_per_election'),
    )
