from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Scene(Base):
    """
    Scene Model

    Represents a scene or chapter within a Factory project.
    Scenes are analyzed by the Factory engine and can have multiple variations.
    """
    __tablename__ = "scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Scene content
    content = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)

    # Scene structure
    chapter_number = Column(Integer, nullable=True)  # e.g., 1, 2, 3
    scene_number = Column(Integer, nullable=True)    # e.g., 1, 2, 3 within chapter
    sequence = Column(Integer, nullable=False)       # Overall sequence in project

    # Metadata
    word_count = Column(Integer, default=0)

    # Scene type: original, variation, hybrid
    scene_type = Column(String(20), default="original")

    # If this is a variation/hybrid, link to parent scene
    parent_scene_id = Column(UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="scenes")
    parent_scene = relationship("Scene", remote_side=[id], backref="variations")
