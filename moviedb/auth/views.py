"""Auth views."""

from flask import request, Blueprint, render_template, make_response, redirect
from flask.views import MethodView
from .func import authenticate_user

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class LoginView(MethodView):
    def get(self):
        return render_template("login.html")

    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        if authenticate_user(username, password):
            res = make_response(redirect("/"))
            return res
        else:
            message = {"message": "Username or password is invalid. "}
            return render_template("login.html", **message)
        

login_view = LoginView.as_view("login")
blueprint.add_url_rule("/login", view_func=login_view)
