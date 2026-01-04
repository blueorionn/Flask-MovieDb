"""Flask extensions for additional functionalities."""

import pymongo
from flask import Flask, g, current_app
from flask_cors import CORS


# Flask Cors Configuration
def init_cors(app: Flask):
    CORS(
        app,
        resources={
            r"/*": {
                "origins": "*",  # Allows all origins
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            }
        },
    )


# Flask db configuration
def get_client():
    if "mongo_client" not in g:
        mongo_uri = current_app.config["MONGO_URI"]
        g.mongo_client = pymongo.MongoClient(mongo_uri)
    return g.mongo_client


def get_db():
    return get_client()[current_app.config["DATABASE_NAME"]]


def close_db(e=None):
    client = g.pop("mongo_client", None)
    if client is not None:
        client.close()
