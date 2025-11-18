from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Badge(Base):
    """
    Badge Model

    Represents authenticity and analysis badges for works published to Community.

    Badge Types:
    - ai_analyzed: Work analyzed by Factory engine
    - human_verified: AI detection confirmed human authorship
    - human_self: User self-declared human authorship
    - community_upload: Direct upload to Community (no Factory analysis)
    """
    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)

    # Badge type
    badge_type = Column(String(50), nullable=False)

    # Verification status
    verified = Column(Boolean, default=False)

    # Metadata (stores additional info like confidence scores, analysis IDs, etc.)
    metadata_json = Column(JSON, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    work = relationship("Work", back_populates="badges")

    def __repr__(self):
        return f"<Badge {self.badge_type} for work {self.work_id}>"
