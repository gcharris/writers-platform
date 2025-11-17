from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.work import Work
from app.models.follow import Follow
from app.schemas.profile import (
    ProfileUpdate, ProfileResponse, UserWorkSummary,
    UserWorksResponse, FollowResponse, FollowersResponse
)
from app.services.notifications import NotificationService
from typing import Optional
import uuid

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile."""

    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        location=current_user.location,
        website=current_user.website,
        role=current_user.role,
        works_count=current_user.works_count,
        followers_count=current_user.followers_count,
        following_count=current_user.following_count,
        created_at=current_user.created_at,
        is_following=None  # N/A for own profile
    )

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""

    if data.bio is not None:
        current_user.bio = data.bio
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    if data.location is not None:
        current_user.location = data.location
    if data.website is not None:
        current_user.website = data.website

    db.commit()
    db.refresh(current_user)

    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        location=current_user.location,
        website=current_user.website,
        role=current_user.role,
        works_count=current_user.works_count,
        followers_count=current_user.followers_count,
        following_count=current_user.following_count,
        created_at=current_user.created_at,
        is_following=None
    )

@router.get("/{username}", response_model=ProfileResponse)
async def get_user_profile(
    username: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile by username."""

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if current user is following this user
    is_following = None
    if current_user:
        follow = db.query(Follow).filter(
            and_(
                Follow.follower_id == current_user.id,
                Follow.following_id == user.id
            )
        ).first()
        is_following = follow is not None

    return ProfileResponse(
        id=user.id,
        username=user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        location=user.location,
        website=user.website,
        role=user.role,
        works_count=user.works_count,
        followers_count=user.followers_count,
        following_count=user.following_count,
        created_at=user.created_at,
        is_following=is_following
    )

@router.get("/{username}/works", response_model=UserWorksResponse)
async def get_user_works(
    username: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's published works."""

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query works
    query = db.query(Work).filter(
        and_(
            Work.author_id == user.id,
            Work.status == "published",
            Work.visibility == "public"
        )
    ).order_by(Work.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    works = query.offset(offset).limit(page_size).all()

    work_summaries = [
        UserWorkSummary(
            id=work.id,
            title=work.title,
            genre=work.genre,
            word_count=work.word_count,
            rating_average=work.rating_average,
            rating_count=work.rating_count,
            views_count=work.views_count,
            published_at=work.published_at,
            created_at=work.created_at
        )
        for work in works
    ]

    return UserWorksResponse(
        works=work_summaries,
        total=total,
        page=page,
        page_size=page_size
    )

@router.post("/{username}/follow", response_model=FollowResponse, status_code=status.HTTP_201_CREATED)
async def follow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow a user."""

    # Get user to follow
    user_to_follow = db.query(User).filter(User.username == username).first()

    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_follow.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Check if already following
    existing = db.query(Follow).filter(
        and_(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_to_follow.id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already following this user")

    # Create follow relationship
    follow = Follow(
        follower_id=current_user.id,
        following_id=user_to_follow.id
    )

    db.add(follow)

    # Update counts
    current_user.following_count += 1
    user_to_follow.followers_count += 1

    db.commit()
    db.refresh(follow)

    # Send follow notification
    NotificationService.create_follow_notification(db, current_user, user_to_follow)

    return FollowResponse(
        id=follow.id,
        follower_id=follow.follower_id,
        following_id=follow.following_id,
        follower_username=current_user.username,
        following_username=user_to_follow.username,
        created_at=follow.created_at
    )

@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user."""

    # Get user to unfollow
    user_to_unfollow = db.query(User).filter(User.username == username).first()

    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")

    # Find follow relationship
    follow = db.query(Follow).filter(
        and_(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_to_unfollow.id
        )
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")

    # Delete follow relationship
    db.delete(follow)

    # Update counts
    current_user.following_count -= 1
    user_to_unfollow.followers_count -= 1

    db.commit()

@router.get("/{username}/followers", response_model=FollowersResponse)
async def get_followers(
    username: str,
    db: Session = Depends(get_db)
):
    """Get user's followers."""

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get followers
    follows = db.query(Follow).filter(Follow.following_id == user.id).all()

    follower_profiles = []
    for follow in follows:
        follower = follow.follower
        follower_profiles.append(ProfileResponse(
            id=follower.id,
            username=follower.username,
            bio=follower.bio,
            avatar_url=follower.avatar_url,
            location=follower.location,
            website=follower.website,
            role=follower.role,
            works_count=follower.works_count,
            followers_count=follower.followers_count,
            following_count=follower.following_count,
            created_at=follower.created_at
        ))

    return FollowersResponse(
        users=follower_profiles,
        total=len(follower_profiles)
    )

@router.get("/{username}/following", response_model=FollowersResponse)
async def get_following(
    username: str,
    db: Session = Depends(get_db)
):
    """Get users that this user is following."""

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get following
    follows = db.query(Follow).filter(Follow.follower_id == user.id).all()

    following_profiles = []
    for follow in follows:
        following_user = follow.following
        following_profiles.append(ProfileResponse(
            id=following_user.id,
            username=following_user.username,
            bio=following_user.bio,
            avatar_url=following_user.avatar_url,
            location=following_user.location,
            website=following_user.website,
            role=following_user.role,
            works_count=following_user.works_count,
            followers_count=following_user.followers_count,
            following_count=following_user.following_count,
            created_at=following_user.created_at
        ))

    return FollowersResponse(
        users=following_profiles,
        total=len(following_profiles)
    )
