"""Application Middleware"""

import os
import time
import pymongo
from flask import request, redirect
from moviedb.auth.func import decode_jwt_token


def authentication_middleware():
    """
    Middleware to run before every request.
    """

    # Allow css files even for non logged in user
    if request.path in ["/static/styles/style.css", "/static/styles/base.css"]:
        return

    if request.path == "/auth/login":
        token = str(request.cookies.get("token"))
        if not is_token_valid(token):
            return
        else:
            return redirect("/")  # Redirect to home if user logged in.

    if "token" in request.cookies:
        token = str(request.cookies.get("token"))
        if not is_token_valid(token):
            return redirect("/auth/login")
        return
    else:
        return redirect("/auth/login")


def is_token_valid(token: str):
    data = decode_jwt_token(token)

    if (
        not "user" in data.keys()
        or (not "iat" in data.keys())
        or (not "exp" in data.keys())
    ):
        return False

    username = data["user"]
    exp = data["exp"]

    # if token has expired
    if int(time.time()) > exp:
        return False

    # creating mongoclient
    client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # auth database
    db = client["auth"]

    # user collection
    user_collection = db["user"]

    # username should be unique
    fetched_user = user_collection.find_one({"username": username})

    if isinstance(fetched_user, dict) and fetched_user.get("username") == username:
        return True
    else:
        return False
