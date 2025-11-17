"""
AI Analysis Routes
==================

Wraps the Factory engine (backend/engine/) for AI analysis.

TODO (for Claude Cloud Agent):
- Trigger analysis on project (calls engine/orchestration/tournament.py)
- Get analysis status (running/completed)
- Get analysis results
- List available AI models
- Configure analysis parameters
"""

from fastapi import APIRouter

router = APIRouter(tags=["analysis"])

# Placeholder - Claude Cloud Agent will implement these endpoints
# Will import from: backend.engine.orchestration.tournament
