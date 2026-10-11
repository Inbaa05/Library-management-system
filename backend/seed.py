"""
Development seed data. Clearly labelled demo data. Run once.

This script populates the database with sample users, books, comments,
and reviews for development and demonstration purposes. It is idempotent —
running it multiple times will not create duplicate records.

Usage:
    cd backend
    flask --app app seed   # if registered as a CLI command, OR
    python seed.py         # if run directly
"""

import sys
import os

# ---------------------------------------------------------------------------
# Ensure the backend package is importable when the script is run directly.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.book import Book
from app.models.comment import Comment
from app.models.review import Review
from app.services.comment_pipeline import process_comment  # adjust import if needed


# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

USERS = [
    {
        "name": "Alice Librarian",
        "email": "librarian@library.edu",
        "role": "librarian",
        "password": "Librarian@2024",
    },
    {
        "name": "Bob Student",
        "email": "student@library.edu",
        "role": "student",
        "password": "Student@2024",
    },
]

BOOKS = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "genre": "Software Engineering",
        "description": (
            "A handbook of agile software craftsmanship. Packed with practical "
            "advice on writing maintainable, readable code."
        ),
        "published_year": 2008,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg",
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas & Andrew Hunt",
        "isbn": "9780135957059",
        "genre": "Software Engineering",
        "description": (
            "Your journey to mastery: timeless lessons about programming "
            "best practices, tools, and philosophies."
        ),
        "published_year": 2019,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780135957059-L.jpg",
    },
    {
        "title": "Introduction to Algorithms",
        "author": "Cormen, Leiserson, Rivest & Stein",
        "isbn": "9780262033848",
        "genre": "Computer Science",
        "description": (
            "The definitive reference for computer science algorithms, "
            "covering sorting, graph theory, dynamic programming, and more."
        ),
        "published_year": 2009,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780262033848-L.jpg",
    },
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "isbn": "9781593279288",
        "genre": "Python Programming",
        "description": (
            "A hands-on, project-based introduction to programming in Python 3, "
            "ideal for beginners and those switching languages."
        ),
        "published_year": 2019,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9781593279288-L.jpg",
    },
    {
        "title": "Fluent Python",
        "author": "Luciano Ramalho",
        "isbn": "9781492056355",
        "genre": "Python Programming",
        "description": (
            "An in-depth look at Python's internals and idiomatic patterns "
            "that experienced developers rely on."
        ),
        "published_year": 2022,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9781492056355-L.jpg",
    },
    {
        "title": "Database System Concepts",
        "author": "Silberschatz, Korth & Sudarshan",
        "isbn": "9780078022159",
        "genre": "Databases",
        "description": (
            "Comprehensive textbook covering relational models, SQL, "
            "transaction management, and distributed databases."
        ),
        "published_year": 2019,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780078022159-L.jpg",
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "isbn": "9781449373320",
        "genre": "Databases",
        "description": (
            "A deep dive into the principles behind reliable, scalable, "
            "and maintainable data systems."
        ),
        "published_year": 2017,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9781449373320-L.jpg",
    },
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "isbn": "9780345391803",
        "genre": "Science Fiction",
        "description": (
            "A comedic sci-fi classic following Arthur Dent's adventures "
            "after Earth is demolished to make way for a hyperspace bypass."
        ),
        "published_year": 1979,
        "cover_url": "https://covers.openlibrary.org/b/isbn/9780345391803-L.jpg",
    },
]

