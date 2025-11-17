from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    type = Column(String(50), nullable=False)  # 'agent', 'editor', 'publisher'
    company = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    specialties = Column(ARRAY(Text), nullable=True)
    bio = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)

    # Search preferences
    seeking_genres = Column(ARRAY(Text), nullable=True)
    min_word_count = Column(Integer, nullable=True)
    max_word_count = Column(Integer, nullable=True)
    min_rating = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="professional_profile")
    submissions = relationship("Submission", back_populates="professional", cascade="all, delete-orphan")

    class Config:
        from_attributes = True

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    professional_id = Column(UUID(as_uuid=True), ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False)

    status = Column(String(50), default="pending")  # 'pending', 'reviewing', 'accepted', 'declined'
    message = Column(Text, nullable=True)  # Writer's pitch
    response = Column(Text, nullable=True)  # Professional's response

    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    work = relationship("Work")
    author = relationship("User", foreign_keys=[author_id])
    professional = relationship("ProfessionalProfile", back_populates="submissions")

    class Config:
        from_attributes = True
