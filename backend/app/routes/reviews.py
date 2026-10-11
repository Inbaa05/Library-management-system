"""
reviews.py - Reviews Blueprint
================================
Handles book reviews (star ratings + text) submitted by authenticated users.
One review per user per book is enforced via UPSERT logic.

Routes
------
GET  /reviews/<book_id>/reviews  - List reviews for a book (paginated)
POST /reviews/<book_id>/reviews  - Submit or update a review for a book
"""

import logging
from flask import Blueprint, request, jsonify
from app.utils.auth import login_required, get_current_user
from app.models.review import Review
from app.models.book import Book
from app import db

logger = logging.getLogger(__name__)

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data or {}, "message": message}), status


def _err(message, status=400, errors=None):
    return jsonify({"success": False, "data": errors or {}, "message": message}), status


def _review_payload(review: Review) -> dict:
    """Serialise a Review ORM instance to a safe dict."""
    return {
        "id": review.id,
        "book_id": review.book_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "text": review.text,
        "created_at": review.created_at.isoformat() if getattr(review, "created_at", None) else None,
        "updated_at": review.updated_at.isoformat() if getattr(review, "updated_at", None) else None,
    }


# ---------------------------------------------------------------------------
# GET /reviews/<book_id>/reviews
# ---------------------------------------------------------------------------

@reviews_bp.route("/<int:book_id>/reviews", methods=["GET"])
@login_required
def list_reviews(book_id: int):
    """
    List reviews for a specific book with optional sorting and pagination.

    Path Parameter
    --------------
    book_id : int  - ID of the book

    Query Parameters
    ----------------
    sort     : str  - newest | highest  (default newest)
    page     : int  (default 1)
    per_page : int  (default 20, max 100)

    Returns
    -------
    200 + paginated review list.
    404 if the book does not exist.
    """
    try:
        book = Book.query.get(book_id)
        if not book:
            return _err("Book not found.", 404)

        args = request.args

        try:
            page = max(1, int(args.get("page", 1)))
            per_page = min(100, max(1, int(args.get("per_page", 20))))
        except ValueError:
            return _err("page and per_page must be integers.", 400)

        sort = args.get("sort", "newest").strip().lower()
        valid_sorts = {"newest", "highest"}
        if sort not in valid_sorts:
            return _err(f"sort must be one of: {', '.join(valid_sorts)}.", 400)

        query = Review.query.filter_by(book_id=book_id)

        if sort == "newest":
            query = query.order_by(Review.created_at.desc())
        elif sort == "highest":
            query = query.order_by(Review.rating.desc(), Review.created_at.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [_review_payload(r) for r in paginated.items]

        return _ok(
            data={
                "items": items,
                "total": paginated.total,
                "page": paginated.page,
                "per_page": per_page,
                "pages": paginated.pages,
                "book_id": book_id,
            },
            message="Reviews retrieved.",
        )

    except Exception:
        logger.exception("Unexpected error in GET /reviews/%s/reviews", book_id)
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# POST /reviews/<book_id>/reviews
# ---------------------------------------------------------------------------

@reviews_bp.route("/<int:book_id>/reviews", methods=["POST"])
@login_required
def submit_review(book_id: int):
    """
    Submit or update a review for a book.

    One review per user per book is allowed.  If the user has already reviewed
    this book the existing review is updated (UPSERT semantics).

    Path Parameter
    --------------
    book_id : int  - ID of the book to review

    Body (JSON)
    -----------
    rating : int  (required) - 1–5 star rating
    text   : str  (optional) - Review body text (max 3000 chars)

    Returns
    -------
    201 on creation, 200 on update.
    400 on invalid fields, 404 if book not found.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        book = Book.query.get(book_id)
        if not book:
            return _err("Book not found.", 404)

        body = request.get_json(silent=True) or {}

        # --- Validate rating ---
        if "rating" not in body:
            return _err("Rating is required.", 400)
        try:
            rating = int(body["rating"])
        except (TypeError, ValueError):
            return _err("Rating must be an integer.", 400)
        if rating < 1 or rating > 5:
            return _err("Rating must be between 1 and 5.", 400)

        # --- Validate text (optional) ---
        text = (body.get("text") or "").strip() or None
        if text and len(text) > 3000:
            return _err("Review text must not exceed 3000 characters.", 400)

        # --- UPSERT: one review per user per book ---
        existing = Review.query.filter_by(user_id=user.id, book_id=book_id).first()
        if existing:
            existing.rating = rating
            existing.text = text
            db.session.commit()
            logger.info(
                "Review updated: user id=%s, book id=%s, rating=%s",
                user.id, book_id, rating,
            )
            return _ok(
                data={"review": _review_payload(existing)},
                message="Review updated.",
                status=200,
            )

        review = Review(
            user_id=user.id,
            book_id=book_id,
            rating=rating,
            text=text,
        )
        db.session.add(review)
        db.session.commit()

        # Optionally refresh book's cached average rating if the model supports it
        _refresh_book_rating(book)

        logger.info(
            "Review created: user id=%s, book id=%s, rating=%s",
            user.id, book_id, rating,
        )
        return _ok(
            data={"review": _review_payload(review)},
            message="Review submitted.",
            status=201,
        )

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in POST /reviews/%s/reviews", book_id)
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _refresh_book_rating(book: Book) -> None:
    """
    Recompute and persist the book's cached average rating and review count.
    Safe to call even if the Book model does not expose those columns.
    """
    try:
        from sqlalchemy import func
        result = (
            db.session.query(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("cnt"),
            )
            .filter(Review.book_id == book.id)
            .one()
        )
        if hasattr(book, "average_rating"):
            book.average_rating = round(float(result.avg_rating or 0), 2)
        if hasattr(book, "review_count"):
            book.review_count = result.cnt or 0
        db.session.commit()
    except Exception:
        # Non-critical — log but don't surface to caller
        logger.warning("Could not refresh cached rating for book id=%s", book.id, exc_info=True)
        db.session.rollback()
