"""Reports route blueprint."""
import io
import csv
from flask import Blueprint, request, jsonify, Response
from ..models.comment import Comment
from ..utils.auth import role_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/comments', methods=['GET'])
@role_required('librarian', 'admin')
def get_comment_report():
    """Retrieve full filtered comment reports."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')

    query = Comment.query
    if category:
        query = query.filter(Comment.category == category)
    if status:
        query = query.filter(Comment.status == status)

    query = query.order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'data': {
            'items': [item.to_dict(include_author=True) for item in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    })

@reports_bp.route('/export.csv', methods=['GET'])
@role_required('librarian', 'admin')
def export_csv():
    """Export filtered comments safely into CSV format."""
    category = request.args.get('category')
    status = request.args.get('status')

    query = Comment.query
    if category:
        query = query.filter(Comment.category == category)
    if status:
        query = query.filter(Comment.status == status)

    comments = query.order_by(Comment.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'ID', 'Title', 'Comment Text', 'Category', 'Status',
        'Moderation Reason', 'Similarity Score', 'Duplicate Of ID',
        'Book Title', 'Rating', 'Facility', 'Created At'
    ])

    for c in comments:
        writer.writerow([
            c.id,
            c.title,
            c.comment_text,
            c.category,
            c.status,
            c.moderation_reason or '',
            c.similarity_score or '',
            c.duplicate_of_id or '',
            c.book_title or '',
            c.rating or '',
            c.facility or '',
            c.created_at.isoformat() if c.created_at else ''
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=library_comments_report.csv"}
    )
