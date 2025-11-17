from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="writer")
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Sprint 3: Profile fields
    location = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)

    # Sprint 3: Engagement stats
    works_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    works = relationship("Work", back_populates="author")
    reading_sessions = relationship("ReadingSession", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    ratings = relationship("Rating", back_populates="user")

    # Sprint 3: Discovery relationships
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    reading_history = relationship("ReadingHistory", back_populates="user", cascade="all, delete-orphan")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan")

    # Sprint 4: Notifications and community
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user", cascade="all, delete-orphan")
    reading_lists = relationship("ReadingList", back_populates="user", cascade="all, delete-orphan")

    # Sprint 5: Professional accounts
    professional_profile = relationship("ProfessionalProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
