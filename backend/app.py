"""
backend/app.py – Flask App Factory.
"""

import os
from flask import Flask, send_from_directory
from backend.database import register_db, init_db


def create_app(test_config=None):
    BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path="",
    )

    # ── Konfiguration ────────────────────────────────────────────────────────
    app.config.from_mapping(
        SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        DATABASE   = os.path.join(BASE_DIR, "produktions.db"),
        SESSION_COOKIE_HTTPONLY = True,
        SESSION_COOKIE_SAMESITE = "Lax",
    )
    if test_config:
        app.config.from_mapping(test_config)

    # ── Datenbank ────────────────────────────────────────────────────────────
    register_db(app)
    with app.app_context():
        init_db(app.config["DATABASE"])

    # ── Blueprints ───────────────────────────────────────────────────────────
    from backend.routes.auth       import auth_bp
    from backend.routes.orders     import orders_bp
    from backend.routes.operations import operations_bp
    from backend.routes.quality    import quality_bp
    from backend.routes.users      import users_bp
    from backend.routes.export     import export_bp

    for bp in [auth_bp, orders_bp, operations_bp, quality_bp, users_bp, export_bp]:
        app.register_blueprint(bp)

    # ── SPA Catch-All: alle nicht-API Routen liefern index.html ─────────────
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        # API-Routen nicht abfangen
        if path.startswith("api/"):
            from flask import abort
            abort(404)
        # Statische Dateien direkt ausliefern (css/, js/, etc.)
        static_file = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(static_file):
            return send_from_directory(FRONTEND_DIR, path)
        # Alles andere → index.html (SPA)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app
