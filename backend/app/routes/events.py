from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.talent_event import TalentEvent, EventEntry
from app.models.work import Work
from pydantic import BaseModel

router = APIRouter(prefix="/events", tags=["events"])

# Schemas
class TalentEventCreate(BaseModel):
    name: str
    description: str
    type: str  # 'contest', 'showcase', 'pitch_event'
    genres: Optional[List[str]] = None
    start_date: datetime
    end_date: datetime
    entry_requirements: Optional[dict] = None

class TalentEventResponse(BaseModel):
    id: str
    name: str
    description: str
    type: str
    genres: Optional[List[str]]
    start_date: datetime
    end_date: datetime
    entry_requirements: Optional[dict]
    status: str
    entry_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class EventEntryCreate(BaseModel):
    work_id: str

class EventEntryResponse(BaseModel):
    id: str
    event_id: str
    work_id: str
    user_id: str
    placement: Optional[int]
    submitted_at: datetime
    work_title: Optional[str]
    author_username: Optional[str]

    class Config:
        from_attributes = True

# List all talent events
@router.get("/", response_model=List[TalentEventResponse])
async def list_events(
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        TalentEvent,
        func.count(EventEntry.id).label('entry_count')
    ).outerjoin(EventEntry, TalentEvent.id == EventEntry.event_id)

    if type:
        query = query.filter(TalentEvent.type == type)

    if status:
        query = query.filter(TalentEvent.status == status)

    query = query.group_by(TalentEvent.id).order_by(TalentEvent.start_date.desc())

    events = query.all()

    return [
        TalentEventResponse(
            id=str(event.id),
            name=event.name,
            description=event.description,
            type=event.type,
            genres=event.genres,
            start_date=event.start_date,
            end_date=event.end_date,
            entry_requirements=event.entry_requirements,
            status=event.status,
            entry_count=entry_count,
            created_at=event.created_at
        )
        for event, entry_count in events
    ]

# Get single event
@router.get("/{event_id}", response_model=TalentEventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    event = db.query(TalentEvent).filter(TalentEvent.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    entry_count = db.query(func.count(EventEntry.id)).filter(
        EventEntry.event_id == event_id
    ).scalar()

    return TalentEventResponse(
        id=str(event.id),
        name=event.name,
        description=event.description,
        type=event.type,
        genres=event.genres,
        start_date=event.start_date,
        end_date=event.end_date,
        entry_requirements=event.entry_requirements,
        status=event.status,
        entry_count=entry_count or 0,
        created_at=event.created_at
    )

# Create event (admin only - for now just requires authentication)
@router.post("/", response_model=TalentEventResponse)
async def create_event(
    data: TalentEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: Add admin role check
    event = TalentEvent(
        name=data.name,
        description=data.description,
        type=data.type,
        genres=data.genres,
        start_date=data.start_date,
        end_date=data.end_date,
        entry_requirements=data.entry_requirements,
        status="upcoming"
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return TalentEventResponse(
        id=str(event.id),
        name=event.name,
        description=event.description,
        type=event.type,
        genres=event.genres,
        start_date=event.start_date,
        end_date=event.end_date,
        entry_requirements=event.entry_requirements,
        status=event.status,
        entry_count=0,
        created_at=event.created_at
    )

# Enter event
@router.post("/{event_id}/enter", response_model=EventEntryResponse)
async def enter_event(
    event_id: UUID,
    data: EventEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify event exists and is active
    event = db.query(TalentEvent).filter(TalentEvent.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status not in ["active", "upcoming"]:
        raise HTTPException(status_code=400, detail="Event is not accepting entries")

    # Verify work exists and belongs to user
    work = db.query(Work).filter(
        Work.id == UUID(data.work_id),
        Work.author_id == current_user.id
    ).first()

    if not work:
        raise HTTPException(status_code=404, detail="Work not found or not owned by you")

    # Check if already entered
    existing = db.query(EventEntry).filter(
        EventEntry.event_id == event_id,
        EventEntry.work_id == UUID(data.work_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Work already entered in this event")

    # Create entry
    entry = EventEntry(
        event_id=event_id,
        work_id=UUID(data.work_id),
        user_id=current_user.id
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return EventEntryResponse(
        id=str(entry.id),
        event_id=str(entry.event_id),
        work_id=str(entry.work_id),
        user_id=str(entry.user_id),
        placement=entry.placement,
        submitted_at=entry.submitted_at,
        work_title=work.title,
        author_username=current_user.username
    )

# Get event entries
@router.get("/{event_id}/entries", response_model=List[EventEntryResponse])
async def get_event_entries(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    entries = db.query(EventEntry).filter(
        EventEntry.event_id == event_id
    ).order_by(EventEntry.placement.nullslast(), EventEntry.submitted_at).all()

    results = []
    for entry in entries:
        work = db.query(Work).filter(Work.id == entry.work_id).first()
        user = db.query(User).filter(User.id == entry.user_id).first()

        results.append(EventEntryResponse(
            id=str(entry.id),
            event_id=str(entry.event_id),
            work_id=str(entry.work_id),
            user_id=str(entry.user_id),
            placement=entry.placement,
            submitted_at=entry.submitted_at,
            work_title=work.title if work else None,
            author_username=user.username if user else None
        ))

    return results

# Get user's event entries
@router.get("/my-entries", response_model=List[EventEntryResponse])
async def get_my_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = db.query(EventEntry).filter(
        EventEntry.user_id == current_user.id
    ).order_by(EventEntry.submitted_at.desc()).all()

    results = []
    for entry in entries:
        work = db.query(Work).filter(Work.id == entry.work_id).first()

        results.append(EventEntryResponse(
            id=str(entry.id),
            event_id=str(entry.event_id),
            work_id=str(entry.work_id),
            user_id=str(entry.user_id),
            placement=entry.placement,
            submitted_at=entry.submitted_at,
            work_title=work.title if work else None,
            author_username=current_user.username
        ))

    return results
