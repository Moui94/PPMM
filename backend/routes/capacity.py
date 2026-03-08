"""
backend/routes/capacity.py
Kapazitätsplanung Haas-Maschinen.
"""
from flask import Blueprint, request
from backend.database import get_db
from backend.routes._helpers import success, error, login_required, role_required
from backend.services.capacity_planner import plan_haas_kapazitaet
from backend.services.date_calc import parse_date_safe, fmt_date_ch
from datetime import date

capacity_bp = Blueprint("capacity", __name__, url_prefix="/api/capacity")


def _load_offene_jobs(conn) -> list:
    """Lädt alle offenen Fräs-AGs aktiver/geplanter Aufträge."""
    rows = conn.execute("""
        SELECT
            op.id         AS op_id,
            op.ag_nr,
            op.solldauer_tage,
            op.start_soll,
            op.ende_soll,
            op.maschine,
            op.status     AS op_status,
            o.pa_nr,
            o.artikel,
            o.art,
            o.menge,
            o.prioritaet,
            o.status      AS order_status
        FROM order_operations op
        JOIN orders o ON o.id = op.order_id
        WHERE op.ag_nr IN (1,2,3)
          AND op.status IN ('offen','laufend')
          AND o.status IN ('aktiv','geplant')
        ORDER BY o.prioritaet, op.ag_nr, o.pa_nr
    """).fetchall()

    jobs = []
    for r in rows:
        # Vorgänger-AG Ende ermitteln (AG1→AG2→AG3)
        vorgaenger_ende = None
        if r["ag_nr"] > 1:
            vorg = conn.execute("""
                SELECT COALESCE(ende_ist, ende_soll) AS ende
                FROM order_operations
                WHERE order_id = (
                    SELECT order_id FROM order_operations WHERE id = ?
                ) AND ag_nr = ?
            """, (r["op_id"], r["ag_nr"] - 1)).fetchone()
            if vorg and vorg["ende"]:
                vorgaenger_ende = str(vorg["ende"])[:10]

        jobs.append({
            "op_id":           r["op_id"],
            "pa_nr":           r["pa_nr"],
            "ag_nr":           r["ag_nr"],
            "artikel":         r["artikel"],
            "art":             r["art"],
            "menge":           r["menge"],
            "solldauer_tage":  r["solldauer_tage"],
            "prioritaet":      r["prioritaet"],
            "start_soll":      str(r["start_soll"] or "")[:10],
            "ende_soll":       str(r["ende_soll"] or "")[:10],
            "maschine":        r["maschine"],
            "vorgaenger_ende": vorgaenger_ende,
            "order_status":    r["order_status"],
        })
    return jobs


@capacity_bp.route("/plan", methods=["GET"])
@login_required
def get_plan():
    """Gibt den Planungsvorschlag zurück."""
    conn  = get_db()
    today = date.today()
    jobs  = _load_offene_jobs(conn)
    plan  = plan_haas_kapazitaet(jobs, today)

    # fmt-Felder für Frontend
    for slot in plan:
        slot["start_fmt"] = fmt_date_ch(parse_date_safe(slot["start_vorschlag"]))
        slot["ende_fmt"]  = fmt_date_ch(parse_date_safe(slot["ende_vorschlag"]))

    return success(plan)


@capacity_bp.route("/apply", methods=["POST"])
@login_required
@role_required("admin", "pl")
def apply_slot():
    """
    Übernimmt einen Planungs-Vorschlag für einen AG:
    Setzt maschine, start_soll, ende_soll auf den Vorschlag.
    """
    conn = get_db()
    data = request.get_json(silent=True) or {}
    op_id          = data.get("op_id")
    maschinen_nr   = str(data.get("maschinen_nr", "")).strip()
    start_vorschlag = data.get("start_vorschlag")
    ende_vorschlag  = data.get("ende_vorschlag")

    if not all([op_id, maschinen_nr, start_vorschlag, ende_vorschlag]):
        return error("op_id, maschinen_nr, start_vorschlag, ende_vorschlag erforderlich.", 400)

    op = conn.execute(
        "SELECT * FROM order_operations WHERE id = ?", (op_id,)
    ).fetchone()
    if not op:
        return error(f"Arbeitsgang {op_id} nicht gefunden.", 404)

    conn.execute("""
        UPDATE order_operations
           SET maschine   = ?,
               start_soll = ?,
               ende_soll  = ?,
               updated_at = CURRENT_TIMESTAMP
         WHERE id = ?
    """, (maschinen_nr, start_vorschlag, ende_vorschlag, op_id))
    conn.commit()

    return success({"op_id": op_id, "maschinen_nr": maschinen_nr,
                    "start_vorschlag": start_vorschlag, "ende_vorschlag": ende_vorschlag})
