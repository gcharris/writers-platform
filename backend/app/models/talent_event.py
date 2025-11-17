from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class TalentEvent(Base):
    __tablename__ = "talent_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # 'contest', 'showcase', 'pitch_event'

    genres = Column(ARRAY(Text), nullable=True)
    entry_requirements = Column(JSONB, nullable=True)  # min_word_count, max_word_count, etc.

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    winners_announced = Column(DateTime, nullable=True)

    status = Column(String(50), default="upcoming")  # 'upcoming', 'open', 'closed', 'completed'

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    entries = relationship("EventEntry", back_populates="event", cascade="all, delete-orphan")

    class Config:
        from_attributes = True

class EventEntry(Base):
    __tablename__ = "event_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("talent_events.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    entry_notes = Column(Text, nullable=True)

    # Results
    placement = Column(Integer, nullable=True)  # 1st, 2nd, 3rd, etc.
    awarded_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("TalentEvent", back_populates="entries")
    work = relationship("Work")
    author = relationship("User")

    # Ensure unique work per event
    __table_args__ = (
        UniqueConstraint('event_id', 'work_id', name='unique_event_work'),
    )

    class Config:
        from_attributes = True
