from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Project(Base):
    """
    Factory Project Model

    Represents a writing project in the Factory workspace.
    Can be created from scratch or by uploading a file (DOCX, PDF, TXT).
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(50), nullable=True)

    # Project status: draft, analyzing, analyzed, published
    status = Column(String(20), default="draft")

    # Metadata
    word_count = Column(Integer, default=0)
    scene_count = Column(Integer, default=0)

    # File info (if uploaded)
    original_filename = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)  # Cloud storage path

    # Settings
    settings = Column(JSON, default={})  # Project-specific settings

    # NotebookLM Integration (Phase 9) - TODO: Add these columns via migration
    # notebooklm_notebooks = Column(JSON, default=dict, nullable=True)
    # Structure: {"character_research": "url", "world_building": "url", "themes": "url"}

    # notebooklm_config = Column(JSON, default=dict, nullable=True)
    # Structure: {"enabled": bool, "auto_query_on_copilot": bool, "configured_at": str}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="projects")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="project", cascade="all, delete-orphan")

    # Manuscript structure (from factory-core integration)
    manuscript_acts = relationship("ManuscriptAct", back_populates="project", cascade="all, delete-orphan", order_by="ManuscriptAct.act_number")
    reference_files = relationship("ReferenceFile", back_populates="project", cascade="all, delete-orphan")

    # Knowledge Graph
    knowledge_graph = relationship("ProjectGraph", back_populates="project", uselist=False, cascade="all, delete-orphan")
