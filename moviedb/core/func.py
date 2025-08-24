"""Functions for view"""

import os
import pymongo
from pymongo.collection import Collection


def get_user_by_id(user_id: str):
    """Get User by Id"""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # auth database
    auth_db = mongo_client["auth"]

    # user collection
    user_collection: Collection = auth_db["user"]

    # getting user
    user = user_collection.find_one({"id": user_id})

    return user


def list_movies(filter = {}):
    """List all movies"""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # movies database
    movies_db = mongo_client["movies"]

    # movie collection
    movie_collection: Collection = movies_db["movie"]

    # getting movies
    movies = list(movie_collection.find(filter))

    return movies


def get_movie(id: str):
    """Get Movie by Id"""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # movies database
    movies_db = mongo_client["movies"]

    # movie collection
    movie_collection: Collection = movies_db["movie"]

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

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # movies database
    movies_db = mongo_client["movies"]

    # movie collection
    movie_collection: Collection = movies_db["movie"]

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


def update_movie(movie_id: str, movie_data):
    """Update the movie document"""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # movies database
    movies_db = mongo_client["movies"]

    # movie collection
    movie_collection: Collection = movies_db["movie"]

    # update document
    movie_collection.update_one({"id": movie_id}, {"$set": movie_data})

    return True


def kebab_case(text: str) -> str:
    """Convert text to kebab case"""
    return text.lower().replace(" ", "-")
