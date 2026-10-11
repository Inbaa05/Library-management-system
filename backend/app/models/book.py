"""Book model."""
from datetime import datetime, timezone
from ..extensions import db


class Book(db.Model):
    """Represents a library book record."""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    isbn = db.Column(db.String(20), nullable=True, unique=True)
    cover_url = db.Column(db.String(500), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    added_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reviews = db.relationship('Review', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def average_rating(self) -> float | None:
        """Compute average rating from all reviews."""
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 2)

    @property
    def review_count(self) -> int:
        """Total number of reviews."""
        return self.reviews.count()

    def to_dict(self) -> dict:
        """Serialize book to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'isbn': self.isbn,
            'cover_url': self.cover_url,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'average_rating': self.average_rating,
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<Book {self.title} by {self.author}>'
