"""
comments.py - Comments Blueprint
==================================
Handles submission, retrieval, editing, and deletion of library feedback
comments.  Access is role-aware:

- Students  : submit, view their own + approved comments from others
- Librarians: full CRUD + see all statuses
- Admins    : same as librarian

Routes
------
POST   /comments/         - Submit a new comment (login required)
GET    /comments/         - List comments (paginated, filtered)
GET    /comments/<id>     - Retrieve single comment
PATCH  /comments/<id>     - Edit comment
DELETE /comments/<id>     - Delete comment
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from app.utils.auth import login_required, get_current_user
from app.services.comment_service import process_comment, _log_moderation
from app.models.comment import Comment
from app.models.user import User
from app import db

logger = logging.getLogger(__name__)

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_SORT = {"newest", "oldest", "rating"}
VALID_STATUSES = {"pending_review", "approved", "flagged", "archived"}


def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data or {}, "message": message}), status


def _err(message, status=400, errors=None):
    return jsonify({"success": False, "data": errors or {}, "message": message}), status


def _comment_payload(comment: Comment, include_private: bool = False) -> dict:
    """Serialise a Comment model to a dict.

    Parameters
    ----------
    comment       : Comment ORM instance
    include_private : When False, strip internal-only fields like raw NLP scores.
    """
    payload = {
        "id": comment.id,
        "text": comment.text,
        "status": comment.status,
        "category": comment.category,
        "sentiment_label": comment.sentiment_label,
        "rating": comment.rating,
        "book_id": comment.book_id,
        "user_id": comment.user_id,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "updated_at": comment.updated_at.isoformat() if getattr(comment, "updated_at", None) else None,
    }
    if include_private:
        payload["sentiment_score"] = getattr(comment, "sentiment_score", None)
        payload["flagged_reason"] = getattr(comment, "flagged_reason", None)
        payload["moderation_note"] = getattr(comment, "moderation_note", None)
    return payload


def _parse_date(date_str: str):
    """Parse an ISO-8601 date string, return None on failure."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# POST /comments/
# ---------------------------------------------------------------------------

@comments_bp.route("/", methods=["POST"])
@login_required
def submit_comment():
    """
    Submit a new feedback comment.

    The comment is passed through ``process_comment()`` which runs sentiment
    analysis, auto-categorisation, and spam detection before persisting it.

    Body (JSON)
    -----------
    text    : str  (required) - Feedback text (10–5000 chars)
    book_id : int  (optional) - Associated book
    rating  : int  (optional) - 1–5 star rating

    Returns
    -------
    201 + processed comment on success.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()

        if not text:
            return _err("Comment text is required.", 400)
        if len(text) < 10:
            return _err("Comment must be at least 10 characters.", 400)
        if len(text) > 5000:
            return _err("Comment must not exceed 5000 characters.", 400)

        book_id = body.get("book_id")
        rating = body.get("rating")
        if rating is not None:
            try:
                rating = int(rating)
            except (TypeError, ValueError):
                return _err("Rating must be an integer.", 400)
            if rating < 1 or rating > 5:
                return _err("Rating must be between 1 and 5.", 400)

        comment = process_comment(
            text=text,
            user_id=user.id,
            book_id=book_id,
            rating=rating,
        )

        is_priv = user.role in ("librarian", "admin")
        return _ok(
            data={"comment": _comment_payload(comment, include_private=is_priv)},
            message="Comment submitted.",
            status=201,
        )

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in POST /comments/")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# GET /comments/
# ---------------------------------------------------------------------------

@comments_bp.route("/", methods=["GET"])
@login_required
def list_comments():
    """
    List comments with optional filtering and pagination.

    Query Parameters
    ----------------
    page       : int  (default 1)
    per_page   : int  (default 20, max 100)
    category   : str  - Filter by NLP category
    status     : str  - Filter by status (librarians/admins only for non-approved)
    search     : str  - Full-text search across comment text
    sort_by    : str  - newest | oldest | rating  (default newest)
    start_date : str  - ISO date lower bound (inclusive)
    end_date   : str  - ISO date upper bound (inclusive)

    Access Control
    --------------
    Students see only their own comments + approved comments from others.
    Librarians and admins see all comments regardless of status.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        is_privileged = user.role in ("librarian", "admin")
        args = request.args

        # --- Pagination ---
        try:
            page = max(1, int(args.get("page", 1)))
            per_page = min(100, max(1, int(args.get("per_page", 20))))
        except ValueError:
            return _err("page and per_page must be integers.", 400)

        # --- Filters ---
        category = args.get("category", "").strip() or None
        status_filter = args.get("status", "").strip() or None
        search = args.get("search", "").strip() or None
        sort_by = args.get("sort_by", "newest").strip().lower()
        start_date_str = args.get("start_date", "").strip() or None
        end_date_str = args.get("end_date", "").strip() or None

        if sort_by not in VALID_SORT:
            return _err(f"sort_by must be one of: {', '.join(VALID_SORT)}.", 400)

        start_date = _parse_date(start_date_str)
        end_date = _parse_date(end_date_str)
        if start_date_str and not start_date:
            return _err("Invalid start_date format. Use YYYY-MM-DD.", 400)
        if end_date_str and not end_date:
            return _err("Invalid end_date format. Use YYYY-MM-DD.", 400)

        # --- Build query ---
        query = Comment.query

        if not is_privileged:
            # Students: own comments (any status) OR approved comments from others
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Comment.user_id == user.id,
                    Comment.status == "approved",
                )
            )

        if status_filter:
            if not is_privileged and status_filter != "approved":
                return _err("Students may only filter by status='approved'.", 403)
            if status_filter not in VALID_STATUSES:
                return _err(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}.", 400)
            query = query.filter(Comment.status == status_filter)

        if category:
            query = query.filter(Comment.category == category)

        if search:
            query = query.filter(Comment.text.ilike(f"%{search}%"))

        if start_date:
            query = query.filter(Comment.created_at >= start_date)
        if end_date:
            # Include the whole end day
            from datetime import timedelta
            query = query.filter(Comment.created_at < end_date + timedelta(days=1))

        # --- Sort ---
        if sort_by == "newest":
            query = query.order_by(Comment.created_at.desc())
        elif sort_by == "oldest":
            query = query.order_by(Comment.created_at.asc())
        elif sort_by == "rating":
            query = query.order_by(Comment.rating.desc().nullslast())

        # --- Paginate ---
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [
            _comment_payload(c, include_private=is_privileged)
            for c in paginated.items
        ]

        return _ok(
            data={
                "items": items,
                "total": paginated.total,
                "page": paginated.page,
                "per_page": per_page,
                "pages": paginated.pages,
            },
            message="Comments retrieved.",
        )

    except Exception:
        logger.exception("Unexpected error in GET /comments/")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# GET /comments/<id>
