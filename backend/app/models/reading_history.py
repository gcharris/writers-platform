from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class ReadingHistory(Base):
    __tablename__ = "reading_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    read_time = Column(Integer, default=0)  # Total reading time in seconds
    progress = Column(Integer, default=100)  # Completion percentage (default 100 for completed)

    # Relationships
    user = relationship("User", back_populates="reading_history")
    work = relationship("Work", back_populates="reading_history")

    class Config:
        from_attributes = True
