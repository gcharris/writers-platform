from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.models.work import Work
from app.models.comment import Comment
import uuid

class NotificationService:
    """Service for creating notifications."""

    @staticmethod
    def create_comment_notification(
        db: Session,
        work: Work,
        commenter: User,
        comment: Comment
    ):
        """Notify work author of new comment."""

        if work.author_id == commenter.id:
            return  # Don't notify yourself

        notification = Notification(
            user_id=work.author_id,
            actor_id=commenter.id,
            work_id=work.id,
            comment_id=comment.id,
            type="comment",
            title="New comment on your work",
            message=f"{commenter.username} commented on '{work.title}'",
            link=f"/works/{work.id}#comment-{comment.id}"
        )

        db.add(notification)
        db.commit()

    @staticmethod
    def create_rating_notification(
        db: Session,
        work: Work,
        rater: User,
        score: int
    ):
        """Notify work author of new rating."""

        if work.author_id == rater.id:
            return  # Don't notify yourself

        stars = "★" * score

        notification = Notification(
            user_id=work.author_id,
            actor_id=rater.id,
            work_id=work.id,
            type="rating",
            title="New rating on your work",
            message=f"{rater.username} rated '{work.title}' {stars}",
            link=f"/works/{work.id}"
        )

        db.add(notification)
        db.commit()

    @staticmethod
    def create_follow_notification(
        db: Session,
        follower: User,
        following: User
    ):
        """Notify user of new follower."""

        notification = Notification(
            user_id=following.id,
            actor_id=follower.id,
            type="follow",
            title="New follower",
            message=f"{follower.username} started following you",
            link=f"/profile/{follower.username}"
        )

        db.add(notification)
        db.commit()

    @staticmethod
    def create_reply_notification(
        db: Session,
        parent_comment: Comment,
        replier: User,
        reply: Comment
    ):
        """Notify comment author of reply."""

        if parent_comment.user_id == replier.id:
            return  # Don't notify yourself

        notification = Notification(
            user_id=parent_comment.user_id,
            actor_id=replier.id,
            comment_id=reply.id,
            type="reply",
            title="Reply to your comment",
            message=f"{replier.username} replied to your comment",
            link=f"/works/{reply.work_id}#comment-{reply.id}"
        )

        db.add(notification)
        db.commit()
