from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class ReadingList(Base):
    __tablename__ = "reading_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    visibility = Column(String(20), default="private")  # 'private', 'public'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reading_lists")
    items = relationship("ReadingListItem", back_populates="reading_list", cascade="all, delete-orphan")

    class Config:
        from_attributes = True

class ReadingListItem(Base):
    __tablename__ = "reading_list_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reading_list_id = Column(UUID(as_uuid=True), ForeignKey("reading_lists.id", ondelete="CASCADE"), nullable=False)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)

    order_index = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reading_list = relationship("ReadingList", back_populates="items")
    work = relationship("Work")

    # Ensure unique work per list
    __table_args__ = (
        UniqueConstraint('reading_list_id', 'work_id', name='unique_reading_list_work'),
    )

    class Config:
        from_attributes = True
