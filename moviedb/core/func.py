"""Functions for view"""

from pymongo.collection import Collection
from moviedb.extensions import get_db


def get_user_by_id(user_id: str):
    """Get User by Id"""

    # Database
    db = get_db()
    user_collection: Collection = db.auth

    # getting user
    user = user_collection.find_one({"id": user_id})

    return user


def list_movies(filter={}):
    """List all movies"""

    # Database
    db = get_db()
    movie_collection: Collection = db.movie

    # getting movies
    movies = list(movie_collection.find(filter))

    return movies


def get_movie(id: str):
    """Get Movie by Id"""

    # Database
    db = get_db()
    movie_collection: Collection = db.movie

    # getting movies
    movie = movie_collection.find_one({"id": id})

    return movie


def create_movie(
    id: str,
    user_id: str,
    title: str,
    release_year: int,
    rating: float,
    genre: str,
    poster: str,
    description: str,
    is_private: bool,
):
    """Create a new movie document"""

    # Database
    db = get_db()
    movie_collection: Collection = db.movie

    # insert document
    movie_collection.insert_one(
        {
            "id": id,
            "created_by": user_id,
            "is_private": is_private,
            "title": title,
            "release_year": release_year,
            "rating": rating,
            "genre": genre,
            "poster": poster,
            "description": description,
        }
    )

    return True


def update_movie(movie_id: str, movie_data={}):
    """Update the movie document"""

    # Database
    db = get_db()
    movie_collection: Collection = db.movie

    # update document
    movie_collection.update_one({"id": movie_id}, {"$set": movie_data})

    return True


def kebab_case(text: str) -> str:
    """Convert text to kebab case"""
    return text.lower().replace(" ", "-")
