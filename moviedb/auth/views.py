"""Auth views."""

import datetime
from flask import request, Blueprint, render_template, make_response, redirect, url_for
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from moviedb.extensions import limiter
from .func import authenticate_user, fetch_user

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class LoginView(MethodView):
    def get(self):
        return render_template("auth/login.html")

    @limiter.limit("20 per minute")
    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        if authenticate_user(username, password):
            user = fetch_user(username)
            additional_claims = {"role": user["role"], "id": user["id"]}
            token = create_access_token(
                identity=username, additional_claims=additional_claims
            )
            res = make_response(redirect(url_for("core.home")))
            set_access_cookies(res, token)
            return res
        else:
            message = {"message": "Username or password is invalid."}
            return render_template("auth/login.html", **message), 400


class LogoutView(MethodView):
    def get(self):
        res = make_response(redirect(url_for("core.home")))
        unset_jwt_cookies(res)
        return res


class ProfileView(MethodView):
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        claims = get_jwt()
        user = fetch_user(username)
        if user:
            user["created_at"] = datetime.datetime.strptime(
                str(user["created_at"]), "%Y-%m-%d %H:%M:%S.%f"
            )
            user["role"] = claims.get("role", user.get("role"))
            return render_template("profile/profile.html", user=user)
        return render_template(
            "handlers/handler.html",
            context={"error_code": 404, "error_message": "User not found."},
        )


login_view = LoginView.as_view("login")
blueprint.add_url_rule("/login", view_func=login_view)

logout_view = LogoutView.as_view("logout")
blueprint.add_url_rule("/logout", view_func=logout_view)

profile_view = ProfileView.as_view("profile")
blueprint.add_url_rule("/user/profile", view_func=profile_view)
