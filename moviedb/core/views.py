"""Core views."""

from flask import Blueprint, render_template
from flask.views import MethodView

blueprint = Blueprint("core", __name__)


class IndexView(MethodView):
    def get(self):
        return render_template("index.html")


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)
