"""Flask extensions for additional functionalities."""

import pymongo
from flask import Flask, g, current_app
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo.uri_parser import parse_uri


# Flask Cors Configuration
def init_cors(app: Flask):
    origins = app.config.get("CORS_ORIGINS")
    CORS(
        app,
        resources={
            r"/*": {
                "origins": origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            }
        },
    )


# Rate Limiter Extention
limiter = Limiter(key_func=get_remote_address)


def init_limiter(app: Flask):
    limiter.init_app(app)


# Flask db configuration
def get_client():
    if "mongo_client" not in g:
        mongo_uri = current_app.config["MONGO_URI"]
        g.mongo_client = pymongo.MongoClient(mongo_uri)
    return g.mongo_client


def get_db():
    uri = current_app.config["MONGO_URI"]
    client = get_client()
    db_name = _extract_db_name(uri)
    if not db_name:
        raise RuntimeError(
            "MONGO_URI must include a database name in the path, "
            "e.g. mongodb://localhost:27017/mydb"
        )
    return client[db_name]


def _extract_db_name(uri: str) -> str | None:
    """Extract the database name from a MongoDB URI."""
    parsed = parse_uri(uri)
    return parsed.get("database")


def close_db(e=None):
    client = g.pop("mongo_client", None)
    if client is not None:
        client.close()
