"""
backend/models/operation.py
CRUD für Arbeitsgänge. Unterstützt Ceramaret (AG1 entfällt).
"""

import sqlite3
from datetime import date
from typing import Optional

from backend.constants import AG_STATUS, ARBEITSGAENGE
from backend.services.date_calc import add_workdays, parse_date_safe


def get_operations(conn: sqlite3.Connection, order_id: int) -> list[sqlite3.Row]:
    return conn.execute("""
        SELECT * FROM order_operations
        WHERE order_id = ?
        ORDER BY ag_nr ASC
    """, (order_id,)).fetchall()


def get_operation_by_id(conn: sqlite3.Connection, op_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("""
        SELECT oo.*, o.pa_nr, o.art, o.menge AS auftrag_menge, o.ceramaret
        FROM order_operations oo
        JOIN orders o ON o.id = oo.order_id
        WHERE oo.id = ?
    """, (op_id,)).fetchone()


def get_operation_progress(conn: sqlite3.Connection, order_id: int) -> dict:
    row = conn.execute("""
        SELECT
            COUNT(*)                                                   AS total,
            SUM(CASE WHEN status = 'abgeschlossen' THEN 1 ELSE 0 END) AS done,
            SUM(CASE WHEN status = 'laufend'       THEN 1 ELSE 0 END) AS laufend,
            SUM(CASE WHEN status = 'offen'         THEN 1 ELSE 0 END) AS offen
        FROM order_operations WHERE order_id = ?
    """, (order_id,)).fetchone()
    total = row["total"] or 1
    done  = row["done"]  or 0
    return {
        "total":   total,
        "done":    done,
        "laufend": row["laufend"] or 0,
        "offen":   row["offen"]   or 0,
        "percent": int(done / total * 100),
    }


def get_last_menge_gut(conn: sqlite3.Connection, order_id: int, ag_nr: int) -> Optional[int]:
    """
    Gibt die Gut-Menge des vorherigen AGs zurück (für Rückmeldungs-Vorschlag).
    Sucht den letzten abgeschlossenen AG vor ag_nr.
    """
    row = conn.execute("""
        SELECT f.menge_gut
        FROM op_feedbacks f
        JOIN order_operations op ON op.id = f.op_id
        WHERE f.order_id = ?
          AND op.ag_nr < ?
        ORDER BY op.ag_nr DESC, f.created_at DESC
        LIMIT 1
    """, (order_id, ag_nr)).fetchone()
    return row["menge_gut"] if row else None


def create_operations_for_order(
    conn: sqlite3.Connection,
    order_id: int,
    art: str,
    pa_start: date,
    ceramaret: bool = False,
    solldauern_override: Optional[dict] = None,
) -> date:
    """
    Legt alle Arbeitsgänge an. Bei ceramaret=True entfällt AG1.
    Gibt den Endtermin zurück.
    """
    from backend.services.date_calc import calc_ag_termine
    termine, endtermin = calc_ag_termine(art, pa_start, solldauern_override, ceramaret)
    for t in termine:
        conn.execute("""
            INSERT INTO order_operations
              (order_id, ag_nr, bezeichnung, solldauer_tage, start_soll, ende_soll, status)
            VALUES (?,?,?,?,?,?,'offen')
        """, (
            order_id, t.ag_nr, t.bezeichnung,
            t.solldauer_tage,
            t.start_soll.isoformat(),
            t.ende_soll.isoformat(),
        ))
    return endtermin


def update_operation(conn: sqlite3.Connection, op_id: int, **fields) -> None:
    ALLOWED = {
        "solldauer_tage","start_soll","ende_soll",
        "maschine","kapazitaet","status","bemerkung",
        "start_ist","ende_ist",
    }
    invalid = set(fields.keys()) - ALLOWED
    if invalid:
        raise ValueError(f"Unbekannte Felder: {invalid}")
    if "status" in fields and fields["status"] not in AG_STATUS:
        raise ValueError(f"Ungültiger AG-Status: '{fields['status']}'")
    if "solldauer_tage" in fields and fields["solldauer_tage"] <= 0:
        raise ValueError("solldauer_tage muss > 0 sein.")

    if "start_soll" in fields and "ende_soll" not in fields:
        start = parse_date_safe(str(fields["start_soll"]))
        op    = conn.execute(
            "SELECT solldauer_tage FROM order_operations WHERE id = ?", (op_id,)
        ).fetchone()
        if start and op:
            dauer = fields.get("solldauer_tage", op["solldauer_tage"])
            fields["ende_soll"] = add_workdays(start, dauer).isoformat()
    elif "solldauer_tage" in fields and "start_soll" not in fields and "ende_soll" not in fields:
        op = conn.execute(
            "SELECT start_soll FROM order_operations WHERE id = ?", (op_id,)
        ).fetchone()
        if op and op["start_soll"]:
            start = parse_date_safe(str(op["start_soll"]))
            if start:
                fields["ende_soll"] = add_workdays(start, fields["solldauer_tage"]).isoformat()

    set_parts = ", ".join(f"{k} = ?" for k in fields)
    set_parts += ", updated_at = CURRENT_TIMESTAMP"
    conn.execute(f"UPDATE order_operations SET {set_parts} WHERE id = ?",
                 list(fields.values()) + [op_id])


def set_operation_status(
    conn, op_id, status,
    start_ist=None, ende_ist=None, maschine=None,
) -> None:
    if status not in AG_STATUS:
        raise ValueError(f"Ungültiger Status: '{status}'")
    conn.execute("""
        UPDATE order_operations
        SET status    = ?,
            start_ist = COALESCE(start_ist, ?),
            ende_ist  = ?,
            maschine  = COALESCE(maschine, ?),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, start_ist, ende_ist, maschine, op_id))
