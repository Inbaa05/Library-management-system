"""Core comment processing pipeline service."""
import hashlib
import re
from datetime import datetime, timezone
from typing import Optional, Tuple
from flask import current_app
from ..extensions import db
from ..models.comment import Comment
from ..models.moderation_log import ModerationLog
from .category_service import assign_category
from .duplicate_service import check_exact_duplicate, check_near_duplicate
from .filter_service import check_relevance, check_appropriateness


def normalize_text(text: str) -> str:
    """Normalize comment text for comparison: lowercase, collapse whitespace, strip punctuation."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def compute_hash(normalized_text: str) -> str:
    """Compute SHA-256 hash of normalized text for exact duplicate detection."""
    return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()


def process_comment(
    comment: Comment,
    user_id: int,
    auto_approve: bool = False
) -> Comment:
    """
    Run the full comment optimization pipeline:
    1. Normalize text
    2. Compute hash for exact dup detection
    3. Categorize (if not already set)
    4. Check exact duplicate
    5. Check near duplicate
    6. Check relevance
    7. Check appropriateness
    8. Assign final status
    9. Log the processing action
    """
    normalized = normalize_text(comment.comment_text)
    content_hash = compute_hash(normalized)
    comment.content_hash = content_hash

    # 1. Auto-assign category if not provided
    if not comment.category or comment.category not in Comment.VALID_CATEGORIES:
        comment.category = assign_category(comment.title, comment.comment_text)

    # 2. Check for exact duplicate
    exact_dup = check_exact_duplicate(content_hash, exclude_id=comment.id)
    if exact_dup:
        comment.status = 'duplicate'
        comment.duplicate_of_id = exact_dup.id
        comment.similarity_score = 1.0
        comment.moderation_reason = f'Exact duplicate of comment #{exact_dup.id}'
        comment.processed_at = datetime.now(timezone.utc)
        _log_moderation(
            comment_id=comment.id,
            previous_status='pending_review',
            new_status='duplicate',
            action='auto_exact_duplicate',
            reason=comment.moderation_reason
        )
        return comment

    # 3. Check for near-duplicate
    threshold = current_app.config.get('SIMILARITY_THRESHOLD', 0.75)
    near_dup, score = check_near_duplicate(normalized, exclude_id=comment.id, threshold=threshold)
    if near_dup:
        comment.status = 'near_duplicate'
        comment.duplicate_of_id = near_dup.id
        comment.similarity_score = score
        comment.moderation_reason = (
            f'Similar to comment #{near_dup.id} '
            f'(similarity: {score:.0%}, threshold: {threshold:.0%}). '
            'Flagged for librarian review.'
        )
        comment.is_flagged = True
        comment.processed_at = datetime.now(timezone.utc)
        _log_moderation(
            comment_id=comment.id,
            previous_status='pending_review',
            new_status='near_duplicate',
            action='auto_near_duplicate',
            reason=comment.moderation_reason
        )
        return comment

    # 4. Check relevance
    is_relevant, relevance_reason = check_relevance(comment.comment_text, comment.title)
    if not is_relevant:
        comment.status = 'irrelevant'
        comment.moderation_reason = relevance_reason
        comment.is_flagged = True
        comment.processed_at = datetime.now(timezone.utc)
        _log_moderation(
            comment_id=comment.id,
            previous_status='pending_review',
            new_status='irrelevant',
            action='auto_irrelevant',
            reason=relevance_reason
        )
        return comment

    # 5. Check appropriateness
    is_appropriate, appropriateness_reason = check_appropriateness(comment.comment_text)
    if not is_appropriate:
        comment.status = 'inappropriate'
        comment.moderation_reason = appropriateness_reason
        comment.is_flagged = True
        comment.processed_at = datetime.now(timezone.utc)
        _log_moderation(
            comment_id=comment.id,
            previous_status='pending_review',
            new_status='inappropriate',
            action='auto_inappropriate',
            reason=appropriateness_reason
        )
        return comment

    # 6. All checks passed
    comment.processed_at = datetime.now(timezone.utc)
    if auto_approve or current_app.config.get('AUTO_APPROVE_LOW_RISK', False):
        comment.status = 'approved'
        _log_moderation(
            comment_id=comment.id,
            previous_status='pending_review',
            new_status='approved',
            action='auto_approve',
            reason='Passed all automated checks with AUTO_APPROVE enabled'
        )
    else:
        comment.status = 'pending_review'

    return comment


def _log_moderation(
    comment_id: int,
    previous_status: str,
    new_status: str,
    action: str,
    reason: str,
    moderator_id: Optional[int] = None
) -> None:
    """Create a ModerationLog entry. moderator_id=None means system action."""
    log_entry = ModerationLog(
        comment_id=comment_id,
        moderator_id=moderator_id,
        previous_status=previous_status,
        new_status=new_status,
        action=action,
        reason=reason,
    )
    db.session.add(log_entry)
