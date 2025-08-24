"""Core views."""

import os
import uuid
from flask import current_app, request, Blueprint, render_template, send_file, redirect
from flask.views import MethodView
from moviedb.auth.func import authenticate_jwt_token, decode_jwt_token
from .func import kebab_case, list_movies, get_movie, create_movie, update_movie

blueprint = Blueprint("core", __name__)


class IndexView(MethodView):
    def get(self):
        movies = list_movies()
        context = {"movies": movies}
        return render_template("index.html", **context)


class CreateMovie(MethodView):
    def get(self):
        """Render the create movie page."""
        return render_template("create.html")

    def post(self):
        """Create a new movie."""
        # User data and generated id
        user = decode_jwt_token(request.cookies.get("token"))
        id = str(uuid.uuid4())

        # Movie data from form
        title = request.form.get("title")
        release_year = request.form.get("release_year")
        rating = request.form.get("rating")
        genre = request.form.get("genre")
        description = request.form.get("description")
        is_private = request.form.get("is_private")
        poster = request.files.get("poster")

        if authenticate_jwt_token(request.cookies.get("token")) is None:
            return render_template(
                "handlers/handler.html",
                context={"error_code": 401, "error_message": "Unauthorized"},
            )
        elif user is None or user.get("id") is None:
            return render_template(
                "handlers/handler.html",
                context={"error_code": 401, "error_message": "Unauthorized"},
            )
        else:
            # save poster
            poster_filename = kebab_case(f"{poster.filename}")
            try:
                poster.save(
                    os.path.join(
                        current_app.config["APP_DIR"], f"assets/{poster_filename}"
                    )
                )
            except Exception as e:
                return render_template(
                    "create.html",
                    context={"error": f"Failed to save poster: {str(e)}"},
                )

            # Processing data and saving to database
            if is_private is None:
                is_private = False
            else:
                is_private = True

            try:
                release_year = int(release_year)
                rating = float(rating)
                create_movie(
                    id,
                    user["id"],
                    title,
                    release_year,
                    rating,
                    genre,
                    poster_filename,
                    description,
                    is_private,
                )
            except ValueError:
                return render_template(
                    "handlers/handler.html",
                    context={
                        "error_code": 500,
                        "error_message": "Internal Server Error",
                    },
                )

            return redirect(f"/movie/{id}/")


index_view = IndexView.as_view("home")
blueprint.add_url_rule("/", view_func=index_view)

create_view = CreateMovie.as_view("create_movie")
blueprint.add_url_rule("/movie/create/", view_func=create_view)


@blueprint.route("/movie/poster/<filename>")
def serve_poster(filename):
    path = os.path.join(current_app.config["APP_DIR"], f"assets/{filename}")

    return send_file(path, mimetype="image/jpg")
