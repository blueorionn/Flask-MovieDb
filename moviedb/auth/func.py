import os
import bcrypt
import pymongo
import jwt
import datetime
from datetime import timedelta
from moviedb.utils import is_valid_uuid_v4
from pymongo.collection import Collection


def authenticate_user(username: str, password: str):
    """Check if user exists with valid credentials."""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # auth database
    auth_db = mongo_client["auth"]

    # user collection
    user_collection: Collection = auth_db["user"]

    # getting user
    user = user_collection.find_one({"username": username})

    # If user exist
    if user is not None and isinstance(user, dict):
        # Checking if password is correct
        fetched_user_id, fetched_username = (user["id"], user["username"])
        fetched_password: str = user["password"]

        if (
            (bcrypt.checkpw(password.encode("utf-8"), fetched_password.encode("utf-8")))
            and (username == fetched_username)
            and is_valid_uuid_v4(fetched_user_id)
        ):
            return True
        else:
            return False
    else:
        return False


def fetch_user_id(username: str):
    """Fetch user id from username."""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # auth database
    auth_db = mongo_client["auth"]

    # user collection
    user_collection: Collection = auth_db["user"]

    # getting user
    user = user_collection.find_one({"username": username})

    if user is not None and isinstance(user, dict):
        return user["id"]
    else:
        return None


def create_jwt_token(username: str):
    """Create JWT token for user."""

    if not username or not isinstance(username, str):
        raise ValueError("Username must be a non-empty string.")

    return jwt.encode(
        {
            "user_id": fetch_user_id(username),
            "user": username,
            "exp": datetime.datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.datetime.utcnow(),
        },
        os.environ.get("SECRET_KEY"),
        algorithm="HS256",
    )


def decode_jwt_token(token: str):
    """Decode JWT token and return user information."""

    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string.")

    if os.environ.get("SECRET_KEY") is None:
        raise ValueError("SECRET_KEY environment variable is not set.")

    try:
        return jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms="HS256")
    except:
        return {}
