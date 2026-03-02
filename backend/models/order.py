"""
backend/models/order.py — Auftrags-CRUD mit Ceramaret-Unterstützung.
"""

import sqlite3
from datetime import date
from typing import Optional

from backend.constants import AUFTRAG_STATUS, PRIORITAETEN, AUFTRAG_TYPEN
from backend.services.date_calc import (
    recalc_endtermin, calc_abweichung, parse_date_safe, fmt_date_ch,
)


def get_order_by_pa_nr(conn, pa_nr):
    return conn.execute("SELECT * FROM orders WHERE pa_nr = ?", (pa_nr,)).fetchone()

def get_order_by_id(conn, order_id):
    return conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

def order_exists(conn, pa_nr):
    return conn.execute("SELECT 1 FROM orders WHERE pa_nr = ?", (pa_nr,)).fetchone() is not None

def list_orders(conn, status=None, art=None, prioritaet=None, search=None):
    sql, params = "SELECT * FROM orders WHERE 1=1", []
    if status:     sql += " AND status = ?";                 params.append(status)
    if art:        sql += " AND art = ?";                    params.append(art)
    if prioritaet: sql += " AND prioritaet = ?";             params.append(prioritaet)
    if search:
        sql += " AND (pa_nr LIKE ? OR artikel LIKE ?)";      params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY prioritaet ASC, endtermin_soll ASC"
    return conn.execute(sql, params).fetchall()


def create_order(
    conn,
    pa_nr: str,
    art: str,
    artikel: str,
    menge: int,
    prioritaet: int = 2,
    pa_start=None,
    auslieferung_kunde=None,
    ceramaret: bool = False,
    spezielles=None,
    haas_nr=None,
    bemerkung=None,
) -> int:
    pa_nr   = pa_nr.strip()
    artikel = artikel.strip()
    if not pa_nr:                          raise ValueError("PA-Nr darf nicht leer sein.")
    if art not in AUFTRAG_TYPEN:           raise ValueError(f"Ungültiger Typ '{art}'.")
    if not artikel:                        raise ValueError("Artikel darf nicht leer sein.")
    if menge <= 0:                         raise ValueError("Menge muss > 0 sein.")
    if prioritaet not in PRIORITAETEN:     raise ValueError(f"Ungültige Priorität '{prioritaet}'.")
    if order_exists(conn, pa_nr):          raise ValueError(f"PA-Nr '{pa_nr}' existiert bereits.")

    pa_start_d = pa_start or date.today()
    ceramaret_int = 1 if ceramaret else 0

    cur = conn.execute("""
        INSERT INTO orders
          (pa_nr, art, artikel, ceramaret, spezielles, menge, prioritaet,
           status, pa_start, auslieferung_kunde, haas_nr, bemerkung)
        VALUES (?,?,?,?,?,?,?,'geplant',?,?,?,?)
    """, (
        pa_nr, art, artikel, ceramaret_int, spezielles or None,
        menge, prioritaet,
        pa_start_d.isoformat() if hasattr(pa_start_d, 'isoformat') else pa_start_d,
        auslieferung_kunde.isoformat() if auslieferung_kunde and hasattr(auslieferung_kunde, 'isoformat') else auslieferung_kunde,
        haas_nr or None,
        bemerkung or None,
    ))
    return cur.lastrowid


def update_order(conn, order_id: int, **fields) -> None:
    ALLOWED = {
        "artikel","ceramaret","spezielles","menge","prioritaet",
        "status","auslieferung_kunde","haas_nr","bemerkung",
        "bestaetigung_kunde","endtermin_soll","abweichung_tage","menge_produziert",
    }
    invalid = set(fields.keys()) - ALLOWED
    if invalid: raise ValueError(f"Unbekannte Felder: {invalid}")
    if "status"    in fields and fields["status"]    not in AUFTRAG_STATUS:
        raise ValueError(f"Ungültiger Status: '{fields['status']}'")
    if "prioritaet" in fields and fields["prioritaet"] not in PRIORITAETEN:
        raise ValueError(f"Ungültige Priorität: {fields['prioritaet']}")
    if "menge" in fields and fields["menge"] <= 0:
        raise ValueError("Menge muss > 0 sein.")
    set_parts = ", ".join(f"{k} = ?" for k in fields)
    set_parts += ", updated_at = CURRENT_TIMESTAMP"
    conn.execute(f"UPDATE orders SET {set_parts} WHERE id = ?",
                 list(fields.values()) + [order_id])


def update_order_endtermin(conn, order_id, auslieferung_kunde=None):
    ops = conn.execute("""
        SELECT ende_soll FROM order_operations
        WHERE order_id = ? AND ende_soll IS NOT NULL
        ORDER BY ag_nr
    """, (order_id,)).fetchall()
    if not auslieferung_kunde:
        row = conn.execute(
            "SELECT auslieferung_kunde FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        if row and row["auslieferung_kunde"]:
            auslieferung_kunde = parse_date_safe(row["auslieferung_kunde"])
    endtermin, abweichung = recalc_endtermin(
        [dict(op) for op in ops], auslieferung_kunde
    )
    conn.execute("""
        UPDATE orders
        SET endtermin_soll = ?, abweichung_tage = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (endtermin.isoformat(), abweichung, order_id))
    return endtermin, abweichung


def get_kpis(conn) -> dict:
    def count(where, params=()):
        return conn.execute(f"SELECT COUNT(*) FROM orders WHERE {where}", params).fetchone()[0]
    return {
        "aktiv":         count("status = 'aktiv'"),
        "geplant":       count("status = 'geplant'"),
        "archiviert":    count("status = 'archiviert'"),
        "abgeschlossen": count("status = 'abgeschlossen'"),
        "verzug":        count("status = 'aktiv' AND abweichung_tage > 0"),
        "prio_hoch":     count("prioritaet = 1 AND status IN ('geplant','aktiv')"),
    }
