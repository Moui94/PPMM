"""
backend/models/user.py
CRUD-Operationen für Benutzer.
"""

import sqlite3
import hashlib
from typing import Optional
from backend.constants import USER_ROLLEN


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> Optional[sqlite3.Row]:
    """Prüft Benutzername + Passwort. Gibt User-Row zurück oder None."""
    user = get_user_by_username(conn, username)
    if user and user["aktiv"] and user["password_hash"] == hash_password(password):
        return user
    return None


def list_users(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM users ORDER BY rolle, username"
    ).fetchall()


def create_user(
    conn: sqlite3.Connection,
    username: str,
    password: str,
    rolle: str = "ma",
) -> int:
    username = username.strip()
    if not username:
        raise ValueError("Benutzername darf nicht leer sein.")
    if len(password) < 6:
        raise ValueError("Passwort muss mind. 6 Zeichen haben.")
    if rolle not in USER_ROLLEN:
        raise ValueError(f"Ungültige Rolle '{rolle}'. Erlaubt: {USER_ROLLEN}")
    if get_user_by_username(conn, username):
        raise ValueError(f"Benutzername '{username}' existiert bereits.")
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, rolle) VALUES (?,?,?)",
        (username, hash_password(password), rolle)
    )
    return cur.lastrowid


def update_user(
    conn: sqlite3.Connection,
    user_id: int,
    **fields,
) -> None:
    ALLOWED = {"rolle", "aktiv", "password_hash"}
    invalid = set(fields.keys()) - ALLOWED
    if invalid:
        raise ValueError(f"Unbekannte Felder: {invalid}")
    if "rolle" in fields and fields["rolle"] not in USER_ROLLEN:
        raise ValueError(f"Ungültige Rolle: '{fields['rolle']}'")
    set_parts = ", ".join(f"{k} = ?" for k in fields)
    set_parts += ", updated_at = CURRENT_TIMESTAMP"
    conn.execute(
        f"UPDATE users SET {set_parts} WHERE id = ?",
        list(fields.values()) + [user_id]
    )


def change_password(conn: sqlite3.Connection, user_id: int, new_password: str) -> None:
    if len(new_password) < 6:
        raise ValueError("Passwort muss mind. 6 Zeichen haben.")
    update_user(conn, user_id, password_hash=hash_password(new_password))
