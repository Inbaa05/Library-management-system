"""JWT authentication utilities."""
import os
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Optional
import jwt
from flask import request, jsonify, current_app, g
from ..models.user import User
from ..extensions import db


def generate_token(user: User) -> str:
    """Generate a signed JWT access token for a user."""
    payload = {
        'sub': user.id,
        'email': user.email,
        'role': user.role,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload dict or None."""
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request() -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def get_current_user() -> Optional[User]:
    """Decode token from request and return the corresponding User."""
    token = get_token_from_request()
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user = db.session.get(User, payload.get('sub'))
    if not user or not user.is_active:
        return None
    return user


def login_required(f):
    """Decorator: require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles: str):
    """Decorator factory: require the current user to have one of the specified roles."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if g.current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions', 'required_roles': list(roles)}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
