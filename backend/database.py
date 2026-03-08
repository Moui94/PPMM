"""
backend/database.py
Datenbankverbindung, Schema-Initialisierung und Hilfsfunktionen.
Kein Flask-Kontext nötig – kann auch standalone verwendet werden.
"""

import sqlite3
import hashlib
import os
from contextlib import contextmanager

DATABASE = os.environ.get("DB_PATH", "produktions.db")


# ──────────────────────────────────────────────────────────────────────────────
# VERBINDUNG
# ──────────────────────────────────────────────────────────────────────────────

def get_connection(db_path: str = DATABASE) -> sqlite3.Connection:
    """Gibt eine neue SQLite-Verbindung zurück (Row-Factory aktiviert)."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # bessere Lese-/Schreibperformance
    return conn


@contextmanager
def db_session(db_path: str = DATABASE):
    """
    Context Manager für eine DB-Session mit automatischem Commit/Rollback.

    Verwendung:
        with db_session() as conn:
            conn.execute("INSERT INTO ...")
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# FLASK-INTEGRATION (g-Objekt)
# ──────────────────────────────────────────────────────────────────────────────

def get_db():
    """
    Gibt die DB-Verbindung für den aktuellen Flask-Request zurück (via flask.g).
    Wird in app.py als before_request / teardown_appcontext registriert.
    """
    from flask import g
    if "db" not in g:
        g.db = get_connection()
    return g.db


def close_db(e=None):
    """Schliesst die DB-Verbindung am Ende des Flask-Requests."""
    from flask import g
    db = g.pop("db", None)
    if db is not None:
        db.close()


def register_db(app):
    """Registriert DB-Handling an der Flask-App."""
    app.teardown_appcontext(close_db)


# ──────────────────────────────────────────────────────────────────────────────
# SCHEMA
# ──────────────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
-- Benutzer
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    rolle         TEXT    NOT NULL DEFAULT 'ma'
                          CHECK(rolle IN ('admin','pl','ma')),
    aktiv         INTEGER NOT NULL DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aufträge
CREATE TABLE IF NOT EXISTS orders (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    pa_nr               TEXT    UNIQUE NOT NULL,
    art                 TEXT    NOT NULL CHECK(art IN ('A','I')),
    artikel             TEXT    NOT NULL,
    ceramaret           TEXT,
    spezielles          TEXT,
    menge               INTEGER NOT NULL DEFAULT 0 CHECK(menge > 0),
    menge_produziert    INTEGER NOT NULL DEFAULT 0,
    prioritaet          INTEGER NOT NULL DEFAULT 2
                                CHECK(prioritaet IN (1,2,3)),
    status              TEXT    NOT NULL DEFAULT 'geplant'
                                CHECK(status IN ('geplant','aktiv','abgeschlossen','archiviert')),
    pa_start            DATE,
    haas_nr             TEXT,
    endtermin_soll      DATE,
    auslieferung_kunde  DATE,
    abweichung_tage     INTEGER NOT NULL DEFAULT 0,
    bestaetigung_kunde  TEXT,
    bemerkung           TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Arbeitsgänge
CREATE TABLE IF NOT EXISTS order_operations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    ag_nr           INTEGER NOT NULL CHECK(ag_nr BETWEEN 1 AND 14),
    bezeichnung     TEXT    NOT NULL,
    solldauer_tage  REAL    NOT NULL DEFAULT 1 CHECK(solldauer_tage > 0),
    start_soll      DATE,
    ende_soll       DATE,
    start_ist       TIMESTAMP,
    ende_ist        TIMESTAMP,
    maschine        TEXT,
    kapazitaet      TEXT,
    status          TEXT    NOT NULL DEFAULT 'offen'
                            CHECK(status IN ('offen','laufend','abgeschlossen')),
    bemerkung       TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
    UNIQUE(order_id, ag_nr)
);

