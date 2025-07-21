"""Auth views."""

import datetime
from flask import request, Blueprint, render_template, make_response, redirect
from flask.views import MethodView
from .func import (
    authenticate_user,
    create_jwt_token,
    authenticate_jwt_token,
)

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class LoginView(MethodView):
    def get(self):
        return render_template("auth/login.html")

    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        if authenticate_user(username, password):
            res = make_response(redirect("/"))
            token = create_jwt_token(username)
            res.set_cookie("token", token, max_age=3600, httponly=False, samesite="Lax")
            return res
        else:
            message = {"message": "Username or password is invalid. "}
            return render_template("auth/login.html", **message)


class ProfileView(MethodView):
    def get(self):

        if authenticate_jwt_token(request.cookies.get("token")) is None:
            return render_template(
                "handlers/handler.html",
                context={"error_code": 401, "error_message": "Unauthorized"},
            )
        else:
            # user details
            user = authenticate_jwt_token(request.cookies.get("token"))
            user["created_at"] = datetime.datetime.strptime(
                user["created_at"], "%Y-%m-%d %H:%M:%S.%f"
            )
            context = {"user": user}
            return render_template("profile/profile.html", **context)


login_view = LoginView.as_view("login")
blueprint.add_url_rule("/login", view_func=login_view)

profile_view = ProfileView.as_view("profile")
blueprint.add_url_rule("/user/profile", view_func=profile_view)
