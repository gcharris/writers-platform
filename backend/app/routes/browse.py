from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.core.database import get_db
from app.models.work import Work
from app.models.user import User
from app.models.badge import Badge
from app.models.knowledge_graph import ProjectGraph
from app.schemas.browse import (
    WorkListItem, BrowseFilters, BrowseResponse,
    SearchQuery, GenreStats
)
from typing import List, Optional
import math
import json

router = APIRouter(prefix="/browse", tags=["browse"])

@router.get("/works", response_model=BrowseResponse)
async def browse_works(
    genre: Optional[str] = None,
    badge_type: Optional[str] = Query(None, description="Filter by badge type: ai_analyzed, human_verified, human_self, community_upload"),
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    min_word_count: Optional[int] = None,
    max_word_count: Optional[int] = None,
    content_rating: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Browse works with filters and pagination.

    Phase 2: Added badge_type filter for discovering authentic content.
    """

    # Build query
    query = db.query(Work).filter(
        and_(
            Work.status == "published",
            Work.visibility == "public"
        )
    ).join(User, Work.author_id == User.id)

    # Phase 2: Filter by badge type
    if badge_type:
        query = query.join(Badge, Work.id == Badge.work_id).filter(Badge.badge_type == badge_type)

    # Apply filters
    if genre:
        query = query.filter(Work.genre == genre)

    if min_rating is not None:
        query = query.filter(Work.rating_average >= min_rating)

    if max_rating is not None:
        query = query.filter(Work.rating_average <= max_rating)

    if min_word_count is not None:
        query = query.filter(Work.word_count >= min_word_count)

    if max_word_count is not None:
        query = query.filter(Work.word_count <= max_word_count)

    if content_rating:
        query = query.filter(Work.content_rating == content_rating)

    # Get total count
    total = query.count()

    # Apply sorting
    if sort_by == "rating_average":
        order_col = Work.rating_average
    elif sort_by == "word_count":
        order_col = Work.word_count
    elif sort_by == "views_count":
        order_col = Work.views_count
    else:
        order_col = Work.created_at

    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    works = query.offset(offset).limit(page_size).all()

    # Format response
    work_items = []
    for work in works:
        work_items.append(WorkListItem(
            id=work.id,
            title=work.title,
            author_id=work.author_id,
            author_username=work.author.username,
            genre=work.genre,
            summary=work.summary,
            word_count=work.word_count,
            rating_average=work.rating_average,
            rating_count=work.rating_count,
            comment_count=work.comment_count,
            bookmarks_count=work.bookmarks_count,
            views_count=work.views_count,
            published_at=work.published_at,
            created_at=work.created_at
        ))

    return BrowseResponse(
        works=work_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )

@router.get("/search", response_model=BrowseResponse)
async def search_works(
    q: str = Query(..., min_length=1),
    search_in: str = "title,summary",
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Search works with full-text search."""

    # Build base query
    query = db.query(Work).filter(
        and_(
            Work.status == "published",
            Work.visibility == "public"
        )
    ).join(User, Work.author_id == User.id)

    # Build search filters
    search_fields = search_in.split(",")
    search_filters = []

    if "title" in search_fields:
        search_filters.append(Work.title.ilike(f"%{q}%"))
    if "summary" in search_fields:
        search_filters.append(Work.summary.ilike(f"%{q}%"))
    if "content" in search_fields:
        search_filters.append(Work.content.ilike(f"%{q}%"))

    if search_filters:
        query = query.filter(or_(*search_filters))

    # Apply additional filters
    if genre:
        query = query.filter(Work.genre == genre)

    if min_rating is not None:
        query = query.filter(Work.rating_average >= min_rating)

    # Get total count
    total = query.count()

    # Apply sorting
    if sort_by == "rating_average":
        order_col = Work.rating_average
    elif sort_by == "views_count":
        order_col = Work.views_count
    else:
        order_col = Work.created_at

    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    works = query.offset(offset).limit(page_size).all()

    # Format response
    work_items = []
    for work in works:
        work_items.append(WorkListItem(
            id=work.id,
            title=work.title,
            author_id=work.author_id,
            author_username=work.author.username,
            genre=work.genre,
            summary=work.summary,
            word_count=work.word_count,
            rating_average=work.rating_average,
            rating_count=work.rating_count,
            comment_count=work.comment_count,
            bookmarks_count=work.bookmarks_count,
            views_count=work.views_count,
            published_at=work.published_at,
            created_at=work.created_at
        ))

    return BrowseResponse(
        works=work_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )

@router.get("/genres", response_model=List[GenreStats])
async def get_genres(db: Session = Depends(get_db)):
    """Get all genres with statistics."""

    results = db.query(
        Work.genre,
        func.count(Work.id).label("count"),
        func.avg(Work.rating_average).label("avg_rating")
    ).filter(
        and_(
            Work.status == "published",
            Work.visibility == "public",
            Work.genre.isnot(None)
        )
    ).group_by(Work.genre).all()

    return [
        GenreStats(
            genre=r.genre,
            count=r.count,
            avg_rating=float(r.avg_rating) if r.avg_rating else 0.0
        )
        for r in results
    ]


@router.get("/by-entity", response_model=BrowseResponse)
async def browse_by_entity(
    entity_name: str = Query(..., description="Entity name to search for (e.g., 'Mickey', 'Shanghai')"),
    entity_type: Optional[str] = Query(None, description="Entity type: character, location, theme, etc."),
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    🎯 ENTITY-BASED DISCOVERY (NEW!)

    Find stories by characters, locations, or themes.

    Examples:
    - Find stories with "Mickey" character: ?entity_name=Mickey&entity_type=character
    - Find stories set in "Shanghai": ?entity_name=Shanghai&entity_type=location
    - Find stories about "AI": ?entity_name=AI&entity_type=theme

    This is a unique discovery mechanism that leverages our Knowledge Graph!
    """

    # Step 1: Find works with Factory projects (only they have knowledge graphs)
    base_query = db.query(Work).filter(
        and_(
            Work.status == "published",
            Work.visibility == "public",
            Work.factory_project_id.isnot(None)
        )
    ).join(User, Work.author_id == User.id)

    # Step 2: Get all knowledge graphs
    graphs = db.query(ProjectGraph).filter(
        ProjectGraph.project_id.in_(
            db.query(Work.factory_project_id).filter(Work.factory_project_id.isnot(None))
        )
    ).all()

    # Step 3: Search graphs for matching entities
    matching_project_ids = []
    entity_name_lower = entity_name.lower()

    for graph in graphs:
        if not graph.graph_data:
            continue

        # Parse graph data
        try:
            graph_json = graph.graph_data
            nodes = graph_json.get('nodes', [])

            # Search for entity in nodes
            for node in nodes:
                node_name = node.get('name', '').lower()
                node_type = node.get('type', '').lower()

                # Fuzzy match on name
                if entity_name_lower in node_name or node_name in entity_name_lower:
                    # If entity_type specified, must match
                    if entity_type:
                        if entity_type.lower() == node_type:
                            matching_project_ids.append(graph.project_id)
                            break
                    else:
                        # No type filter, just name match
                        matching_project_ids.append(graph.project_id)
                        break

        except Exception as e:
            # Skip malformed graph data
            print(f"Error parsing graph {graph.id}: {e}")
            continue

    # Remove duplicates
    matching_project_ids = list(set(matching_project_ids))

    # Step 4: Filter works to only those with matching entities
    if matching_project_ids:
        base_query = base_query.filter(Work.factory_project_id.in_(matching_project_ids))
    else:
        # No matches found - return empty result
        return BrowseResponse(
            works=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )

    # Step 5: Apply additional filters
    if genre:
        base_query = base_query.filter(Work.genre == genre)

    if min_rating is not None:
        base_query = base_query.filter(Work.rating_average >= min_rating)

    # Get total count
    total = base_query.count()

    # Step 6: Apply sorting
    if sort_by == "rating_average":
        order_col = Work.rating_average
    elif sort_by == "word_count":
        order_col = Work.word_count
    elif sort_by == "views_count":
        order_col = Work.views_count
    else:
        order_col = Work.created_at

    if sort_order == "asc":
        base_query = base_query.order_by(order_col.asc())
    else:
        base_query = base_query.order_by(order_col.desc())

    # Step 7: Apply pagination
    offset = (page - 1) * page_size
    works = base_query.offset(offset).limit(page_size).all()

    # Step 8: Format response
    work_items = []
    for work in works:
        work_items.append(WorkListItem(
            id=work.id,
            title=work.title,
            author_id=work.author_id,
            author_username=work.author.username,
            genre=work.genre,
            summary=work.summary,
            word_count=work.word_count,
            rating_average=work.rating_average,
            rating_count=work.rating_count,
            comment_count=work.comment_count,
            bookmarks_count=work.bookmarks_count,
            views_count=work.views_count,
            published_at=work.published_at,
            created_at=work.created_at
        ))

    return BrowseResponse(
        works=work_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )
