"""Comment model — stores feedback, reviews, and moderated outcomes."""
from datetime import datetime, timezone
from ..extensions import db


class Comment(db.Model):
    """Represents a piece of user feedback/comment submitted to the system."""
    __tablename__ = 'comments'

    # Core fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)

    # Moderation fields
    status = db.Column(db.String(30), nullable=False, default='pending_review', index=True)
    moderation_reason = db.Column(db.Text, nullable=True)
    moderation_note = db.Column(db.Text, nullable=True)

    # Duplicate detection
    content_hash = db.Column(db.String(64), nullable=True, index=True)  # SHA-256 of normalized text
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    similarity_score = db.Column(db.Float, nullable=True)

    # Optional fields
    book_title = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    facility = db.Column(db.String(100), nullable=True)

    # Processing metadata
    processed_at = db.Column(db.DateTime, nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    duplicate_of = db.relationship('Comment', remote_side=[id], foreign_keys=[duplicate_of_id])
    moderation_logs = db.relationship('ModerationLog', backref='comment', lazy='dynamic')

    # Valid values
    VALID_CATEGORIES = (
        'book_suggestion',
        'book_review',
        'library_facility',
        'library_service',
        'wifi_digital',
        'reading_recommendation',
        'general_feedback',
    )

    VALID_STATUSES = (
        'pending_review',
        'approved',
        'duplicate',
        'near_duplicate',
        'irrelevant',
        'inappropriate',
        'archived',
    )

    CATEGORY_LABELS = {
        'book_suggestion': 'Book Suggestion',
        'book_review': 'Book Review',
        'library_facility': 'Library Facility',
        'library_service': 'Library Service',
        'wifi_digital': 'Wi-Fi & Digital Facilities',
        'reading_recommendation': 'Reading Recommendation',
        'general_feedback': 'General Feedback',
    }

    def to_dict(self, include_author: bool = False) -> dict:
        """Serialize comment to a dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'comment_text': self.comment_text,
            'category': self.category,
            'category_label': self.CATEGORY_LABELS.get(self.category, self.category),
            'status': self.status,
            'moderation_reason': self.moderation_reason,
            'moderation_note': self.moderation_note,
            'duplicate_of_id': self.duplicate_of_id,
            'similarity_score': self.similarity_score,
            'book_title': self.book_title,
            'rating': self.rating,
            'facility': self.facility,
            'is_flagged': self.is_flagged,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
            }
        return data

    def __repr__(self) -> str:
        return f'<Comment {self.id} [{self.category}] {self.status}>'
