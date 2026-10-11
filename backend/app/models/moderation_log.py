"""ModerationLog model — audit trail for librarian actions."""
from datetime import datetime, timezone
from ..extensions import db


class ModerationLog(db.Model):
    """Audit log entry for every moderation action taken on a comment."""
    __tablename__ = 'moderation_logs'

    id = db.Column(db.Integer, primary_key=True)
    moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # None = system
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False, index=True)
    previous_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(60), nullable=False)  # e.g. 'approve', 'flag', 'auto_duplicate'
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        """Serialize moderation log to dictionary."""
        data = {
            'id': self.id,
            'comment_id': self.comment_id,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'action': self.action,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if self.moderator:
            data['moderator'] = {
                'id': self.moderator.id,
                'name': self.moderator.name,
            }
        else:
            data['moderator'] = {'id': None, 'name': 'System'}
        return data

    def __repr__(self) -> str:
        return f'<ModerationLog comment={self.comment_id} action={self.action}>'
