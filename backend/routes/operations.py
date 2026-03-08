"""
backend/routes/operations.py
"""

from flask import Blueprint, request, session
from backend.database import get_db
from backend.models.operation import (
    get_operation_by_id, update_operation,
    set_operation_status, get_last_menge_gut,
)
from backend.models.feedback import create_feedback, get_feedbacks_for_op
from backend.models.order import update_order_endtermin
from backend.services.date_calc import fmt_date_ch
from backend.constants import (
    get_ag_kapazitaet_config, get_maschinen_fuer_ag,
    get_kapazitaet_optionen, ist_fraes_ag, get_kapazitaet_fix,
)
from ._helpers import success, error, login_required, role_required

operations_bp = Blueprint("operations", __name__, url_prefix="/api/operations")


def _op_detail(conn, op) -> dict:
    ag_nr  = op["ag_nr"]
    fraes  = ist_fraes_ag(ag_nr)
    kap_cfg = get_ag_kapazitaet_config(ag_nr)
    return {
        "id":             op["id"],
        "order_id":       op["order_id"],
        "pa_nr":          op["pa_nr"],
        "ag_nr":          ag_nr,
        "ag_nr_fmt":      f"AG{ag_nr:02d}",
        "bezeichnung":    op["bezeichnung"],
        "solldauer_tage": op["solldauer_tage"],
        "start_soll":     str(op["start_soll"] or ""),
        "start_soll_fmt": fmt_date_ch(op["start_soll"]),
        "ende_soll":      str(op["ende_soll"] or ""),
        "ende_soll_fmt":  fmt_date_ch(op["ende_soll"]),
        "start_ist":      str(op["start_ist"] or ""),
        "ende_ist":       str(op["ende_ist"]  or ""),
        "maschine":       op["maschine"],
        "kapazitaet":     op["kapazitaet"],
        "status":         op["status"],
        "bemerkung":      op["bemerkung"],
        "auftrag_menge":  op["auftrag_menge"],
        "ceramaret":      op["ceramaret"],
        # Kapazitäts-Konfiguration
        "ist_fraes_ag":         fraes,
        "kap_typ":              kap_cfg.get("typ"),
        "maschinen_liste":      get_maschinen_fuer_ag(ag_nr),   # [(nr, label), ...]
        "kapazitaet_optionen":  get_kapazitaet_optionen(ag_nr),
        "kapazitaet_fix":       kap_cfg.get("wert") if kap_cfg.get("typ") == "fix" else None,
    }


@operations_bp.route("/<int:op_id>", methods=["GET"])
@login_required
def get_op(op_id):
    conn = get_db()
    op   = get_operation_by_id(conn, op_id)
    if not op: return error(f"Arbeitsgang {op_id} nicht gefunden.", 404)
    detail = _op_detail(conn, op)
    detail["vorgaenger_menge_gut"] = get_last_menge_gut(conn, op["order_id"], op["ag_nr"])
    return success(detail)


@operations_bp.route("/<int:op_id>", methods=["PUT"])
@login_required
@role_required("admin", "pl")
def update_op(op_id):
    conn = get_db()
    op   = get_operation_by_id(conn, op_id)
    if not op: return error(f"Arbeitsgang {op_id} nicht gefunden.", 404)
    data = request.get_json(silent=True) or {}
    EDITABLE = {"solldauer_tage","start_soll","ende_soll","maschine","kapazitaet","status","bemerkung"}
    fields = {k: v for k,v in data.items() if k in EDITABLE}
    if "solldauer_tage" in fields:
        try:   fields["solldauer_tage"] = float(fields["solldauer_tage"])
        except: return error("solldauer_tage muss eine Zahl sein.", 400)
    try:
        update_operation(conn, op_id, **fields)
        update_order_endtermin(conn, op["order_id"])
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success(_op_detail(conn, get_operation_by_id(conn, op_id)))


@operations_bp.route("/<int:op_id>/feedback", methods=["POST"])
@login_required
def post_feedback(op_id):
    conn = get_db()
    op   = get_operation_by_id(conn, op_id)
    if not op: return error(f"Arbeitsgang {op_id} nicht gefunden.", 404)
    data = request.get_json(silent=True) or {}
    try:
        menge_input     = int(data.get("menge_input",     0))
        menge_ausschuss = int(data.get("menge_ausschuss", 0))
    except: return error("Mengenfelder müssen ganze Zahlen sein.", 400)
    maschine  = str(data.get("maschine",  "") or "").strip() or None
    bemerkung = str(data.get("bemerkung", "") or "").strip() or None
    fehler    = data.get("fehler", [])
    try:
        fb_id = create_feedback(
            conn, op_id=op_id, order_id=op["order_id"], ag_nr=op["ag_nr"],
            user_id=session["user_id"],
            menge_input=menge_input, menge_ausschuss=menge_ausschuss,
            start_ist=data.get("start_ist"), ende_ist=data.get("ende_ist"),
            maschine=maschine, bemerkung=bemerkung, fehler=fehler,
        )
        new_status = "abgeschlossen" if data.get("ende_ist") else "laufend"
        set_operation_status(conn, op_id, new_status,
                             start_ist=data.get("start_ist"),
                             ende_ist=data.get("ende_ist"), maschine=maschine)
        update_order_endtermin(conn, op["order_id"])
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success({
        "feedback_id": fb_id,
        "menge_gut": menge_input - menge_ausschuss,
        "menge_ausschuss": menge_ausschuss,
        "ag_status": new_status,
    }, status=201)


@operations_bp.route("/<int:op_id>/feedbacks", methods=["GET"])
@login_required
def get_feedbacks(op_id):
    conn = get_db()
    op   = get_operation_by_id(conn, op_id)
    if not op: return error(f"Arbeitsgang {op_id} nicht gefunden.", 404)
    return success([dict(fb) for fb in get_feedbacks_for_op(conn, op_id)])
