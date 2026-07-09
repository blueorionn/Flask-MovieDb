"""Unit tests for authenticate_user and fetch_user"""

import bcrypt
import mongomock
from moviedb.auth.func import authenticate_user, fetch_user


def _seeded_db():
    pw = bcrypt.hashpw("testpass123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    client = mongomock.MongoClient()
    db = client["testdb"]
    db.auth.insert_one(
        {
            "id": "48bb52b9-75a7-4b77-ba6a-36b0be0fb8c5",
            "first_name": "Alice",
            "last_name": "Rondo",
            "username": "testuser",
            "password": pw,
            "role": "admin",
            "created_at": "2026-01-01 00:00:00.000000",
        }
    )

    import moviedb.auth.func as mod

    mod.get_db = lambda: db  # Mock get_db to return our seeded db


class TestAuthenticateUser:
    def test_valid(self):
        _seeded_db()
        assert authenticate_user("testuser", "testpass123") is True

    def test_bad_username(self):
        _seeded_db()
        assert authenticate_user("nobody", "testpass123") is False

    def test_bad_password(self):
        _seeded_db()
        assert authenticate_user("testuser", "wrong") is False

    def test_empty_username(self):
        _seeded_db()
        assert authenticate_user("", "testpass123") is False


class TestFetchUser:
    def test_exists(self):
        _seeded_db()
        u = fetch_user("testuser")
        assert u["username"] == "testuser"
        assert u["role"] == "admin"

    def test_not_found(self):
        _seeded_db()
        assert fetch_user("ghost") is None
