"""Auth views."""

from flask import Blueprint, render_template
from flask.views import MethodView

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class LoginView(MethodView):
    def get(self):
        return render_template("login.html")


login_view = LoginView.as_view("login")
blueprint.add_url_rule("/login", view_func=login_view)
