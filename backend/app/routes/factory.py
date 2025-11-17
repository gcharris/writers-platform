from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/factory", tags=["factory"])

# Schemas for Writers Factory API integration
class FactorySubmissionRequest(BaseModel):
    work_id: str
    event_id: str
    pitch: str

class FactorySubmissionResponse(BaseModel):
    submission_id: str
    status: str
    message: str

    class Config:
        from_attributes = True

class FactoryEventResponse(BaseModel):
    event_id: str
    name: str
    type: str
    description: str
    deadline: str
    entry_fee: float
    prizes: List[str]

    class Config:
        from_attributes = True

# Get available Writers Factory events
@router.get("/events", response_model=List[FactoryEventResponse])
async def get_factory_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available events from Writers Factory API.

    This is a stub endpoint for future integration with the external Writers Factory API.
    In production, this would make an authenticated API call to retrieve live events.
    """
    # TODO: Integrate with Writers Factory API
    # For now, return empty list
    return []

# Submit work to Writers Factory event
@router.post("/submit", response_model=FactorySubmissionResponse)
async def submit_to_factory(
    data: FactorySubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a work to a Writers Factory event.

    This is a stub endpoint for future integration with the external Writers Factory API.
    In production, this would:
    1. Validate the work belongs to the user
    2. Make an authenticated API call to Writers Factory
    3. Track submission status locally
    4. Return confirmation
    """
    # TODO: Integrate with Writers Factory API
    raise HTTPException(
        status_code=501,
        detail="Writers Factory integration is not yet implemented. Coming soon!"
    )

# Get submission status from Writers Factory
@router.get("/submissions/{submission_id}")
async def get_factory_submission_status(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a Writers Factory submission.

    This is a stub endpoint for future integration with the external Writers Factory API.
    """
    # TODO: Integrate with Writers Factory API
    raise HTTPException(
        status_code=501,
        detail="Writers Factory integration is not yet implemented. Coming soon!"
    )

# Get user's Writers Factory submission history
@router.get("/my-submissions")
async def get_my_factory_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all of the current user's Writers Factory submissions.

    This is a stub endpoint for future integration with the external Writers Factory API.
    """
    # TODO: Integrate with Writers Factory API
    return []
