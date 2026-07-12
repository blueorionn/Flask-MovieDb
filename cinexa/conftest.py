import os
import uuid
import bcrypt
import mongomock
import pytest
from cinexa import create_app
from cinexa.settings import TestingConfig

TEST_USER_ID = str(uuid.uuid1())
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"
TEST_PASSWORD_HASH = bcrypt.hashpw(
    TEST_PASSWORD.encode("utf-8"), bcrypt.gensalt()
).decode("utf-8")

TEST_USER_DOC = {
    "id": TEST_USER_ID,
    "firstname": "Test",
    "lastname": "User",
    "username": TEST_USERNAME,
    "password": TEST_PASSWORD_HASH,
    "role": "user",
    "created_at": "2026-01-01 00:00:00.000000",
}


class _MockMongoClient(mongomock.MongoClient):
    """mongomock doesn't implement server_info() — Flask-JWT-Extended >=4.7
    calls it, so we return a fake response."""

    def server_info(self):
        return {"version": "7.0.0", "ok": 1.0}


# Replace pymongo.MongoClient BEFORE create_app() imports extensions
import cinexa.extensions as _ext

_ext.pymongo.MongoClient = _MockMongoClient


@pytest.fixture(scope="function")
def app():
    os.environ["SECRET_KEY"] = "56=gvSt*,hl7XYJ_"

    config = TestingConfig()
    config.MONGO_URI = "mongodb://localhost:27017/testdb"
    config.WTF_CSRF_ENABLED = False
    config.RATELIMIT_ENABLED = False
    config.SERVER_NAME = "localhost"

    flask_app = create_app(config_object=config)

    with flask_app.app_context():
        from cinexa.extensions import get_db

        get_db().auth.insert_one(TEST_USER_DOC.copy())

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def auth_client(client):
    resp = client.post(
        "/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert resp.status_code == 302, f"Login failed: {resp.status_code}"
    return client
