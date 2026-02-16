import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


# Enums definition
class UserRole(str, enum.Enum):
    ADMIN = "Administrator"
    TEACHER = "Teacher"
    CLASS_REPR = "Class Representative"
    STUDENT = "Student"

class MessageType(str, enum.Enum):
    STANDARD = "Standard"
    ANNOUNCEMENT = "Announcement"


# Tables definition
class ClassGroup(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    schedule_path = Column(String, nullable=True)

    users = relationship("User", back_populates="class_group")
    messages = relationship("Message", back_populates="class_group")
    events = relationship("StudyEvent", back_populates="class_group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(
        String, default=UserRole.STUDENT
    )

    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    class_group = relationship("ClassGroup", back_populates="users")
    messages = relationship("Message", back_populates="author")
    created_events = relationship("StudyEvent", back_populates="creator")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default=MessageType.STANDARD)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    author = relationship("User", back_populates="messages")
    class_group = relationship("ClassGroup", back_populates="messages")


class StudyEvent(Base):
    __tablename__ = "study_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)

    creator_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    creator = relationship("User", back_populates="created_events")
    class_group = relationship("ClassGroup", back_populates="events")
