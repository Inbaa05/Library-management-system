"""Review model — star ratings and text reviews for books."""
from datetime import datetime, timezone
from ..extensions import db


class Review(db.Model):
    """Represents a student's star rating and review of a library book."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # One review per user per book
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_review'),
    )

    def to_dict(self, include_reviewer: bool = True) -> dict:
        """Serialize review to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_reviewer and self.reviewer:
            data['reviewer'] = {
                'id': self.reviewer.id,
                'name': self.reviewer.name,
            }
        return data

    def __repr__(self) -> str:
        return f'<Review user={self.user_id} book={self.book_id} rating={self.rating}>'