-- Qualitäts-Rückmeldungen
CREATE TABLE IF NOT EXISTS op_feedbacks (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    op_id            INTEGER NOT NULL,
    order_id         INTEGER NOT NULL,
    ag_nr            INTEGER NOT NULL,
    user_id          INTEGER NOT NULL,
    menge_input      INTEGER NOT NULL DEFAULT 0 CHECK(menge_input >= 0),
    menge_gut        INTEGER NOT NULL DEFAULT 0 CHECK(menge_gut >= 0),
    menge_ausschuss  INTEGER NOT NULL DEFAULT 0 CHECK(menge_ausschuss >= 0),
    start_ist        TIMESTAMP,
    ende_ist         TIMESTAMP,
    maschine         TEXT,
    bemerkung        TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(op_id)    REFERENCES order_operations(id),
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(user_id)  REFERENCES users(id)
);

-- Ausschuss-Fehlercodes
CREATE TABLE IF NOT EXISTS defect_entries (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id         INTEGER NOT NULL,
    order_id            INTEGER NOT NULL,
    ag_nr               INTEGER NOT NULL,
    fehler_code         TEXT    NOT NULL,
    fehler_bezeichnung  TEXT    NOT NULL,
    fehler_kategorie    TEXT,
    menge               INTEGER NOT NULL DEFAULT 1 CHECK(menge > 0),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(feedback_id) REFERENCES op_feedbacks(id)
);

-- Fräsplanungen (Header)
CREATE TABLE IF NOT EXISTS schedule_plans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ag_nr       INTEGER NOT NULL CHECK(ag_nr IN (1,2,3)),
    plan_name   TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'vorschlag'
                        CHECK(status IN ('vorschlag','aktiv','archiviert')),
    created_by  INTEGER,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(created_by) REFERENCES users(id)
);

-- Fräsplanungs-Slots (Maschinenbelegung)
CREATE TABLE IF NOT EXISTS schedule_slots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id       INTEGER NOT NULL,
    order_id      INTEGER NOT NULL,
    pa_nr         TEXT    NOT NULL,
    artikel       TEXT    NOT NULL,
    art           TEXT    NOT NULL CHECK(art IN ('A','I')),
    menge         INTEGER,
    maschine      TEXT    NOT NULL,
    reihenfolge   INTEGER NOT NULL,
    prioritaet    INTEGER DEFAULT 2,
    planzeit_tage REAL,
    start_plan    DATE,
    ende_plan     DATE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(plan_id)   REFERENCES schedule_plans(id) ON DELETE CASCADE,
    FOREIGN KEY(order_id)  REFERENCES orders(id)
);
"""

SEED_SQL = """
INSERT OR IGNORE INTO users (username, password_hash, rolle)
VALUES ('admin', '{pw_hash}', 'admin');
"""


def init_db(db_path: str = DATABASE) -> None:
    """
    Initialisiert die Datenbank: Schema anlegen + Admin-User seeden.
    Sicher wiederholbar (CREATE TABLE IF NOT EXISTS / INSERT OR IGNORE).
    """
    with db_session(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, rolle) VALUES (?,?,?)",
            ("admin", pw_hash, "admin")
        )
    print(f"[db] Datenbank initialisiert: {db_path}")


def reset_db(db_path: str = DATABASE) -> None:
    """Löscht und re-initialisiert die Datenbank. NUR für Tests/Entwicklung!"""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[db] Alte Datenbank gelöscht: {db_path}")
    init_db(db_path)


# ──────────────────────────────────────────────────────────────────────────────
# MIGRATIONS-HILFSFUNKTION
# ──────────────────────────────────────────────────────────────────────────────

def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Prüft ob eine Spalte in einer Tabelle existiert."""
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(c["name"] == column for c in cols)


def add_column_if_missing(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> bool:
    """
    Fügt eine Spalte hinzu, falls sie noch nicht existiert.
    Gibt True zurück wenn die Spalte hinzugefügt wurde, sonst False.
    """
    if not column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"[db] Migration: {table}.{column} ({definition}) hinzugefügt.")
        return True
    return False