# Each comment dict includes: text, category_hint, note (for console output)
COMMENTS = [
    # ── Book suggestions ────────────────────────────────────────────────────
    {
        "text": (
            "I would love to see more computer science textbooks in the library. "
            "Books like 'Operating System Concepts' by Silberschatz or "
            "'Computer Networks' by Tanenbaum would be very helpful for CS students."
        ),
        "note": "Book suggestion – CS textbooks",
    },
    {
        "text": (
            "Could the library please add more Python programming books? "
            "We need 'Automate the Boring Stuff with Python' and 'Python for Data Analysis'. "
            "These are used in our coursework but always checked out."
        ),
        "note": "Book suggestion – Python books",
    },
    {
        "text": (
            "Please consider purchasing 'Artificial Intelligence: A Modern Approach' "
            "by Russell and Norvig. Our AI course relies heavily on this text and "
            "the current copy is always borrowed."
        ),
        "note": "Book suggestion – AI textbook",
    },
    # ── Wi-Fi / internet complaints ─────────────────────────────────────────
    {
        "text": (
            "The Wi-Fi in the reading area on the second floor is extremely slow, "
            "especially during peak hours between 2 PM and 6 PM. It makes it nearly "
            "impossible to access online journals or submit assignments."
        ),
        "note": "Wi-Fi complaint – reading area",
    },
    {
        "text": (
            "Internet connectivity near the periodicals section keeps dropping. "
            "I lose my connection every 10–15 minutes, which interrupts my research. "
            "Could we get a Wi-Fi extender or a dedicated study network?"
        ),
        "note": "Wi-Fi complaint – periodicals section",
    },
    # ── Seating / facility requests ─────────────────────────────────────────
    {
        "text": (
            "There are never enough quiet study seats available, particularly during "
            "exam season. Could the library expand the silent study zone on the third "
            "floor or add more individual carrels?"
        ),
        "note": "Seating request – more study seats",
    },
    {
        "text": (
            "The group study rooms are always fully booked. It would be great to have "
            "an online reservation system so students can book in advance rather than "
            "waiting in line."
        ),
        "note": "Seating request – group study rooms",
    },
    # ── Book reviews ────────────────────────────────────────────────────────
    {
        "text": (
            "Clean Code by Robert C. Martin is an excellent resource. "
            "The chapter on meaningful names alone changed how I write code. "
            "Highly recommend it to every CS student."
        ),
        "note": "Good review – Clean Code",
    },
    {
        "text": (
            "Introduction to Algorithms is challenging but incredibly thorough. "
            "I used it for my algorithms course and it covered every topic in depth. "
            "The library's copy is well-maintained. Five stars!"
        ),
        "note": "Good review – Introduction to Algorithms",
    },
    # ── Near-duplicate pair (demonstrates detection) ─────────────────────────
    {
        "text": (
            "The library should stock more Python books. Students in programming "
            "courses urgently need titles like 'Python Crash Course' and "
            "'Automate the Boring Stuff'. Please acquire additional copies."
        ),
        "note": "Near-duplicate #1 – Python books (original)",
    },
    {
        "text": (
            "The library really needs to stock more Python programming books. "
            "Students taking programming classes urgently need books like "
            "'Python Crash Course' and 'Automate the Boring Stuff'. "
            "Please buy more copies as soon as possible."
        ),
        "note": "Near-duplicate #2 – Python books (near-duplicate of previous)",
    },
    # ── Off-topic comment (demonstrates irrelevance detection) ───────────────
    {
        "text": (
            "I had a great pizza at the new Italian restaurant downtown last night. "
            "The margherita was perfectly crispy. Totally unrelated to the library, "
            "but just wanted to share!"
        ),
        "note": "Off-topic – food review (irrelevance detection demo)",
    },
    # ── Late hours request ───────────────────────────────────────────────────
    {
        "text": (
            "Please consider extending the library's opening hours to midnight, "
            "at least during finals week. Many students need a quiet place to "
            "study late into the night and the current 9 PM closing time is too early."
        ),
        "note": "Facility request – late hours",
    },
    # ── General positive feedback ────────────────────────────────────────────
    {
        "text": (
            "The new self-checkout kiosks are fantastic! They save so much time "
            "compared to waiting in line at the desk. Well done to the library team "
            "for implementing them."
        ),
        "note": "Positive feedback – self-checkout kiosks",
    },
    # ── Inappropriate / blocked-term comment ────────────────────────────────
    {
        "text": (
            "This library is absolutely useless and the staff are complete idiots "
            "who have no idea what they are doing."
        ),
        "note": "Inappropriate – blocked terms / disrespectful",
    },
]

