"""
Factory Orchestrator Service
=============================

Wraps backend/engine/orchestration/tournament.py for web API use.
Provides async job management for long-running AI analyses.
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

# Add engine to path so we can import tournament
# In Railway deployment: __file__ is /app/app/services/orchestrator.py
# parent.parent.parent is /app
# So this adds /app/engine to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))

from orchestration.tournament import TournamentOrchestrator

from app.models.project import Project
from app.models.scene import Scene
from app.models.analysis_result import AnalysisResult


class FactoryOrchestrator:
    """
    Wraps TournamentOrchestrator for web API use.

    Manages background analysis jobs and tracks results in database.
    """

    def __init__(self, db: Session):
        """
        Initialize orchestrator.

        Args:
            db: Database session
        """
        self.db = db

    async def run_analysis(
        self,
        project_id: uuid.UUID,
        scene_id: Optional[uuid.UUID] = None,
        scene_outline: Optional[str] = None,
        chapter: Optional[str] = None,
        context_requirements: Optional[List[str]] = None,
        agents: Optional[List[str]] = None,
        synthesize: bool = True
    ) -> uuid.UUID:
        """
        Start AI analysis job.

        Args:
            project_id: Project UUID
            scene_id: Optional scene UUID (if analyzing specific scene)
            scene_outline: Scene description/outline
            chapter: Chapter identifier (e.g., "2.3.6")
            context_requirements: Required context (characters, worldbuilding)
            agents: List of agent names (defaults to all 5)
            synthesize: Whether to synthesize hybrid scene

        Returns:
            AnalysisResult UUID (job ID)
        """
        # Create analysis result record (status: pending)
        analysis = AnalysisResult(
            project_id=project_id,
            scene_id=scene_id,
            status="pending",
            scene_outline=scene_outline,
            chapter_identifier=chapter
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        # Return job ID immediately (analysis runs in background)
        return analysis.id

    def run_analysis_sync(
        self,
        analysis_id: uuid.UUID,
        scene_outline: str,
        chapter: Optional[str] = None,
        context_requirements: Optional[List[str]] = None,
        agents: Optional[List[str]] = None,
        synthesize: bool = True
    ):
        """
        Run analysis synchronously (called by background task).

        Updates database with results when complete.

        Args:
            analysis_id: AnalysisResult UUID
            scene_outline: Scene description
            chapter: Chapter identifier
            context_requirements: Required context
            agents: List of agent names
            synthesize: Whether to synthesize hybrid
        """
        # Get analysis record
        analysis = self.db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            print(f"Error: Analysis {analysis_id} not found")
            return

        try:
            # Update status to running
            analysis.status = "running"
            analysis.started_at = datetime.utcnow()
            self.db.commit()

            # Initialize tournament orchestrator
            # Note: This uses credentials from environment or credentials.json
            orchestrator = TournamentOrchestrator(
                project_name="Writers-Platform",
                synthesis_threshold=7.0,
                use_gemini_search=False,  # Disable for web to avoid file dependencies
                use_cognee=False
            )

            # Run tournament
            results = orchestrator.run_tournament(
                scene_outline=scene_outline,
                chapter=chapter,
                context_requirements=context_requirements,
                agents=agents,
                synthesize=synthesize,
                max_tokens=4000
            )

            # Update analysis with results
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
            analysis.results_json = results

            # Extract quick access fields
            summary = results.get('summary', {})
            analysis.best_agent = summary.get('highest_scoring')
            analysis.best_score = summary.get('highest_score')
            analysis.hybrid_score = summary.get('hybrid_score')
            analysis.total_cost = summary.get('total_cost', 0.0)
            analysis.total_tokens = summary.get('total_tokens', 0)

            self.db.commit()

            print(f"✓ Analysis {analysis_id} completed successfully")
            print(f"  Best: {analysis.best_agent} ({analysis.best_score:.1f}/70)")
            if analysis.hybrid_score:
                print(f"  Hybrid: {analysis.hybrid_score:.1f}/70")

        except Exception as e:
            # Update analysis with error
            analysis.status = "failed"
            analysis.completed_at = datetime.utcnow()
            analysis.error_message = str(e)
            self.db.commit()

            print(f"✗ Analysis {analysis_id} failed: {e}")
            traceback.print_exc()

    def get_analysis_status(self, analysis_id: uuid.UUID) -> Optional[Dict]:
        """
        Get analysis job status.

        Args:
            analysis_id: AnalysisResult UUID

        Returns:
            Status dict with:
                - status: pending, running, completed, failed
                - started_at: timestamp
                - completed_at: timestamp
                - error_message: if failed
        """
        analysis = self.db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            return None

        return {
            'id': str(analysis.id),
            'status': analysis.status,
            'scene_outline': analysis.scene_outline,
            'chapter': analysis.chapter_identifier,
            'started_at': analysis.started_at.isoformat() if analysis.started_at else None,
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
            'error_message': analysis.error_message
        }

    def get_analysis_results(self, analysis_id: uuid.UUID) -> Optional[Dict]:
        """
        Get analysis results.

        Args:
            analysis_id: AnalysisResult UUID

        Returns:
            Results dict with:
                - status: completed (or error if not ready)
                - results: Full tournament results
                - summary: Quick summary (best agent, scores, etc.)
        """
        analysis = self.db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            return None

        if analysis.status != "completed":
            return {
                'status': analysis.status,
                'error': analysis.error_message if analysis.status == "failed" else None,
                'message': 'Analysis not yet complete' if analysis.status in ['pending', 'running'] else None
            }

        return {
            'status': 'completed',
            'id': str(analysis.id),
            'scene_outline': analysis.scene_outline,
            'chapter': analysis.chapter_identifier,
            'started_at': analysis.started_at.isoformat() if analysis.started_at else None,
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
            'summary': {
                'best_agent': analysis.best_agent,
                'best_score': analysis.best_score,
                'hybrid_score': analysis.hybrid_score,
                'total_cost': analysis.total_cost,
                'total_tokens': analysis.total_tokens
            },
            'full_results': analysis.results_json  # Complete tournament data
        }

    def list_project_analyses(self, project_id: uuid.UUID) -> List[Dict]:
        """
        List all analyses for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of analysis summary dicts
        """
        analyses = self.db.query(AnalysisResult).filter(
            AnalysisResult.project_id == project_id
        ).order_by(AnalysisResult.created_at.desc()).all()

        return [
            {
                'id': str(a.id),
                'status': a.status,
                'scene_outline': a.scene_outline,
                'chapter': a.chapter_identifier,
                'best_agent': a.best_agent,
                'best_score': a.best_score,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'completed_at': a.completed_at.isoformat() if a.completed_at else None
            }
            for a in analyses
        ]
