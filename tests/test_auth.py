"""
Tests for authentication routes: register, login, logout.
I test the happy path, duplicate emails, bad passwords, and session isolation.
"""

import pytest
from tests.conftest import login, logout


class TestRegister:
    def test_register_new_user(self, client, db):
        resp = client.post(
            "/register",
            data={
                "full_name": "Alice Smith",
                "email": "alice@example.com",
                "password": "securepass1",
                "confirm_password": "securepass1",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Alice Smith" in resp.data or b"profile" in resp.request.url.encode()

    def test_register_duplicate_email(self, client, patient_user):
        resp = client.post(
            "/register",
            data={
                "full_name": "Dup User",
                "email": patient_user.email,
                "password": "securepass1",
                "confirm_password": "securepass1",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"already exists" in resp.data

    def test_register_mismatched_passwords(self, client):
        resp = client.post(
            "/register",
            data={
                "full_name": "Bob",
                "email": "bob@example.com",
                "password": "securepass1",
                "confirm_password": "different",
            },
            follow_redirects=True,
        )
        assert b"do not match" in resp.data

    def test_register_short_password(self, client):
        resp = client.post(
            "/register",
            data={
                "full_name": "Carol",
                "email": "carol@example.com",
                "password": "abc",
                "confirm_password": "abc",
            },
            follow_redirects=True,
        )
        assert b"8 characters" in resp.data


class TestLogin:
    def test_login_valid_credentials(self, client, patient_user):
        resp = login(client, patient_user.email, "testpass1")
        assert resp.status_code == 200
        assert b"dashboard" in resp.request.url.encode() or b"Dashboard" in resp.data

    def test_login_wrong_password(self, client, patient_user):
        resp = login(client, patient_user.email, "wrongpassword")
        assert b"Invalid email or password" in resp.data

    def test_login_unknown_email(self, client):
        resp = login(client, "nobody@nowhere.com", "doesntmatter")
        assert b"Invalid email or password" in resp.data

    def test_login_redirects_authenticated_user(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        resp = client.get("/login", follow_redirects=False)
        assert resp.status_code == 302

    def test_logout_clears_session(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        resp = logout(client)
        assert resp.status_code == 200
        # After logout, accessing dashboard should redirect to login
        resp2 = client.get("/dashboard/", follow_redirects=False)
        assert resp2.status_code == 302
        assert "login" in resp2.headers["Location"]


class TestLanding:
    def test_landing_accessible_unauthenticated(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_landing_redirects_authenticated(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        logout(client)
