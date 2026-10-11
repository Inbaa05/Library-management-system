"""
users.py - Users Blueprint
===========================
Provides endpoints for a user to view and partially update their own profile.

Routes
------
GET   /users/me  - Retrieve the authenticated user's profile
PATCH /users/me  - Update display name (role and email are immutable here)
"""

import logging
from flask import Blueprint, request, jsonify
from app.utils.auth import login_required, get_current_user
from app.utils.validation import validate_required_fields
from app import db

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__, url_prefix="/users")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _user_payload(user) -> dict:
    """Return a safe, serialisable dict for a User model instance."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if getattr(user, "updated_at", None) else None,
    }


def _ok(data: dict = None, message: str = "Success", status: int = 200):
    return jsonify({"success": True, "data": data or {}, "message": message}), status


def _err(message: str, status: int = 400, errors: dict = None):
    return jsonify({"success": False, "data": errors or {}, "message": message}), status


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------

@users_bp.route("/me", methods=["GET"])
@login_required
def get_profile():
    """
    Retrieve the currently authenticated user's full profile.

    Returns
    -------
    200 + user object on success.
    404 if the user account no longer exists.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("User account not found.", 404)

        return _ok(data={"user": _user_payload(user)}, message="Profile retrieved.")

    except Exception:
        logger.exception("Unexpected error in GET /users/me")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# PATCH /users/me
# ---------------------------------------------------------------------------

@users_bp.route("/me", methods=["PATCH"])
@login_required
def update_profile():
    """
    Update the currently authenticated user's display name.

    Only the ``name`` field may be changed through this endpoint.
    Email and role changes are intentionally not supported here to prevent
    privilege escalation or account-hijacking via self-service mutation.

    Body (JSON)
    -----------
    name : str  (required) - New display name (2–120 characters)

    Returns
    -------
    200 + updated user object on success.
    400 on missing / invalid fields.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("User account not found.", 404)

        body = request.get_json(silent=True) or {}

        # --- Reject attempts to mutate protected fields ---
        protected = [k for k in ("email", "role", "password", "password_hash") if k in body]
        if protected:
            return _err(
                f"Field(s) not allowed in this endpoint: {', '.join(protected)}. "
                "Use the appropriate endpoint to change email or password.",
                403,
            )

        # --- Validate name ---
        missing = validate_required_fields(body, ["name"])
        if missing:
            return _err("The 'name' field is required.", 400)

        new_name = body["name"].strip()
        if len(new_name) < 2:
            return _err("Name must be at least 2 characters.", 400)
        if len(new_name) > 120:
            return _err("Name must not exceed 120 characters.", 400)

        # --- Persist ---
        user.name = new_name
        db.session.commit()

        logger.info("Profile updated for user id=%s", user.id)
        return _ok(data={"user": _user_payload(user)}, message="Profile updated.")

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in PATCH /users/me")
        return _err("An unexpected error occurred.", 500)
