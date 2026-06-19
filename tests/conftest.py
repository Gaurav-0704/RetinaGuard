"""
Shared fixtures for the RetinaGuard test suite.

I use an in-memory SQLite database so tests never touch the real retinoguard.db,
and a temporary uploads directory so no files spill outside the test run.
"""

import io
import os
import tempfile
import pytest

from backend.app import create_app
from backend.database import db as _db
from backend.models.user import User
from backend.models.scan import Scan


@pytest.fixture(scope="session")
def app():
    tmp_dir = tempfile.mkdtemp()
    os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"

    app = create_app("development")
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        UPLOAD_FOLDER=tmp_dir,
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    """Yields the SQLAlchemy db instance inside an app context."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture()
def patient_user(db):
    user = User(full_name="Test Patient", email="patient@test.com", role="patient")
    user.set_password("testpass1")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


@pytest.fixture()
def doctor_user(db):
    user = User(full_name="Test Doctor", email="doctor@test.com", role="doctor")
    user.set_password("testpass1")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def png_bytes():
    """Minimal 1×1 white PNG for upload tests."""
    import struct, zlib
    def chunk(name, data):
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
    iend = chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend
