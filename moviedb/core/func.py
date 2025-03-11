"""Functions for view"""

import os
import pymongo
from pymongo.collection import Collection


def list_movies():
    """List all movies"""

    # creating pymongo client
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # movies database
    movies_db = mongo_client["movies"]

    # movie collection
    movie_collection: Collection = movies_db["movie"]

    # getting movies
    movies = list(movie_collection.find({}))

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
