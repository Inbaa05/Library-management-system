"""Analytics and dashboard data service."""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from sqlalchemy import func, case
from ..extensions import db
from ..models.comment import Comment
from ..models.user import User
from ..models.review import Review
from ..models.moderation_log import ModerationLog


def get_dashboard_summary() -> Dict[str, Any]:
    """Compute summary statistics for the librarian dashboard."""
    total = db.session.query(func.count(Comment.id)).scalar() or 0

    status_counts = dict(
        db.session.query(Comment.status, func.count(Comment.id))
        .group_by(Comment.status)
        .all()
    )

    avg_rating = (
        db.session.query(func.avg(Review.rating)).scalar() or 0
    )

    total_users = db.session.query(func.count(User.id)).scalar() or 0
    student_count = (
        db.session.query(func.count(User.id))
        .filter(User.role == 'student')
        .scalar() or 0
    )

    return {
        'total_comments': total,
        'approved': status_counts.get('approved', 0),
        'pending_review': status_counts.get('pending_review', 0),
        'duplicate': status_counts.get('duplicate', 0),
        'near_duplicate': status_counts.get('near_duplicate', 0),
        'irrelevant': status_counts.get('irrelevant', 0),
        'inappropriate': status_counts.get('inappropriate', 0),
        'archived': status_counts.get('archived', 0),
        'average_rating': round(float(avg_rating), 2) if avg_rating else None,
        'total_users': total_users,
        'student_count': student_count,
    }


def get_feedback_trends(days: int = 30) -> List[Dict[str, Any]]:
    """Return daily comment submission counts for the past N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    results = (
        db.session.query(
            func.date(Comment.created_at).label('date'),
            func.count(Comment.id).label('count')
        )
        .filter(Comment.created_at >= cutoff)
        .group_by(func.date(Comment.created_at))
        .order_by('date')
        .all()
    )

    return [{'date': str(r.date), 'count': r.count} for r in results]


def get_category_distribution() -> List[Dict[str, Any]]:
    """Return comment counts grouped by category."""
    results = (
        db.session.query(
            Comment.category,
            func.count(Comment.id).label('count')
        )
        .filter(Comment.status != 'archived')
        .group_by(Comment.category)
        .order_by(func.count(Comment.id).desc())
        .all()
    )

    labels = Comment.CATEGORY_LABELS
    return [
        {'category': r.category, 'label': labels.get(r.category, r.category), 'count': r.count}
        for r in results
    ]


def get_insights() -> Dict[str, Any]:
    """Surface actionable insights from approved comments."""
    # Most requested improvements (top categories by approved count)
    top_categories = (
        db.session.query(
            Comment.category,
            func.count(Comment.id).label('count')
        )
        .filter(Comment.status == 'approved')
        .group_by(Comment.category)
        .order_by(func.count(Comment.id).desc())
        .limit(5)
        .all()
    )

    # Most common facilities mentioned
    facility_requests = (
        db.session.query(
            Comment.facility,
            func.count(Comment.id).label('count')
        )
        .filter(Comment.facility.isnot(None), Comment.status == 'approved')
        .group_by(Comment.facility)
        .order_by(func.count(Comment.id).desc())
        .limit(5)
        .all()
    )

    # Recent moderation actions
    recent_actions = (
        ModerationLog.query
        .order_by(ModerationLog.created_at.desc())
        .limit(10)
        .all()
    )

    labels = Comment.CATEGORY_LABELS
    return {
        'top_feedback_categories': [
            {'category': r.category, 'label': labels.get(r.category, r.category), 'count': r.count}
            for r in top_categories
        ],
        'top_facilities': [
            {'facility': r.facility, 'count': r.count}
            for r in facility_requests
        ],
        'recent_moderation_actions': [a.to_dict() for a in recent_actions],
    }
