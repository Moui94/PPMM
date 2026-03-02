"""
backend/routes/auth.py
Authentifizierungs-Endpunkte.

POST /api/auth/login    → Session erstellen
POST /api/auth/logout   → Session löschen
GET  /api/auth/me       → Aktuellen Benutzer abfragen
"""

from flask import Blueprint, session, request
from backend.database import get_db
from backend.models.user import authenticate
from ._helpers import success, error, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Body: {"username": "...", "password": "..."}
    Response: {"ok": true, "data": {"username": ..., "rolle": ...}}
    """
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return error("Benutzername und Passwort sind Pflichtfelder.", 400)

    user = authenticate(get_db(), username, password)
    if not user:
        return error("Ungültiger Benutzername oder Passwort.", 401)

    session.clear()
    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    session["rolle"]    = user["rolle"]
    session.permanent   = True

    return success({
        "user_id":  user["id"],
        "username": user["username"],
        "rolle":    user["rolle"],
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return success(message="Erfolgreich abgemeldet.")


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return success({
        "user_id":  session["user_id"],
        "username": session["username"],
        "rolle":    session["rolle"],
    })
