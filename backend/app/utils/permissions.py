"""Permission helpers for comment-level access control."""
from flask import g
from ..models.comment import Comment
from ..models.user import User


def can_view_comment(comment: Comment, user: 'User | None') -> bool:
    """Determine if a user can view a given comment."""
    if comment.status == 'approved':
        return True
    if user is None:
        return False
    if user.role in ('librarian', 'admin'):
        return True
    # Owner can always see their own comment
    return comment.user_id == user.id


def can_edit_comment(comment: Comment, user: 'User | None') -> bool:
    """Determine if a user may edit the given comment."""
    if user is None:
        return False
    if user.role in ('librarian', 'admin'):
        return True
    return comment.user_id == user.id and comment.status == 'pending_review'


def can_delete_comment(comment: Comment, user: 'User | None') -> bool:
    """Determine if a user may delete the given comment."""
    if user is None:
        return False
    if user.role in ('librarian', 'admin'):
        return True
    return comment.user_id == user.id
