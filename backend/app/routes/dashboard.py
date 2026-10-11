"""Dashboard route blueprint."""
from flask import Blueprint, request, jsonify
from ..utils.auth import role_required
from ..services.analytics_service import (
    get_dashboard_summary,
    get_feedback_trends,
    get_category_distribution,
    get_insights
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
@role_required('librarian', 'admin')
def summary():
    """Retrieve top-level summary metrics."""
    data = get_dashboard_summary()
    return jsonify({'success': True, 'data': data})

@dashboard_bp.route('/trends', methods=['GET'])
@role_required('librarian', 'admin')
def trends():
    """Retrieve submission volume trends."""
    days = request.args.get('days', 30, type=int)
    data = get_feedback_trends(days=days)
    return jsonify({'success': True, 'data': data})

@dashboard_bp.route('/categories', methods=['GET'])
@role_required('librarian', 'admin')
def categories():
    """Retrieve category distribution statistics."""
    data = get_category_distribution()
    return jsonify({'success': True, 'data': data})

@dashboard_bp.route('/insights', methods=['GET'])
@role_required('librarian', 'admin')
def insights():
    """Retrieve actionable insights and recurring themes."""
    data = get_insights()
    return jsonify({'success': True, 'data': data})