# ---------------------------------------------------------------------------

@comments_bp.route("/<int:comment_id>", methods=["GET"])
@login_required
def get_comment(comment_id: int):
    """
    Retrieve a single comment by ID.

    Access is governed by ``can_view_comment``:
    - Students may view their own comments or any approved comment.
    - Librarians and admins may view any comment.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        comment = Comment.query.get(comment_id)
        if not comment:
            return _err("Comment not found.", 404)

        is_privileged = user.role in ("librarian", "admin")
        can_view = is_privileged or comment.user_id == user.id or comment.status == "approved"
        if not can_view:
            return _err("You do not have permission to view this comment.", 403)

        return _ok(
            data={"comment": _comment_payload(comment, include_private=is_privileged)},
            message="Comment retrieved.",
        )

    except Exception:
        logger.exception("Unexpected error in GET /comments/%s", comment_id)
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# PATCH /comments/<id>
# ---------------------------------------------------------------------------

@comments_bp.route("/<int:comment_id>", methods=["PATCH"])
@login_required
def update_comment(comment_id: int):
    """
    Update a comment's text (and optionally rating / book_id).

    Access is governed by ``can_edit_comment``:
    - Students may edit only their own comments that are pending_review.
    - Librarians and admins may edit any comment.

    If the text is changed the comment is re-processed through NLP.

    Body (JSON)
    -----------
    text    : str  (optional)
    rating  : int  (optional, 1–5)
    book_id : int  (optional)
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        comment = Comment.query.get(comment_id)
        if not comment:
            return _err("Comment not found.", 404)

        is_privileged = user.role in ("librarian", "admin")
        is_owner = comment.user_id == user.id
        is_editable_status = comment.status in ("pending_review",)

        can_edit = is_privileged or (is_owner and is_editable_status)
        if not can_edit:
            return _err(
                "You do not have permission to edit this comment or it is no longer editable.",
                403,
            )

        body = request.get_json(silent=True) or {}
        text_changed = False

        if "text" in body:
            new_text = (body["text"] or "").strip()
            if len(new_text) < 10:
                return _err("Comment text must be at least 10 characters.", 400)
            if len(new_text) > 5000:
                return _err("Comment text must not exceed 5000 characters.", 400)
            if new_text != comment.text:
                comment.text = new_text
                text_changed = True

        if "rating" in body:
            rating = body["rating"]
            if rating is not None:
                try:
                    rating = int(rating)
                except (TypeError, ValueError):
                    return _err("Rating must be an integer.", 400)
                if rating < 1 or rating > 5:
                    return _err("Rating must be between 1 and 5.", 400)
            comment.rating = rating

        if "book_id" in body:
            comment.book_id = body["book_id"]

        if text_changed:
            # Re-run NLP pipeline on updated text
            updated = process_comment(
                text=comment.text,
                user_id=comment.user_id,
                book_id=comment.book_id,
                rating=comment.rating,
                existing_comment=comment,
            )
            db.session.commit()
            return _ok(
                data={"comment": _comment_payload(updated, include_private=is_privileged)},
                message="Comment updated and re-processed.",
            )

        db.session.commit()
        return _ok(
            data={"comment": _comment_payload(comment, include_private=is_privileged)},
            message="Comment updated.",
        )

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in PATCH /comments/%s", comment_id)
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# DELETE /comments/<id>
# ---------------------------------------------------------------------------

@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id: int):
    """
    Delete a comment.

    Access is governed by ``can_delete_comment``:
    - Students may delete only their own pending_review comments.
    - Librarians and admins may delete any comment.

    Returns
    -------
    200 on success, 403 on permission denied, 404 if not found.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        comment = Comment.query.get(comment_id)
        if not comment:
            return _err("Comment not found.", 404)

        is_privileged = user.role in ("librarian", "admin")
        is_owner = comment.user_id == user.id
        is_deletable_status = comment.status in ("pending_review",)

        can_delete = is_privileged or (is_owner and is_deletable_status)
        if not can_delete:
            return _err(
                "You do not have permission to delete this comment or it is not in a deletable state.",
                403,
            )

        db.session.delete(comment)
        db.session.commit()
        logger.info(
            "Comment id=%s deleted by user id=%s (role=%s)",
            comment_id,
            user.id,
            user.role,
        )
        return _ok(message="Comment deleted successfully.")

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in DELETE /comments/%s", comment_id)
        return _err("An unexpected error occurred.", 500)
