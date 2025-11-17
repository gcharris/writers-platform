from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.reading_session import ReadingSession
from app.models.section import Section
from app.models.work import Work
from app.schemas.reading import (
    ReadingSessionStart,
    ReadingSessionUpdate,
    ReadingSessionComplete,
    ReadingSessionResponse,
    ReadingValidationResponse
)
from datetime import datetime
import uuid

router = APIRouter(prefix="/reading", tags=["reading"])

def calculate_reading_speed(time_seconds: int, word_count: int) -> float:
    """Calculate words per minute."""
    if time_seconds == 0:
        return 0.0
    minutes = time_seconds / 60
    return word_count / minutes

def validate_reading_session(session: ReadingSession, content_word_count: int) -> bool:
    """
    Validate if user actually read the content.

    Criteria (must pass 2 out of 3):
    1. Time: At least 70% of expected reading time (250 WPM average)
    2. Scroll: At least 80% scroll depth
    3. Speed: Reading speed between 100-500 WPM (realistic range)
    """
    # Expected reading time at 250 WPM
    min_time = (content_word_count / 250) * 60 * 0.7  # 70% of expected

    criteria = {
        "time": session.time_on_page >= min_time,
        "scroll": session.scroll_depth >= 80,
        "speed": session.reading_speed and 100 <= session.reading_speed <= 500
    }

    # Must pass 2 out of 3 criteria
    return sum(criteria.values()) >= 2

@router.post("/start", response_model=ReadingSessionResponse)
async def start_reading_session(
    data: ReadingSessionStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new reading session."""

    # Check if session already exists
    existing = db.query(ReadingSession).filter(
        and_(
            ReadingSession.user_id == current_user.id,
            ReadingSession.work_id == data.work_id,
            ReadingSession.section_id == data.section_id
        )
    ).first()

    if existing:
        return existing

    # Create new session
    session = ReadingSession(
        user_id=current_user.id,
        work_id=data.work_id,
        section_id=data.section_id,
        started_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

@router.put("/{session_id}/update", response_model=ReadingSessionResponse)
async def update_reading_session(
    session_id: uuid.UUID,
    data: ReadingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading metrics (called periodically by frontend)."""

    session = db.query(ReadingSession).filter(
        and_(
            ReadingSession.id == session_id,
            ReadingSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Reading session not found")

    # Update metrics
    session.time_on_page = data.time_on_page
    session.scroll_depth = data.scroll_depth

    # Track scroll events
    if data.scroll_event:
        events = session.scroll_events or []
        events.append(data.scroll_event.isoformat())
        session.scroll_events = events

    db.commit()
    db.refresh(session)

    return session

@router.post("/{session_id}/complete", response_model=ReadingValidationResponse)
async def complete_reading_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete reading session and validate engagement."""

    session = db.query(ReadingSession).filter(
        and_(
            ReadingSession.id == session_id,
            ReadingSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Reading session not found")

    # Get content word count
    if session.section_id:
        section = db.query(Section).filter(Section.id == session.section_id).first()
        word_count = section.word_count if section else 0
    else:
        work = db.query(Work).filter(Work.id == session.work_id).first()
        word_count = work.word_count if work else 0

    # Calculate reading speed
    if session.time_on_page > 0:
        session.reading_speed = calculate_reading_speed(session.time_on_page, word_count)

    # Mark as completed
    session.completed = True
    session.ended_at = datetime.utcnow()

    # Validate reading
    session.validated = validate_reading_session(session, word_count)

    db.commit()
    db.refresh(session)

    # Check if user can comment/rate
    can_comment = session.validated
    can_rate = check_can_rate(current_user.id, session.work_id, db)

    message = "Reading validated! You can now comment." if session.validated else \
              "Please read more carefully to unlock commenting."

    return ReadingValidationResponse(
        validated=session.validated,
        can_comment=can_comment,
        can_rate=can_rate,
        message=message
    )

def check_can_rate(user_id: uuid.UUID, work_id: uuid.UUID, db: Session) -> bool:
    """Check if user has read all sections and can rate the work."""

    # Get all sections for work
    sections = db.query(Section).filter(Section.work_id == work_id).all()

    if not sections:
        # No sections, check if user validated reading the main work
        session = db.query(ReadingSession).filter(
            and_(
                ReadingSession.user_id == user_id,
                ReadingSession.work_id == work_id,
                ReadingSession.section_id == None,
                ReadingSession.validated == True
            )
        ).first()
        return session is not None

    # Check if user has validated sessions for all sections
    validated_sessions = db.query(ReadingSession).filter(
        and_(
            ReadingSession.user_id == user_id,
            ReadingSession.work_id == work_id,
            ReadingSession.validated == True
        )
    ).all()

    validated_section_ids = {s.section_id for s in validated_sessions}
    required_section_ids = {s.id for s in sections}

    return required_section_ids.issubset(validated_section_ids)

@router.get("/validation/{work_id}", response_model=ReadingValidationResponse)
async def check_reading_validation(
    work_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can comment/rate a work."""

    # Check for any validated session
    validated_session = db.query(ReadingSession).filter(
        and_(
            ReadingSession.user_id == current_user.id,
            ReadingSession.work_id == work_id,
            ReadingSession.validated == True
        )
    ).first()

    can_comment = validated_session is not None
    can_rate = check_can_rate(current_user.id, work_id, db)

    if can_rate:
        message = "You can comment and rate this work!"
    elif can_comment:
        message = "You can comment. Read all sections to unlock rating."
    else:
        message = "Read the work to unlock commenting and rating."

    return ReadingValidationResponse(
        validated=can_comment,
        can_comment=can_comment,
        can_rate=can_rate,
        message=message
    )