REVIEWS = [
    # (book_isbn, user_email, rating, body)
    ("9780132350884", "student@library.edu", 5, "A must-read for any developer. Changed the way I write code."),
    ("9780135957059", "student@library.edu", 4, "Packed with practical wisdom. A bit dated in places but mostly timeless."),
    ("9780262033848", "student@library.edu", 4, "Dense but essential. Great reference during my algorithms course."),
    ("9781593279288", "student@library.edu", 5, "Perfect for beginners. Clear explanations and fun projects."),
    ("9781492056355", "librarian@library.edu", 5, "Outstanding. The best book for understanding Python deeply."),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_user(email: str, name: str, role: str, password: str) -> tuple[User, bool]:
    """Return (user, created). Does NOT commit."""
    existing = User.query.filter_by(email=email).first()
    if existing:
        return existing, False
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    return user, True


def _get_or_create_book(data: dict) -> tuple[Book, bool]:
    """Return (book, created). Does NOT commit."""
    existing = Book.query.filter_by(isbn=data["isbn"]).first()
    if existing:
        return existing, False
    book = Book(**data)
    db.session.add(book)
    return book, True


# ---------------------------------------------------------------------------
# Main seeding function
# ---------------------------------------------------------------------------

def seed_database() -> None:
    """Populate the database with demo seed data (idempotent)."""

    print("\n" + "=" * 60)
    print("  LIBRARY MANAGEMENT SYSTEM — SEED DATA")
    print("  Development / demo data only. Do not use in production.")
    print("=" * 60 + "\n")

    # ── Users ────────────────────────────────────────────────────────────────
    print("▶  Creating users …")
    created_users: dict[str, User] = {}
    for spec in USERS:
        user, created = _get_or_create_user(
            email=spec["email"],
            name=spec["name"],
            role=spec["role"],
            password=spec["password"],
        )
        db.session.flush()  # get the ID without a full commit
        status = "CREATED" if created else "EXISTS "
        print(f"   [{status}] {spec['role']:10s}  {spec['email']}")
        created_users[spec["email"]] = user

    db.session.commit()
    print()

    # ── Books ────────────────────────────────────────────────────────────────
    print("▶  Creating books …")
    created_books: dict[str, Book] = {}
    for spec in BOOKS:
        book, created = _get_or_create_book(spec)
        db.session.flush()
        status = "CREATED" if created else "EXISTS "
        print(f"   [{status}] {spec['title']}")
        created_books[spec["isbn"]] = book

    db.session.commit()
    print()

    # ── Reviews ─────────────────────────────────────────────────────────────
    print("▶  Creating reviews …")
    for isbn, user_email, rating, body in REVIEWS:
        book = created_books.get(isbn)
        user = created_users.get(user_email)
        if book is None or user is None:
            print(f"   [SKIP   ] Review skipped — book or user not found ({isbn})")
            continue

        existing = Review.query.filter_by(book_id=book.id, user_id=user.id).first()
        if existing:
            print(f"   [EXISTS ] Review by {user_email} for '{book.title}'")
            continue

        review = Review(
            book_id=book.id,
            user_id=user.id,
            rating=rating,
            body=body,
        )
        db.session.add(review)
        db.session.flush()
        print(f"   [CREATED] ★{rating} review by {user_email} for '{book.title}'")

    db.session.commit()
    print()

    # ── Comments ─────────────────────────────────────────────────────────────
    print("▶  Creating and processing comments …")
    student = created_users.get("student@library.edu")
    if student is None:
        print("   [ERROR] Student user not found — skipping comments.")
    else:
        for i, spec in enumerate(COMMENTS, start=1):
            text = spec["text"]
            note = spec["note"]

            # Idempotency: skip if this exact text already exists for this user
            existing = Comment.query.filter_by(user_id=student.id, text=text).first()
            if existing:
                print(f"   [EXISTS ] Comment {i:02d}: {note}")
                continue

            comment = Comment(user_id=student.id, text=text)
            db.session.add(comment)
            db.session.flush()  # populate comment.id before pipeline

            # Run through the AI/NLP comment pipeline
            try:
                process_comment(comment)
            except Exception as exc:  # noqa: BLE001
                # Pipeline errors should not abort the entire seed
                print(f"   [WARN   ] Pipeline error for comment {i:02d}: {exc}")

            db.session.commit()
            status_label = getattr(comment, "status", "unknown")
            category_label = getattr(comment, "category", "uncategorized")
            print(
                f"   [CREATED] Comment {i:02d}: {note}\n"
                f"             status={status_label!r}  category={category_label!r}"
            )

    print()
    print("=" * 60)
    print("  Seed complete.")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    flask_app = create_app(os.getenv("FLASK_ENV", "development"))
    with flask_app.app_context():
        seed_database()
