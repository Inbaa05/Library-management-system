"""User model."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model):
    """Represents an application user (student, librarian, or admin)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        nullable=False,
        default='student',
        server_default='student'
    )
    is_active = db.Column(db.Boolean, default=True, server_default='1')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    comments = db.relationship('Comment', foreign_keys='Comment.user_id', backref='author', lazy='dynamic')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    moderation_actions = db.relationship('ModerationLog', backref='moderator', lazy='dynamic')

    VALID_ROLES = ('student', 'librarian', 'admin')

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email: bool = True) -> dict:
        """Serialize user to a safe dictionary (never includes password hash)."""
        data = {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data

    def __repr__(self) -> str:
        return f'<User {self.email} ({self.role})>'
