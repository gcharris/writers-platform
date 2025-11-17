from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.work import Work
from app.models.reading_list import ReadingList, ReadingListItem
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/reading-lists", tags=["reading-lists"])

class ReadingListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: str = "private"

class ReadingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None

class ReadingListItemAdd(BaseModel):
    work_id: uuid.UUID
    notes: Optional[str] = None

class ReadingListItemResponse(BaseModel):
    id: uuid.UUID
    work_id: uuid.UUID
    work_title: str
    work_author_username: str
    order_index: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ReadingListResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    visibility: str
    created_at: datetime
    updated_at: datetime
    items_count: int

    class Config:
        from_attributes = True

@router.post("/", response_model=ReadingListResponse, status_code=status.HTTP_201_CREATED)
async def create_reading_list(
    data: ReadingListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reading list."""

    reading_list = ReadingList(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        visibility=data.visibility
    )

    db.add(reading_list)
    db.commit()
    db.refresh(reading_list)

    return ReadingListResponse(
        **reading_list.__dict__,
        items_count=0
    )

@router.get("/", response_model=List[ReadingListResponse])
async def get_my_reading_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's reading lists."""

    lists = db.query(ReadingList).filter(
        ReadingList.user_id == current_user.id
    ).order_by(ReadingList.updated_at.desc()).all()

    result = []
    for reading_list in lists:
        items_count = db.query(ReadingListItem).filter(
            ReadingListItem.reading_list_id == reading_list.id
        ).count()

        result.append(ReadingListResponse(
            **reading_list.__dict__,
            items_count=items_count
        ))

    return result

@router.get("/{list_id}/items", response_model=List[ReadingListItemResponse])
async def get_reading_list_items(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items in a reading list."""

    reading_list = db.query(ReadingList).filter(
        and_(
            ReadingList.id == list_id,
            ReadingList.user_id == current_user.id
        )
    ).first()

    if not reading_list:
        raise HTTPException(status_code=404, detail="Reading list not found")

    items = db.query(ReadingListItem).filter(
        ReadingListItem.reading_list_id == list_id
    ).order_by(ReadingListItem.order_index).all()

    result = []
    for item in items:
        work = item.work
        result.append(ReadingListItemResponse(
            id=item.id,
            work_id=item.work_id,
            work_title=work.title,
            work_author_username=work.author.username,
            order_index=item.order_index,
            notes=item.notes,
            created_at=item.created_at
        ))

    return result

@router.post("/{list_id}/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_reading_list(
    list_id: uuid.UUID,
    data: ReadingListItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to a reading list."""

    reading_list = db.query(ReadingList).filter(
        and_(
            ReadingList.id == list_id,
            ReadingList.user_id == current_user.id
        )
    ).first()

    if not reading_list:
        raise HTTPException(status_code=404, detail="Reading list not found")

    # Check if work exists
    work = db.query(Work).filter(Work.id == data.work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    # Check if already in list
    existing = db.query(ReadingListItem).filter(
        and_(
            ReadingListItem.reading_list_id == list_id,
            ReadingListItem.work_id == data.work_id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Work already in reading list")

    # Get next order index
    max_order = db.query(func.max(ReadingListItem.order_index)).filter(
        ReadingListItem.reading_list_id == list_id
    ).scalar()

    order_index = (max_order or 0) + 1

    item = ReadingListItem(
        reading_list_id=list_id,
        work_id=data.work_id,
        order_index=order_index,
        notes=data.notes
    )

    db.add(item)
    db.commit()

    return {"message": "Item added to reading list"}

@router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_reading_list(
    list_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from a reading list."""

    reading_list = db.query(ReadingList).filter(
        and_(
            ReadingList.id == list_id,
            ReadingList.user_id == current_user.id
        )
    ).first()

    if not reading_list:
        raise HTTPException(status_code=404, detail="Reading list not found")

    item = db.query(ReadingListItem).filter(
        and_(
            ReadingListItem.id == item_id,
            ReadingListItem.reading_list_id == list_id
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading_list(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reading list."""

    reading_list = db.query(ReadingList).filter(
        and_(
            ReadingList.id == list_id,
            ReadingList.user_id == current_user.id
        )
    ).first()

    if not reading_list:
        raise HTTPException(status_code=404, detail="Reading list not found")

    db.delete(reading_list)
    db.commit()
