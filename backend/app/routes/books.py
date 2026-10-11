"""
books.py - Books Blueprint
===========================
Provides endpoints for listing, retrieving, and adding books.
Only librarians and admins can add new books; all authenticated users
can browse and search.

Routes
------
GET  /books/      - List books with optional search and pagination
GET  /books/<id>  - Retrieve a single book with full details
POST /books/      - Add a new book (librarian / admin only)
"""

import logging
from flask import Blueprint, request, jsonify
from app.utils.auth import login_required, get_current_user
from app.utils.validation import validate_required_fields
from app.models.book import Book
from app import db

logger = logging.getLogger(__name__)

books_bp = Blueprint("books", __name__, url_prefix="/books")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data or {}, "message": message}), status


def _err(message, status=400, errors=None):
    return jsonify({"success": False, "data": errors or {}, "message": message}), status


def _book_payload(book: Book) -> dict:
    """Serialise a Book model instance to a safe dict."""
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": getattr(book, "isbn", None),
        "genre": getattr(book, "genre", None),
        "description": getattr(book, "description", None),
        "published_year": getattr(book, "published_year", None),
        "cover_url": getattr(book, "cover_url", None),
        "average_rating": getattr(book, "average_rating", None),
        "review_count": getattr(book, "review_count", None),
        "created_at": book.created_at.isoformat() if getattr(book, "created_at", None) else None,
        "updated_at": book.updated_at.isoformat() if getattr(book, "updated_at", None) else None,
    }


# ---------------------------------------------------------------------------
# GET /books/
# ---------------------------------------------------------------------------

@books_bp.route("/", methods=["GET"])
@login_required
def list_books():
    """
    List all books with optional full-text search and pagination.

    Query Parameters
    ----------------
    search   : str  - Search across title, author, isbn, genre
    page     : int  (default 1)
    per_page : int  (default 20, max 100)
    genre    : str  - Filter by genre (exact match)
    sort_by  : str  - title | author | newest (default title)

    Returns
    -------
    200 + paginated book list.
    """
    try:
        args = request.args

        try:
            page = max(1, int(args.get("page", 1)))
            per_page = min(100, max(1, int(args.get("per_page", 20))))
        except ValueError:
            return _err("page and per_page must be integers.", 400)

        search = args.get("search", "").strip() or None
        genre = args.get("genre", "").strip() or None
        sort_by = args.get("sort_by", "title").strip().lower()

        valid_sorts = {"title", "author", "newest"}
        if sort_by not in valid_sorts:
            return _err(f"sort_by must be one of: {', '.join(valid_sorts)}.", 400)

        query = Book.query

        if search:
            like = f"%{search}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Book.title.ilike(like),
                    Book.author.ilike(like),
                    Book.isbn.ilike(like) if hasattr(Book, "isbn") else False,
                    Book.genre.ilike(like) if hasattr(Book, "genre") else False,
                )
            )

        if genre:
            query = query.filter(Book.genre.ilike(genre))

        if sort_by == "title":
            query = query.order_by(Book.title.asc())
        elif sort_by == "author":
            query = query.order_by(Book.author.asc())
        elif sort_by == "newest":
            query = query.order_by(Book.created_at.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [_book_payload(b) for b in paginated.items]

        return _ok(
            data={
                "items": items,
                "total": paginated.total,
                "page": paginated.page,
                "per_page": per_page,
                "pages": paginated.pages,
            },
            message="Books retrieved.",
        )

    except Exception:
        logger.exception("Unexpected error in GET /books/")
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# GET /books/<id>
# ---------------------------------------------------------------------------

@books_bp.route("/<int:book_id>", methods=["GET"])
@login_required
def get_book(book_id: int):
    """
    Retrieve a single book by ID with all its stored details.

    Returns
    -------
    200 + book object on success.
    404 if the book does not exist.
    """
    try:
        book = Book.query.get(book_id)
        if not book:
            return _err("Book not found.", 404)

        return _ok(data={"book": _book_payload(book)}, message="Book retrieved.")

    except Exception:
        logger.exception("Unexpected error in GET /books/%s", book_id)
        return _err("An unexpected error occurred.", 500)


# ---------------------------------------------------------------------------
# POST /books/
# ---------------------------------------------------------------------------

@books_bp.route("/", methods=["POST"])
@login_required
def add_book():
    """
    Add a new book to the catalogue.

    **Access**: librarian and admin only.

    Body (JSON)
    -----------
    title          : str  (required)
    author         : str  (required)
    isbn           : str  (optional)
    genre          : str  (optional)
    description    : str  (optional)
    published_year : int  (optional)
    cover_url      : str  (optional)

    Returns
    -------
    201 + book object on success.
    400 on missing / invalid fields.
    403 on insufficient privileges.
    409 on duplicate ISBN.
    """
    try:
        user = get_current_user()
        if not user:
            return _err("Authentication required.", 401)

        if user.role not in ("librarian", "admin"):
            return _err("Only librarians and admins may add books.", 403)

        body = request.get_json(silent=True) or {}

        missing = validate_required_fields(body, ["title", "author"])
        if missing:
            return _err(f"Missing required fields: {', '.join(missing)}", 400)

        title = body["title"].strip()
        author = body["author"].strip()

        if not title:
            return _err("Title must not be blank.", 400)
        if len(title) > 500:
            return _err("Title must not exceed 500 characters.", 400)
        if not author:
            return _err("Author must not be blank.", 400)
        if len(author) > 300:
            return _err("Author must not exceed 300 characters.", 400)

        isbn = (body.get("isbn") or "").strip() or None
        genre = (body.get("genre") or "").strip() or None
        description = (body.get("description") or "").strip() or None
        cover_url = (body.get("cover_url") or "").strip() or None

        published_year = body.get("published_year")
        if published_year is not None:
            try:
                published_year = int(published_year)
            except (TypeError, ValueError):
                return _err("published_year must be an integer.", 400)
            from datetime import date
            current_year = date.today().year
            if published_year < 1000 or published_year > current_year + 2:
                return _err(f"published_year must be between 1000 and {current_year + 2}.", 400)

        # --- Duplicate ISBN check ---
        if isbn and hasattr(Book, "isbn"):
            existing = Book.query.filter_by(isbn=isbn).first()
            if existing:
                return _err(f"A book with ISBN '{isbn}' already exists (id={existing.id}).", 409)

        book = Book(
            title=title,
            author=author,
        )
        # Set optional attributes safely
        for attr, val in (
            ("isbn", isbn),
            ("genre", genre),
            ("description", description),
            ("cover_url", cover_url),
            ("published_year", published_year),
        ):
            if hasattr(book, attr):
                setattr(book, attr, val)

        db.session.add(book)
        db.session.commit()

        logger.info(
            "Book '%s' added by user id=%s (role=%s)", title, user.id, user.role
        )
        return _ok(data={"book": _book_payload(book)}, message="Book added.", status=201)

    except Exception:
        db.session.rollback()
        logger.exception("Unexpected error in POST /books/")
        return _err("An unexpected error occurred.", 500)
