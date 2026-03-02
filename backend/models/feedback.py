"""
backend/models/feedback.py
CRUD für Qualitäts-Rückmeldungen (op_feedbacks) und Fehlercodes (defect_entries).
"""

import sqlite3
from typing import Optional
from backend.constants import FEHLERKATALOG


# ──────────────────────────────────────────────────────────────────────────────
# RÜCKMELDUNGEN LESEN
# ──────────────────────────────────────────────────────────────────────────────

def get_feedbacks_for_op(conn: sqlite3.Connection, op_id: int) -> list[sqlite3.Row]:
    """Gibt alle Rückmeldungen zu einem AG zurück, neueste zuerst."""
    return conn.execute("""
        SELECT f.*, u.username
        FROM op_feedbacks f
        JOIN users u ON u.id = f.user_id
        WHERE f.op_id = ?
        ORDER BY f.created_at DESC
    """, (op_id,)).fetchall()


def get_latest_feedback(conn: sqlite3.Connection, op_id: int) -> Optional[sqlite3.Row]:
    """Gibt die neueste Rückmeldung zu einem AG zurück oder None."""
    return conn.execute("""
        SELECT f.*, u.username
        FROM op_feedbacks f
        JOIN users u ON u.id = f.user_id
        WHERE f.op_id = ?
        ORDER BY f.created_at DESC
        LIMIT 1
    """, (op_id,)).fetchone()


def get_defects_for_feedback(conn: sqlite3.Connection, feedback_id: int) -> list[sqlite3.Row]:
    return conn.execute("""
        SELECT * FROM defect_entries WHERE feedback_id = ?
        ORDER BY menge DESC
    """, (feedback_id,)).fetchall()


# ──────────────────────────────────────────────────────────────────────────────
# RÜCKMELDUNG SPEICHERN
# ──────────────────────────────────────────────────────────────────────────────

def create_feedback(
    conn: sqlite3.Connection,
    op_id: int,
    order_id: int,
    ag_nr: int,
    user_id: int,
    menge_input: int,
    menge_ausschuss: int,
    start_ist: Optional[str] = None,
    ende_ist: Optional[str] = None,
    maschine: Optional[str] = None,
    bemerkung: Optional[str] = None,
    fehler: Optional[list[dict]] = None,
) -> int:
    """
    Speichert eine Rückmeldung inkl. optionaler Fehlercodes.

    Args:
        fehler: Liste von Dicts mit 'code' und optional 'menge'
                z.B. [{'code': 'M01', 'menge': 2}, {'code': 'O03', 'menge': 1}]

    Returns:
        feedback_id (neu angelegte ID)

    Raises:
        ValueError: bei ungültigen Mengenwerten
    """
    if menge_input <= 0:
        raise ValueError("menge_input muss > 0 sein.")
    if menge_ausschuss < 0:
        raise ValueError("menge_ausschuss darf nicht negativ sein.")
    if menge_ausschuss > menge_input:
        raise ValueError("menge_ausschuss darf nicht grösser als menge_input sein.")

    menge_gut = menge_input - menge_ausschuss

    cur = conn.execute("""
        INSERT INTO op_feedbacks
          (op_id, order_id, ag_nr, user_id,
           menge_input, menge_gut, menge_ausschuss,
           start_ist, ende_ist, maschine, bemerkung)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        op_id, order_id, ag_nr, user_id,
        menge_input, menge_gut, menge_ausschuss,
        start_ist, ende_ist, maschine, bemerkung,
    ))
    feedback_id = cur.lastrowid

    # Fehlercodes speichern
    for f in (fehler or []):
        code  = f.get("code","").strip()
        menge = int(f.get("menge", 1))
        if not code or menge <= 0:
            continue
        fehler_info = FEHLERKATALOG.get(code, {})
        conn.execute("""
            INSERT INTO defect_entries
              (feedback_id, order_id, ag_nr,
               fehler_code, fehler_bezeichnung, fehler_kategorie, menge)
            VALUES (?,?,?,?,?,?,?)
        """, (
            feedback_id, order_id, ag_nr,
            code,
            fehler_info.get("bezeichnung", code),
            fehler_info.get("kategorie", "S"),
            menge,
        ))

    return feedback_id


# ──────────────────────────────────────────────────────────────────────────────
# QUALITÄTS-AUSWERTUNGEN
# ──────────────────────────────────────────────────────────────────────────────

def get_ausschuss_quote(conn: sqlite3.Connection, order_id: int) -> dict:
    """
    Berechnet die Ausschussquote eines Auftrags.
    Returns: {menge_input, menge_gut, menge_ausschuss, quote_pct}
    """
    row = conn.execute("""
        SELECT
            COALESCE(SUM(menge_input), 0)     AS total_input,
            COALESCE(SUM(menge_gut), 0)       AS total_gut,
            COALESCE(SUM(menge_ausschuss), 0) AS total_ausschuss
        FROM op_feedbacks
        WHERE order_id = ?
    """, (order_id,)).fetchone()

    total_input = row["total_input"] or 1
    return {
        "menge_input":     row["total_input"],
        "menge_gut":       row["total_gut"],
        "menge_ausschuss": row["total_ausschuss"],
        "quote_pct":       round(row["total_ausschuss"] / total_input * 100, 2),
    }


def get_pareto_fehler(
    conn: sqlite3.Connection,
    ag_nr: Optional[int] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Top-N Fehlercodes (Pareto) optional gefiltert nach AG.
    Returns: [{fehler_code, bezeichnung, kategorie, total_menge, anteil_pct}]
    """
    sql    = """
        SELECT fehler_code, fehler_bezeichnung, fehler_kategorie,
               SUM(menge) AS total_menge
        FROM defect_entries
        WHERE 1=1
    """
    params = []
    if ag_nr:
        sql += " AND ag_nr = ?"; params.append(ag_nr)
    sql += " GROUP BY fehler_code ORDER BY total_menge DESC LIMIT ?"
    params.append(limit)

    rows  = conn.execute(sql, params).fetchall()
    total = sum(r["total_menge"] for r in rows) or 1
    return [
        {
            "fehler_code":  r["fehler_code"],
            "bezeichnung":  r["fehler_bezeichnung"],
            "kategorie":    r["fehler_kategorie"],
            "total_menge":  r["total_menge"],
            "anteil_pct":   round(r["total_menge"] / total * 100, 1),
        }
        for r in rows
    ]
