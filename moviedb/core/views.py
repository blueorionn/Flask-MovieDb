"""Core views."""

import os
from flask import current_app, request, Blueprint, render_template, send_file
from flask.views import MethodView
from .func import list_movies, get_movie

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


class UpdateMovie(MethodView):
    def get(self, movie_id):
        # get movie
        movie = get_movie(str(movie_id))
        context = {"movie": movie}
        return render_template("movie.html", **context)


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)

update_view = UpdateMovie.as_view("update_movie")
blueprint.add_url_rule("/movie/<uuid:movie_id>", view_func=update_view)