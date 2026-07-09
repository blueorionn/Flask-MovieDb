"""Main application package."""

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from moviedb.settings import config
from moviedb.extensions import init_cors, init_limiter, close_db, init_jwt
from moviedb import core, auth
from .views import blueprint as base_blueprint


def create_app(config_object=config):
    """Create an application factory

    :param config_object: The configuration object to use
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Database
    app.teardown_appcontext(close_db)

    # log config_object type
    app.logger.info(f"Using {config_object.__class__.__name__}")
    app.logger.info(f"Debug mode is {config_object.DEBUG}")

    register_extension(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_context_processors(app)

    return app


def register_extension(app: Flask):
    """Registering extensions."""

    init_cors(app)
    CSRFProtect(app)
    init_limiter(app)
    init_jwt(app)


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

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Renders a custom 400.html for failed token validation
        context = {"error_code": "400", "error_message": "Invalid CSRF Token"}
        return render_template("handlers/handler.html", context=context), 400

    @app.errorhandler(429)
    def too_many_requests(e):
        context = {"error_code": "429", "error_message": "Too Many Requests"}
        return render_template("handlers/handler.html", context=context), 429


def register_context_processors(app: Flask):
    @app.context_processor
    def inject_user():
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return {"current_user": identity}
