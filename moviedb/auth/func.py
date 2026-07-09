import bcrypt
from pymongo.collection import Collection
from moviedb.utils import is_valid_uuid_v4
from moviedb.extensions import get_db


def authenticate_user(username: str, password: str):
    """Check if user exists with valid credentials."""
    db = get_db()
    user_collection: Collection = db["auth"]
    user = user_collection.find_one({"username": username})

    if user is None or not isinstance(user, dict):
        return False

    fetched_user_id = user["id"]
    fetched_username = user["username"]
    fetched_password: str = user["password"]

    return (
        bcrypt.checkpw(password.encode("utf-8"), fetched_password.encode("utf-8"))
        and username == fetched_username
        and is_valid_uuid_v4(fetched_user_id)
    )


def fetch_user(username: str):
    """Fetch user details from username."""

    # Database
    db = get_db()
    user_collection: Collection = db["auth"]

    # getting user
    user = user_collection.find_one({"username": username})

    if user is not None and isinstance(user, dict):
        return user
    else:
        return None
