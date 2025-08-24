"""Main application package."""

from flask import Flask, render_template

from moviedb.settings import config
from moviedb.extensions import init_cors
from moviedb import core, auth
from .views import blueprint as base_blueprint
from .middleware import authentication_middleware


def create_app(config_object=config):
    """Create an application factory

    :param config_object: The configuration object to use
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Running middleware
    app.before_request(authentication_middleware)

    # log config_object type
    app.logger.info(f"Using {config_object.__class__.__name__}")
    app.logger.info(f"Debug mode is {config_object.DEBUG}")

    register_extension(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_extension(app: Flask):
    """Registering extensions."""

    init_cors(app)


def register_blueprints(app: Flask):
    """Registering blueprints."""

    app.register_blueprint(base_blueprint)
    app.register_blueprint(core.views.blueprint)
    app.register_blueprint(auth.views.blueprint)


def register_error_handlers(app: Flask):
    """Registering error handlers."""

    @app.errorhandler(404)
    def not_found(e):
        context = {"error_code": "404", "error_message": "Page Not Found"}
        return render_template("handlers/handler.html", context=context), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        context = {"error_code": "405", "error_message": "Method Not Allowed"}
        return render_template("handlers/handler.html", context=context), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        context = {"error_code": "500", "error_message": "Internal Server Error"}
        return render_template("handlers/handler.html", context=context), 500
