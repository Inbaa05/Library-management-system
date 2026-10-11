"""Flask application factory."""
import os
from flask import Flask, jsonify
from .config import config_by_name
from .extensions import db, migrate, cors, jwt


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', 'http://localhost:5173').split(','),
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
        }
    })

    # Import models to register with SQLAlchemy
    from .models import user, comment, book, review, moderation_log  # noqa: F401

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.comments import comments_bp
    from .routes.books import books_bp
    from .routes.reviews import reviews_bp
    from .routes.moderation import moderation_bp
    from .routes.dashboard import dashboard_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(comments_bp, url_prefix='/api/v1/comments')
    app.register_blueprint(books_bp, url_prefix='/api/v1/books')
    app.register_blueprint(reviews_bp, url_prefix='/api/v1/books')
    app.register_blueprint(moderation_bp, url_prefix='/api/v1/moderation')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'version': '1.0.0'})

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({'error': 'Validation failed', 'message': str(e)}), 422

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

    return app
