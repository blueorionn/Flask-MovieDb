"""Application Configuration."""

import os


class Config:
    """Base Configuration."""

    SECRET_KEY = os.environ["SECRET_KEY"]
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    # File size restriction
    MAX_CONTENT_LENGTH = 24 * 1024 * 1024  # 24 megabytes
    # Database variable
    MONGO_URI = os.environ.get("MONGO_URI")


class DevelopmentConfig(Config):
    """Development Configuration."""

    ENV = "dev"
    DEBUG = True


class ProductionConfig(Config):
    """Production Configuration."""

    ENV = "prod"
    DEBUG = False


class TestingConfig(Config):
    """Testing Configuration."""

    TESTING = True
    DEBUG = True


if os.environ.get("FLASK_ENV") == "production":
    config = ProductionConfig()
elif os.environ.get("FLASK_ENV") == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()
