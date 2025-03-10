"""Flask extensions for additional functionalities."""

from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo


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

# Mongodb extension
mongo = PyMongo()
