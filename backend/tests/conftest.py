"""Pytest configuration and fixtures for backend tests."""
import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """Create a Flask test application with an in-memory SQLite database."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database for each test (rolls back after each test)."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        yield _db
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app, db):
    """Test client with a clean database."""
    return app.test_client()


@pytest.fixture
def student_user(db):
    """Create a student user for testing."""
    user = User(name='Test Student', email='student@test.com', role='student')
    user.set_password('TestPass@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def librarian_user(db):
    """Create a librarian user for testing."""
    user = User(name='Test Librarian', email='librarian@test.com', role='librarian')
    user.set_password('LibPass@123')
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(client, email: str, password: str) -> dict:
    """Log in and return Authorization headers."""
    response = client.post('/api/v1/auth/login', json={
        'email': email,
        'password': password
    })
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}
