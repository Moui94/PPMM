"""
backend/routes/users.py
Benutzerverwaltungs-API (nur admin).

GET    /api/users            → Alle Benutzer
POST   /api/users            → Neuen Benutzer anlegen
PUT    /api/users/<id>       → Benutzer bearbeiten
PUT    /api/users/<id>/pw    → Passwort ändern
PUT    /api/users/<id>/toggle → Aktivieren / Deaktivieren
"""

from flask import Blueprint, request, session
from backend.database import get_db
from backend.models.user import (
    list_users, get_user_by_id, create_user,
    update_user, change_password,
)
from ._helpers import success, error, login_required, role_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _user_dict(u) -> dict:
    return {
        "id":         u["id"],
        "username":   u["username"],
        "rolle":      u["rolle"],
        "aktiv":      bool(u["aktiv"]),
        "created_at": str(u["created_at"] or ""),
    }


@users_bp.route("", methods=["GET"])
@login_required
@role_required("admin")
def get_users():
    return success([_user_dict(u) for u in list_users(get_db())])


@users_bp.route("", methods=["POST"])
@login_required
@role_required("admin")
def post_user():
    conn = get_db()
    data = request.get_json(silent=True) or {}
    try:
        user_id = create_user(
            conn,
            username = str(data.get("username", "")),
            password = str(data.get("password", "")),
            rolle    = str(data.get("rolle", "ma")),
        )
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success(_user_dict(get_user_by_id(conn, user_id)), status=201)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
@role_required("admin")
def put_user(user_id):
    conn = get_db()
    user = get_user_by_id(conn, user_id)
    if not user:
        return error(f"Benutzer {user_id} nicht gefunden.", 404)
    data = request.get_json(silent=True) or {}
    fields = {}
    if "rolle" in data: fields["rolle"] = data["rolle"]
    if "aktiv" in data: fields["aktiv"] = 1 if data["aktiv"] else 0
    try:
        update_user(conn, user_id, **fields)
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success(_user_dict(get_user_by_id(conn, user_id)))


@users_bp.route("/<int:user_id>/pw", methods=["PUT"])
@login_required
def put_password(user_id):
    # Nur admin oder eigenes Passwort
    if session.get("rolle") != "admin" and session.get("user_id") != user_id:
        return error("Keine Berechtigung.", 403)
    data = request.get_json(silent=True) or {}
    conn = get_db()
    try:
        change_password(conn, user_id, str(data.get("password", "")))
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success(message="Passwort geändert.")


@users_bp.route("/<int:user_id>/toggle", methods=["PUT"])
@login_required
@role_required("admin")
def toggle_user(user_id):
    conn = get_db()
    user = get_user_by_id(conn, user_id)
    if not user:
        return error(f"Benutzer {user_id} nicht gefunden.", 404)
    if user["username"] == "admin":
        return error("Admin-Benutzer kann nicht deaktiviert werden.", 400)
    new_aktiv = 0 if user["aktiv"] else 1
    update_user(conn, user_id, aktiv=new_aktiv)
    conn.commit()
    return success(_user_dict(get_user_by_id(conn, user_id)))
