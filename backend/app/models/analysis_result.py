from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class AnalysisResult(Base):
    """
    Analysis Result Model

    Stores results from Factory AI analysis (tournament results).
    Each analysis run creates one record with complete tournament data.
    """
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scene_id = Column(UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=True)

    # Analysis status: pending, running, completed, failed
    status = Column(String(20), default="pending")

    # Tournament metadata
    scene_outline = Column(Text, nullable=True)
    chapter_identifier = Column(String(50), nullable=True)

    # Results (JSON from tournament.py)
    results_json = Column(JSON, nullable=True)  # Complete tournament results

    # Quick access fields
    best_agent = Column(String(50), nullable=True)
    best_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)

    # Error info
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="analysis_results")
    scene = relationship("Scene", backref="analysis_results")
