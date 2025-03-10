"""Core views."""

import os
from flask import current_app, Blueprint, render_template, send_file
from flask.views import MethodView
from .func import list_movies

blueprint = Blueprint("core", __name__)


class IndexView(MethodView):
    def get(self):
        movies = list_movies()
        context = {"movies": movies}
        return render_template("index.html", **context)


@blueprint.route("/movie/poster/<filename>")
def serve_poster(filename):
    path = os.path.join(current_app.config["APP_DIR"], f"assets/{filename}")

    return send_file(path, mimetype="image/jpg")


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)
