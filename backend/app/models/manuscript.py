"""
Manuscript database models for PostgreSQL.

Based on factory-core's manuscript structure but adapted for SQLAlchemy.
Replaces JSON file storage with proper relational database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.core.database import Base


class ManuscriptAct(Base):
    """Act in a manuscript (e.g., Act 1, Act 2, Act 3)"""

    __tablename__ = "manuscript_acts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    volume = Column(Integer, default=1, nullable=False)
    act_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    notes = Column(Text, default="")
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="manuscript_acts")
    chapters = relationship("ManuscriptChapter", back_populates="act", cascade="all, delete-orphan", order_by="ManuscriptChapter.chapter_number")

    @property
    def total_word_count(self) -> int:
        """Calculate total word count for all chapters in this act"""
        return sum(chapter.total_word_count for chapter in self.chapters)

    def __repr__(self):
        return f"<ManuscriptAct(id={self.id}, title='{self.title}', act_number={self.act_number})>"


class ManuscriptChapter(Base):
    """Chapter in an act"""

    __tablename__ = "manuscript_chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    act_id = Column(UUID(as_uuid=True), ForeignKey("manuscript_acts.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    notes = Column(Text, default="")
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    act = relationship("ManuscriptAct", back_populates="chapters")
    scenes = relationship("ManuscriptScene", back_populates="chapter", cascade="all, delete-orphan", order_by="ManuscriptScene.scene_number")

    @property
    def total_word_count(self) -> int:
        """Calculate total word count for all scenes in this chapter"""
        return sum(scene.word_count for scene in self.scenes)

    def __repr__(self):
        return f"<ManuscriptChapter(id={self.id}, title='{self.title}', chapter_number={self.chapter_number})>"


class ManuscriptScene(Base):
    """Scene in a chapter"""

    __tablename__ = "manuscript_scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("manuscript_chapters.id", ondelete="CASCADE"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, default="")  # The actual prose
    word_count = Column(Integer, default=0)
    notes = Column(Text, default="")
    metadata = Column(JSONB, default=dict)  # Generation context, prompts, models used, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chapter = relationship("ManuscriptChapter", back_populates="scenes")

    def update_content(self, content: str) -> None:
        """Update scene content and recalculate word count"""
        self.content = content
        self.word_count = len(content.split()) if content else 0
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<ManuscriptScene(id={self.id}, title='{self.title}', scene_number={self.scene_number}, words={self.word_count})>"


class ReferenceFile(Base):
    """Knowledge base reference files (characters, world building, plot, etc.)"""

    __tablename__ = "reference_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # 'characters', 'world_building', 'story_structure', etc.
    subcategory = Column(String(50), default="")  # 'protagonists', 'locations', 'outline', etc.
    filename = Column(String(255), nullable=False)
    content = Column(Text, default="")  # Markdown content
    word_count = Column(Integer, default=0)
    metadata = Column(JSONB, default=dict)  # Tags, source (NotebookLM URL, etc.), version info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="reference_files")

    def update_content(self, content: str) -> None:
        """Update content and recalculate word count"""
        self.content = content
        self.word_count = len(content.split()) if content else 0
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<ReferenceFile(id={self.id}, category='{self.category}', filename='{self.filename}')>"


# Update Project model to include relationships
# This would be added to the existing Project model in app/models/project.py:
#
# from sqlalchemy.orm import relationship
#
# class Project(Base):
#     # ... existing fields ...
#
#     # Add these relationships:
#     manuscript_acts = relationship("ManuscriptAct", back_populates="project", cascade="all, delete-orphan")
#     reference_files = relationship("ReferenceFile", back_populates="project", cascade="all, delete-orphan")
