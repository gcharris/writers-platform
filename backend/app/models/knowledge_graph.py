"""
SQLAlchemy models for knowledge graph persistence.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ProjectGraph(Base):
    """
    Stores serialized knowledge graph for each project.
    Main persistence mechanism for NetworkX graphs.
    """
    __tablename__ = "project_graphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Serialized NetworkX graph (full graph as JSON)
    graph_data = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_extracted_scene = Column(UUID(as_uuid=True), nullable=True)

    # Statistics
    entity_count = Column(Integer, default=0)
    relationship_count = Column(Integer, default=0)
    scene_count = Column(Integer, default=0)

    # Extraction stats
    total_extractions = Column(Integer, default=0)
    successful_extractions = Column(Integer, default=0)
    failed_extractions = Column(Integer, default=0)

    # Relationship to project
    project = relationship("Project", back_populates="knowledge_graph")


class ExtractionJob(Base):
    """
    Tracks entity/relationship extraction jobs.
    Useful for monitoring and debugging.
    """
    __tablename__ = "extraction_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('manuscript_scenes.id', ondelete='CASCADE'), nullable=False)

    # Job info
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    extractor_type = Column(String(20), nullable=False)  # llm, ner, hybrid
    model_name = Column(String(50), nullable=True)  # claude-sonnet-4.5, spacy, etc.

    # Results
    entities_extracted = Column(Integer, default=0)
    relationships_extracted = Column(Integer, default=0)

    # Timing
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Cost tracking (for LLM extraction)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
