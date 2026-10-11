"""Moderation blueprint."""
from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models.comment import Comment
from ..models.moderation_log import ModerationLog
from ..utils.auth import login_required, role_required
from ..services.comment_service import _log_moderation

moderation_bp = Blueprint('moderation', __name__)

@moderation_bp.route('/queue', methods=['GET'])
@role_required('librarian', 'admin')
def get_moderation_queue():
    """List pending or flagged comments needing moderation."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')

    query = Comment.query
    if status_filter:
        query = query.filter(Comment.status == status_filter)
    else:
        query = query.filter(Comment.status.in_(['pending_review', 'near_duplicate', 'irrelevant', 'inappropriate']))

    if category_filter:
        query = query.filter(Comment.category == category_filter)

    query = query.order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = [item.to_dict(include_author=True) for item in pagination.items]

    return jsonify({
        'success': True,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    })

@moderation_bp.route('/<int:comment_id>/approve', methods=['POST'])
@role_required('librarian', 'admin')
def approve_comment(comment_id):
    """Approve a comment for public visibility."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    data = request.get_json() or {}
    prev_status = comment.status
    comment.status = 'approved'
    comment.is_flagged = False
    comment.moderation_note = data.get('note', '')

    _log_moderation(
        comment_id=comment.id,
        previous_status=prev_status,
        new_status='approved',
        action='manual_approve',
        reason=data.get('note', 'Approved by librarian'),
        moderator_id=g.current_user.id
    )
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Comment approved successfully',
        'data': comment.to_dict(include_author=True)
    })

@moderation_bp.route('/<int:comment_id>/flag', methods=['POST'])
@role_required('librarian', 'admin')
def flag_comment(comment_id):
    """Flag a comment with a reason."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    data = request.get_json() or {}
    reason = data.get('reason')
    if not reason:
        return jsonify({'error': 'A reason is required to flag a comment'}), 422

    target_status = data.get('status', 'inappropriate')
    if target_status not in Comment.VALID_STATUSES:
        target_status = 'inappropriate'

    prev_status = comment.status
    comment.status = target_status
    comment.is_flagged = True
    comment.moderation_reason = reason

    _log_moderation(
        comment_id=comment.id,
        previous_status=prev_status,
        new_status=target_status,
        action='manual_flag',
        reason=reason,
        moderator_id=g.current_user.id
    )
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Comment flagged as {target_status}',
        'data': comment.to_dict(include_author=True)
    })

@moderation_bp.route('/<int:comment_id>/archive', methods=['POST'])
@role_required('librarian', 'admin')
def archive_comment(comment_id):
    """Archive a comment."""
    data = request.get_json() or {}
    if not data.get('confirm'):
        return jsonify({'error': 'Confirmation is required for destructive action'}), 400

    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    prev_status = comment.status
    comment.status = 'archived'

    _log_moderation(
        comment_id=comment.id,
        previous_status=prev_status,
        new_status='archived',
        action='archive',
        reason=data.get('reason', 'Archived by librarian'),
        moderator_id=g.current_user.id
    )
    db.session.commit()

    return jsonify({'success': True, 'message': 'Comment archived successfully'})

@moderation_bp.route('/<int:comment_id>/restore', methods=['POST'])
@role_required('librarian', 'admin')
def restore_comment(comment_id):
    """Restore an archived comment to pending review."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    prev_status = comment.status
    comment.status = 'pending_review'

    _log_moderation(
        comment_id=comment.id,
        previous_status=prev_status,
        new_status='pending_review',
        action='restore',
        reason='Restored from archive',
        moderator_id=g.current_user.id
    )
    db.session.commit()

    return jsonify({'success': True, 'message': 'Comment restored to pending review', 'data': comment.to_dict()})

@moderation_bp.route('/<int:comment_id>/category', methods=['PATCH'])
@role_required('librarian', 'admin')
def update_comment_category(comment_id):
    """Manually update category of a comment."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    data = request.get_json() or {}
    new_cat = data.get('category')
    if not new_cat or new_cat not in Comment.VALID_CATEGORIES:
        return jsonify({'error': 'Invalid category provided'}), 422

    prev_cat = comment.category
    comment.category = new_cat

    _log_moderation(
        comment_id=comment.id,
        previous_status=comment.status,
        new_status=comment.status,
        action='change_category',
        reason=f'Category changed from {prev_cat} to {new_cat}',
        moderator_id=g.current_user.id
    )
    db.session.commit()

    return jsonify({'success': True, 'message': 'Category updated', 'data': comment.to_dict()})

@moderation_bp.route('/<int:comment_id>/history', methods=['GET'])
@role_required('librarian', 'admin')
def get_comment_moderation_history(comment_id):
    """Get audit trail of moderation actions for a comment."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    logs = ModerationLog.query.filter_by(comment_id=comment.id).order_by(ModerationLog.created_at.desc()).all()
    return jsonify({
        'success': True,
        'data': [log.to_dict() for log in logs]
    })
