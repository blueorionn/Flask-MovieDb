"""Core views."""

import os
import uuid
from flask import current_app, request, Blueprint, render_template, redirect
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request,
)
from flask.views import MethodView
from werkzeug.utils import secure_filename

from cinexa.utils import kebab_case, upload_to_s3
from .func import list_movies, get_movie, create_movie, update_movie, list_series

blueprint = Blueprint("core", __name__)


@blueprint.route("/movie/poster/<filename>")
def serve_poster(filename):
    folder_prefix = "posters"
    path = os.path.join(current_app.config["S3_BUCKET_URI"], folder_prefix, filename)
    return redirect(path)


class MoviesView(MethodView):
    def get(self):
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            if claims:
                user_id = claims.get("id")
        except Exception:
            pass

        filter = (
            {"$or": [{"is_private": False}, {"created_by": user_id}]}
            if user_id
            else {"is_private": False}
        )
        movies = list_movies(filter)
        return render_template("index.html", movies=movies)


class CreateView(MethodView):
    @jwt_required()
    def get(self):
        return render_template("misc/create.html", context={})


class YourMovies(MethodView):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        user_id = claims.get("id")
        movies = list_movies({"created_by": user_id})
        return render_template("index.html", movies=movies)


class GetMovie(MethodView):
    def get(self, id):
        movie = get_movie(id)
        if movie is None:
            return (
                render_template(
                    "handlers/handler.html",
                    context={"error_code": 404, "error_message": "Movie Not Found"},
                ),
                404,
            )
        return render_template("movie/movie.html", movie=movie)


class CreateMovie(MethodView):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        user_id = claims.get("id")
        movie_id = str(uuid.uuid4())

        title = request.form.get("title")
        release_year = request.form.get("release_year")
        rating = request.form.get("rating")
        genre = request.form.get("genre")
        description = request.form.get("description")
        is_private = request.form.get("is_private")
        poster = request.files.get("poster")

        # upload poster to S3
        poster_filename = kebab_case(f"{secure_filename(poster.filename)}")
        poster_path = "project-cinexa/posters/"
        try:
            poster.seek(0)
            upload_to_s3(
                poster,
                f"{poster_path}{poster_filename}",
                content_type=poster.content_type,
            )
        except Exception:
            return (
                render_template(
                    "misc/create.html",
                    context={"error": "Failed to upload poster: S3Error"},
                ),
                500,
            )

        if is_private is None:
            is_private = False
        else:
            is_private = True

        try:
            release_year = int(release_year)
            rating = float(rating)
            create_movie(
                movie_id,
                user_id,
                title,
                release_year,
                rating,
                genre,
                poster_filename,
                description,
                is_private,
            )
        except ValueError:
            return (
                render_template(
                    "handlers/handler.html",
                    context={
                        "error_code": 500,
                        "error_message": "Internal Server Error",
                    },
                ),
                500,
            )

        return redirect(f"/movie/{movie_id}/")


class UpdateMovie(MethodView):
    @jwt_required()
    def get(self, id):
        movie = get_movie(id)
        if movie is None:
            return (
                render_template(
                    "handlers/handler.html",
                    context={"error_code": 404, "error_message": "Movie Not Found"},
                ),
                404,
            )

        claims = get_jwt()
        if claims.get("id") != movie.get("created_by"):
            return (
                render_template(
                    "handlers/handler.html",
                    context={"error_code": 401, "error_message": "Unauthorized"},
                ),
                401,
            )

        return render_template("movie/update.html", movie=movie)

    @jwt_required()
    def post(self, id):
        title = request.form.get("title")
        release_year = request.form.get("release_year")
        rating = request.form.get("rating")
        genre = request.form.get("genre")
        description = request.form.get("description")
        is_private = request.form.get("is_private")

        if is_private is None:
            is_private = False
        else:
            is_private = True

        try:
            release_year = int(release_year)
            rating = float(rating)
            update_movie(
                movie_id=id,
                movie_data={
                    "title": title,
                    "release_year": release_year,
                    "rating": rating,
                    "genre": genre,
                    "description": description,
                    "is_private": is_private,
                },
            )
        except ValueError:
            return (
                render_template(
                    "handlers/handler.html",
                    context={
                        "error_code": 500,
                        "error_message": "Internal Server Error",
                    },
                ),
                500,
            )

        return redirect(f"/movie/{id}/")


class SeriesView(MethodView):
    def get(self):
        series = list_series({"is_private": False})
        return render_template("series/series.html", series=series)


create_view = CreateView.as_view("create")
blueprint.add_url_rule("/create/", view_func=create_view)

movies_view = MoviesView.as_view("home")
blueprint.add_url_rule("/", view_func=movies_view)

your_movies_view = YourMovies.as_view("your_movies")
blueprint.add_url_rule("/movies/", view_func=your_movies_view)

get_movie_view = GetMovie.as_view("get_movie")
blueprint.add_url_rule("/movie/<id>/", view_func=get_movie_view)

create_movie_view = CreateMovie.as_view("create_movie")
blueprint.add_url_rule("/movie/create/", view_func=create_movie_view)

update_view = UpdateMovie.as_view("update_movie")
blueprint.add_url_rule("/movie/update/<id>/", view_func=update_view)

series_view = SeriesView.as_view("series")
blueprint.add_url_rule("/series/", view_func=series_view)
