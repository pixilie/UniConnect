import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    schedule_path = Column(String, nullable=True)

    students = relationship("User", back_populates="student_group")
    teachers = relationship("User", secondary=teacher_groups_association, back_populates="teaching_groups")
    messages = relationship("Message", back_populates="group")
    events = relationship("Event", back_populates="group")
    assignments = relationship("Assignment", back_populates="group")

    resources = relationship("Resource", back_populates="group")
    elections = relationship("Election", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.STUDENT)
    student_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    student_group = relationship("Group", back_populates="students", foreign_keys=[student_group_id])
    teaching_groups = relationship("Group", secondary=teacher_groups_association, back_populates="teachers")
    messages = relationship("Message", back_populates="author")
    created_events = relationship("Event", back_populates="creator")
    created_assignments = relationship("Assignment", back_populates="creator")

    uploaded_resources = relationship("Resource", back_populates="uploader")
    votes = relationship("Vote", back_populates="voter")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default=MessageType.STANDARD)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    author = relationship("User", back_populates="messages")
    group = relationship("Group", back_populates="messages")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    type =  Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    creator = relationship("User", back_populates="created_events")
    group = relationship("Group", back_populates="events")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    group_id = Column(Integer, ForeignKey("groups.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))

    group = relationship("Group", back_populates="assignments")
    creator = relationship("User", back_populates="created_assignments")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False) # Chemin local vers le fichier
    file_type = Column(String, nullable=True)  # ex: "pdf", "docx"
    category = Column(String, default=ResourceCategory.OTHER)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    uploader = relationship("User", back_populates="uploaded_resources")
    group = relationship("Group", back_populates="resources")


class Election(Base):
    __tablename__ = "elections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    group_id = Column(Integer, ForeignKey("groups.id"))

    group = relationship("Group", back_populates="elections")
    candidates = relationship("Candidate", back_populates="election")
    votes = relationship("Vote", back_populates="election")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    manifesto = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)

    election_id = Column(Integer, ForeignKey("elections.id"))

    election = relationship("Election", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    voted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    election_id = Column(Integer, ForeignKey("elections.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    voter = relationship("User", back_populates="votes")
    election = relationship("Election", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

    __table_args__ = (
        UniqueConstraint('user_id', 'election_id', name='unique_user_vote_per_election'),
    )
