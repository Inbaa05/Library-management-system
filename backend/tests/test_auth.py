"""
Tests for authentication endpoints.

Covers: registration, login, /me, and password-change flows.
"""

import pytest
from tests.conftest import auth_headers


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:
    """POST /api/v1/auth/register"""

    ENDPOINT = "/api/v1/auth/register"

    def test_register_student_success(self, client):
        """A new student can register with valid credentials."""
        payload = {
            "name": "Jane Doe",
            "email": "jane.doe@university.edu",
            "password": "Secure@Pass1",
            "role": "student",
        }
        response = client.post(self.ENDPOINT, json=payload)
        data = response.get_json()

        assert response.status_code == 201, data
        assert data["status"] == "success"
        assert "token" in data["data"]
        assert data["data"]["user"]["email"] == payload["email"]
        assert data["data"]["user"]["role"] == "student"

    def test_register_duplicate_email(self, client, student_user):
        """Registering with an already-used e-mail returns 409 Conflict."""
        payload = {
            "name": "Duplicate User",
            "email": student_user.email,   # same e-mail as the fixture user
            "password": "Secure@Pass1",
            "role": "student",
        }
        response = client.post(self.ENDPOINT, json=payload)
        data = response.get_json()

        assert response.status_code == 409, data
        assert data["status"] == "error"

    def test_register_invalid_email(self, client):
        """A malformed e-mail address returns 422 Unprocessable Entity."""
        payload = {
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "Secure@Pass1",
            "role": "student",
        }
        response = client.post(self.ENDPOINT, json=payload)
        data = response.get_json()

        assert response.status_code == 422, data
        assert data["status"] == "error"

    def test_register_weak_password(self, client):
        """A password that fails the strength policy returns 422."""
        payload = {
            "name": "Weak Pass",
            "email": "weakpass@university.edu",
            "password": "abc",          # too short, no uppercase, no special char
            "role": "student",
        }
        response = client.post(self.ENDPOINT, json=payload)
        data = response.get_json()

        assert response.status_code == 422, data
        assert data["status"] == "error"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    """POST /api/v1/auth/login"""

    ENDPOINT = "/api/v1/auth/login"

    def test_login_success(self, client, student_user):
        """Valid credentials return a JWT token and user info."""
        response = client.post(self.ENDPOINT, json={
            "email": student_user.email,
            "password": "TestPass@123",
        })
        data = response.get_json()

        assert response.status_code == 200, data
        assert data["status"] == "success"
        assert "token" in data["data"]
        assert data["data"]["user"]["email"] == student_user.email

    def test_login_invalid_password(self, client, student_user):
        """Wrong password returns 401 Unauthorized."""
        response = client.post(self.ENDPOINT, json={
            "email": student_user.email,
            "password": "WrongPassword!9",
        })
        data = response.get_json()

        assert response.status_code == 401, data
        assert data["status"] == "error"

    def test_login_nonexistent_email(self, client):
        """Logging in with an e-mail that does not exist returns 401."""
        response = client.post(self.ENDPOINT, json={
            "email": "nobody@nowhere.edu",
            "password": "Irrelevant@1",
        })
        data = response.get_json()

        assert response.status_code == 401, data
        assert data["status"] == "error"


# ---------------------------------------------------------------------------
# /me — current user
# ---------------------------------------------------------------------------

class TestGetMe:
    """GET /api/v1/auth/me"""

    ENDPOINT = "/api/v1/auth/me"

    def test_get_me_authenticated(self, client, student_user):
        """An authenticated user can retrieve their own profile."""
        headers = auth_headers(client, student_user.email, "TestPass@123")
        response = client.get(self.ENDPOINT, headers=headers)
        data = response.get_json()

        assert response.status_code == 200, data
        assert data["status"] == "success"
        assert data["data"]["user"]["email"] == student_user.email
        assert data["data"]["user"]["role"] == "student"

    def test_get_me_unauthenticated(self, client):
        """A request without a token returns 401 Unauthorized."""
        response = client.get(self.ENDPOINT)
        data = response.get_json()

        assert response.status_code == 401, data
        assert data["status"] == "error"


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------

class TestChangePassword:
    """POST /api/v1/auth/change-password"""

    ENDPOINT = "/api/v1/auth/change-password"

    def test_change_password_success(self, client, student_user):
        """A user can change their password with correct old password."""
        headers = auth_headers(client, student_user.email, "TestPass@123")
        response = client.post(
            self.ENDPOINT,
            json={
                "old_password": "TestPass@123",
                "new_password": "NewSecure@456",
            },
            headers=headers,
        )
        data = response.get_json()

        assert response.status_code == 200, data
        assert data["status"] == "success"

        # Verify the new password actually works for login
        login_resp = client.post("/api/v1/auth/login", json={
            "email": student_user.email,
            "password": "NewSecure@456",
        })
        assert login_resp.status_code == 200

    def test_change_password_wrong_old(self, client, student_user):
        """Supplying the wrong old password returns 401."""
        headers = auth_headers(client, student_user.email, "TestPass@123")
        response = client.post(
            self.ENDPOINT,
            json={
                "old_password": "CompletelyWrong@9",
                "new_password": "NewSecure@456",
            },
            headers=headers,
        )
        data = response.get_json()

        assert response.status_code == 401, data
        assert data["status"] == "error"
