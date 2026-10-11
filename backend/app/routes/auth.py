"""
auth.py - Authentication Blueprint
===================================
Handles user registration, login, logout, profile retrieval,
and password change for the Library Management Comment Optimization System.

Routes
------
POST   /register         - Register a new student user
POST   /login            - Authenticate user, return JWT token
POST   /logout           - Stateless JWT logout (client-side)
GET    /me               - Return current authenticated user info
POST   /change-password  - Change password with old-password verification
"""

import logging
from flask import Blueprint, request, jsonify, g
from app.utils.auth import (
    hash_password,
    verify_password,
    generate_token,
    login_required,
    get_current_user,
)
from app.utils.validation import (
    validate_email,
    validate_password_strength,
    validate_required_fields,
)
from app.models.user import User
from app import db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _user_payload(user: User) -> dict:
    """Return a safe, serialisable representation of a User."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _ok(data: dict = None, message: str = "Success", status: int = 200):
    """Return a successful JSON response."""
    return jsonify({"success": True, "data": data or {}, "message": message}), status


def _err(message: str, status: int = 400, errors: dict = None):
    """Return an error JSON response (never leaks stack traces)."""
    body = {"success": False, "data": errors or {}, "message": message}
    return jsonify(body), status


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new student user.

    Body (JSON)
    -----------
    name     : str  - Display name (required)
    email    : str  - Unique university e-mail (required)
    password : str  - Must satisfy strength requirements (required)

    Returns
    -------
    201 + user info on success, 400 on validation error, 409 on duplicate email.
    """
    try:
        body = request.get_json(silent=True) or {}

        # --- Required-field check ---
        missing = validate_required_fields(body, ["name", "email", "password"])
        if missing:
            return _err(f"Missing required fields: {', '.join(missing)}", 400)

        name = body["name"].strip()
        email = body["email"].strip().lower()
        password = body["password"]

        # --- Validate name ---
        if not name or len(name) < 2:
            return _err("Name must be at least 2 characters.", 400)
        if len(name) > 120:
            return _err("Name must not exceed 120 characters.", 400)

        # --- Validate email format ---
        if not validate_email(email):
            return _err("Invalid e-mail address format.", 400)

        # --- Validate password strength ---
        strength_ok, strength_msg = validate_password_strength(password)
        if not strength_ok:
            return _err(strength_msg, 400)

        # --- Duplicate check ---
        if User.query.filter_by(email=email).first():
            return _err("An account with that e-mail already exists.", 409)

        # --- Persist ---
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="student",
        )
        db.session.add(user)
        db.session.commit()

        token = generate_token(user)
        logger.info("New student registered: %s (id=%s)", email, user.id)

        return _ok(
            data={"token": token, "user": _user_payload(user)},
            message="Registration successful.",
            status=201,
        )

    except Exception as exc:
        db.session.rollback()
        logger.exception("Unexpected error during registration")
        return _err("An unexpected error occurred. Please try again later.", 500)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT access token.

    Body (JSON)
    -----------
    email    : str
    password : str

    Returns
    -------
    200 + {token, user} on success, 400 on missing fields, 401 on bad credentials.
    """
    try:
        body = request.get_json(silent=True) or {}

        missing = validate_required_fields(body, ["email", "password"])
        if missing:
            return _err(f"Missing required fields: {', '.join(missing)}", 400)

        email = body["email"].strip().lower()
        password = body["password"]

        user = User.query.filter_by(email=email).first()

        # Use the same generic message for both "not found" and "wrong password"
        # to prevent user-enumeration attacks.
        if not user or not verify_password(password, user.password_hash):
            return _err("Invalid e-mail or password.", 401)

        if getattr(user, "is_active", True) is False:
            return _err("Your account has been deactivated. Contact the librarian.", 403)

        token = generate_token(user)
        logger.info("User logged in: %s (id=%s)", email, user.id)

        return _ok(
            data={"token": token, "user": _user_payload(user)},
            message="Login successful.",
        )

    except Exception:
        logger.exception("Unexpected error during login")
        return _err("An unexpected error occurred. Please try again later.", 500)


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Logout the current user.

    JWT is stateless; the server does not maintain a session.  The client
    must discard the token from local storage.  If token invalidation is
    required in the future, implement a server-side deny-list here.

    Returns
    -------
    200 with instructions for the client.
    """
    try:
        logger.info("User logged out: id=%s", getattr(g, "current_user_id", "unknown"))
        return _ok(
            data={"instructions": "Please remove the token from client storage."},
            message="Logged out successfully.",
        )
    except Exception:
        logger.exception("Unexpected error during logout")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """
    Return profile information for the currently authenticated user.

    Returns
    -------
    200 + user object, 401 if not authenticated.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("User not found.", 404)

        return _ok(data={"user": _user_payload(user)}, message="Profile retrieved.")

    except Exception:
        logger.exception("Unexpected error fetching /me")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# POST /auth/change-password
# ---------------------------------------------------------------------------

@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """
    Change the authenticated user's password.

    Body (JSON)
    -----------
    old_password     : str - Current password for verification
    new_password     : str - Must satisfy strength requirements
    confirm_password : str - Must match new_password

    Returns
    -------
    200 on success, 400 on validation errors, 401 on wrong old password.
    """
    try:
        body = request.get_json(silent=True) or {}

        missing = validate_required_fields(
            body, ["old_password", "new_password", "confirm_password"]
        )
        if missing:
            return _err(f"Missing required fields: {', '.join(missing)}", 400)

        old_password = body["old_password"]
        new_password = body["new_password"]
        confirm_password = body["confirm_password"]

        user = get_current_user()
        if not user:
            return _err("User not found.", 404)

        # --- Verify old password ---
        if not verify_password(old_password, user.password_hash):
            return _err("Current password is incorrect.", 401)

        # --- Ensure new != old ---
        if old_password == new_password:
            return _err("New password must differ from the current password.", 400)

        # --- Confirm match ---
        if new_password != confirm_password:
            return _err("New password and confirmation do not match.", 400)

        # --- Strength check ---
        strength_ok, strength_msg = validate_password_strength(new_password)
        if not strength_ok:
            return _err(strength_msg, 400)

        # --- Persist ---
        user.password_hash = hash_password(new_password)
        db.session.commit()

        logger.info("Password changed for user id=%s", user.id)
        return _ok(message="Password changed successfully.")

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error during change-password")
        return _err("An unexpected error occurred. Please try again later.", 500)
