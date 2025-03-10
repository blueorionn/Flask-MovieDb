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
