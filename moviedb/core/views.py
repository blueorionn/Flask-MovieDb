"""Core views."""

import os
from flask import current_app, request, Blueprint, render_template, send_file
from flask.views import MethodView
from moviedb.auth.func import decode_jwt_token
from .func import get_user_by_id, list_movies, get_movie, update_movie

blueprint = Blueprint("core", __name__)


class IndexView(MethodView):
    def get(self):
        movies = list_movies()
        context = {"movies": movies}
        return render_template("index.html", **context)


class ProfileView(MethodView):
    def get(self):

        if request.cookies.get("token") is not None:
            token = request.cookies.get("token")
            user_id = decode_jwt_token(token)["user_id"]

        context = {"user": get_user_by_id(user_id)}
        print(context, user_id)
        return render_template("profile/profile.html", **context)


@blueprint.route("/movie/poster/<filename>")
def serve_poster(filename):
    path = os.path.join(current_app.config["APP_DIR"], f"assets/{filename}")

    return send_file(path, mimetype="image/jpg")


class UpdateMovie(MethodView):
    def get(self, movie_id):
        # get movie
        movie = get_movie(str(movie_id))
        context = {"movie": movie}
        return render_template("update.html", **context)

    def post(self, movie_id):
        title = request.form.get("title")
        release_year = request.form.get("release_year")
        rating = request.form.get("rating")
        genre = request.form.get("genre")
        poster = request.form.get("poster")
        description = request.form.get("description")

        # update document
        update_movie(
            str(movie_id),
            {
                "title": title,
                "release_year": release_year,
                "rating": rating,
                "genre": genre,
                "poster": poster,
                "description": description,
            },
        )

        # requesting for updated movie object
        movie = get_movie(str(movie_id))
        context = {"movie": movie}
        return render_template("movie.html", **context)


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)

update_view = UpdateMovie.as_view("update_movie")
blueprint.add_url_rule("/update/<uuid:movie_id>", view_func=update_view)

profile_view = ProfileView.as_view("profile")
blueprint.add_url_rule("/user/profile", view_func=profile_view)
