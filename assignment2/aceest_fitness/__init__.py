"""Application factory, environment configuration and health endpoints."""
import os

from flask import Flask, jsonify, request
from sqlalchemy import text
from sqlalchemy.engine import URL

from .models import db


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates")
    app.config.update(
        SQLALCHEMY_DATABASE_URI=_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        APP_VERSION=os.environ.get("APP_VERSION", "3.2.4-web"),
        SHADOW_MODE=os.environ.get("SHADOW_MODE", "false").lower() == "true",
        APP_VARIANT=os.environ.get("APP_VARIANT", "stable"),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    with app.app_context():
        if db.engine.dialect.name == "postgresql":
            # Prevent simultaneous replicas/workers from racing during demo schema creation.
            with db.engine.connect() as connection:
                connection.execute(text("SELECT pg_advisory_lock(437802)"))
                try:
                    db.create_all()
                finally:
                    connection.execute(text("SELECT pg_advisory_unlock(437802)"))
        else:
            db.create_all()

    from .routes import api
    app.register_blueprint(api)

    @app.before_request
    def protect_shadow_from_writes():
        if app.config["SHADOW_MODE"] and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            # NGINX mirror requests must not mutate the shared database.
            return ("", 204)

    @app.after_request
    def add_version_header(response):
        response.headers["X-ACEest-Version"] = app.config["APP_VERSION"]
        response.headers["X-ACEest-Variant"] = app.config["APP_VARIANT"]
        return response

    @app.get("/health/live")
    def live():
        return jsonify(status="alive", version=app.config["APP_VERSION"])

    @app.get("/health/ready")
    def ready():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ready")
        except Exception:
            return jsonify(status="unavailable"), 503

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error="Method not allowed"), 405

    return app


def _database_url():
    """Use local SQLite by default, but PostgreSQL in Kubernetes."""
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    host = os.environ.get("DB_HOST")
    if host:
        return URL.create(
            "postgresql+psycopg2",
            username=os.environ.get("DB_USER", "aceest"),
            password=os.environ.get("DB_PASSWORD", ""),
            host=host,
            port=int(os.environ.get("DB_PORT", "5432")),
            database=os.environ.get("DB_NAME", "aceest"),
        )
    return "sqlite:///aceest_fitness.db"
