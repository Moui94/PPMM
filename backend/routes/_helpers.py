"""
backend/routes/_helpers.py
Gemeinsame Hilfsfunktionen und Decorators für alle Blueprint-Routen.
"""

from functools import wraps
from flask import jsonify, session, request


def success(data=None, status: int = 200, **kwargs):
    """Standardisierte Erfolgsantwort."""
    body = {"ok": True}
    if data is not None:
        body["data"] = data
    body.update(kwargs)
    return jsonify(body), status


def error(message: str, status: int = 400, **kwargs):
    """Standardisierte Fehlerantwort."""
    body = {"ok": False, "error": message}
    body.update(kwargs)
    return jsonify(body), status


def login_required(f):
    """Decorator: Prüft ob ein Benutzer eingeloggt ist."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return error("Nicht authentifiziert. Bitte einloggen.", 401)
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: Prüft ob der eingeloggte Benutzer eine der erlaubten Rollen hat."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("rolle") not in roles:
                return error(
                    f"Keine Berechtigung. Erforderlich: {list(roles)}", 403
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_json_or_400():
    """Parst JSON-Body oder gibt 400 zurück."""
    data = request.get_json(silent=True)
    if data is None:
        return None, error("Ungültiger JSON-Body.", 400)
    return data, None
