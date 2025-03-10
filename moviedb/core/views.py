"""Core views."""

from flask import Blueprint, render_template
from flask.views import MethodView
from .func import list_movies

blueprint = Blueprint("core", __name__)


class IndexView(MethodView):
    def get(self):
        print(list_movies())
        return render_template("index.html")


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)
