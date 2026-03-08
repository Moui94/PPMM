"""
backend/routes/orders.py
Auftrags-API inkl. Produkt-Dropdown und Ceramaret-Logik.
"""

from flask import Blueprint, request
from backend.database import get_db
from backend.models.order import (
    list_orders, get_order_by_pa_nr, create_order,
    update_order, update_order_endtermin, get_kpis,
)
from backend.models.operation import (
    create_operations_for_order, get_operations, get_operation_progress,
)
from backend.models.feedback import get_latest_feedback
from backend.services.date_calc import parse_date_safe, fmt_date_ch
from backend.constants import (
    get_kapazitaet_fix, PRODUKTE, get_produkte_by_art, get_produkt_info,
    is_ceramaret_moeglich, AUFTRAG_TYPEN,
    get_ag_sequenz_fuer_produkt, get_fraes_solldauern,
    get_ausbringung, AUSBRINGUNG_PRO_TAG, AUSBRINGUNG_PRODUKT_AG,
)
from ._helpers import success, error, login_required, role_required

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


def _order_to_dict(conn, order) -> dict:
    progress = get_operation_progress(conn, order["id"])
    abw      = order["abweichung_tage"] or 0
    ceramaret_val = order["ceramaret"]
    # ceramaret kann als String "true"/"false" oder als int 0/1 in DB liegen
    is_ceramaret = ceramaret_val in (True, 1, "true", "True", "1")
    return {
        "id":                 order["id"],
        "pa_nr":              order["pa_nr"],
        "art":                order["art"],
        "art_label":          "Implantat" if order["art"] == "I" else "Abutment",
        "artikel":            order["artikel"],
        "ceramaret":          is_ceramaret,
        "ceramaret_label":    "Ceramaret" if is_ceramaret else "Standard",
        "spezielles":         order["spezielles"],
        "menge":              order["menge"],
        "menge_produziert":   order["menge_produziert"],
        "prioritaet":         order["prioritaet"],
        "status":             order["status"],
        "pa_start":           str(order["pa_start"] or "")[:10],
        "pa_erfasst":         str(order["pa_erfasst"] or "")[:10],
        "pa_erfasst_fmt":     fmt_date_ch(order["pa_erfasst"]),
        "pa_start_fmt":       fmt_date_ch(order["pa_start"]),
        "haas_nr":            order["haas_nr"],
        "endtermin_soll":     str(order["endtermin_soll"] or ""),
        "endtermin_soll_fmt": fmt_date_ch(order["endtermin_soll"]),
        "auslieferung_kunde": str(order["auslieferung_kunde"] or ""),
        "auslieferung_fmt":   fmt_date_ch(order["auslieferung_kunde"]),
        "abweichung_tage":    abw,
        "in_verzug":          abw > 0,
        "bestaetigung_kunde": order["bestaetigung_kunde"],
        "bemerkung":          order["bemerkung"],
        "progress":           progress,
        "created_at":         str(order["created_at"] or ""),
        "updated_at":         str(order["updated_at"] or ""),
    }


def _op_to_dict(conn, op) -> dict:
    fb = get_latest_feedback(conn, op["id"])
    return {
        "id":             op["id"],
        "ag_nr":          op["ag_nr"],
        "ag_nr_fmt":      f"AG{op['ag_nr']:02d}",
        "bezeichnung":    op["bezeichnung"],
        "solldauer_tage": op["solldauer_tage"],
        "start_soll":     str(op["start_soll"] or "")[:10],
        "start_soll_fmt": fmt_date_ch(op["start_soll"]),
        "ende_soll":      str(op["ende_soll"] or "")[:10],
        "ende_soll_fmt":  fmt_date_ch(op["ende_soll"]),
        "start_ist":      str(op["start_ist"] or "")[:10],
        "ende_ist":       str(op["ende_ist"] or "")[:10],
        "maschine":       op["maschine"] or get_kapazitaet_fix(op["ag_nr"]) or "—",
        "kapazitaet":     op["kapazitaet"],
        "status":         op["status"],
        "bemerkung":      op["bemerkung"],
        "latest_feedback": {
            "menge_gut":       fb["menge_gut"]       if fb else None,
            "menge_ausschuss": fb["menge_ausschuss"] if fb else None,
            "username":        fb["username"]         if fb else None,
            "created_at":      str(fb["created_at"]) if fb else None,
        } if fb else None,
    }


# ── GET /api/orders/produkte  → Produktliste + AG-Vorschau ──────────────────
@orders_bp.route("/produkte", methods=["GET"])
@login_required
def get_produkte():
    art   = request.args.get("art")
    menge = int(request.args.get("menge", 0) or 0)
    result = {}
    for artikel, info in PRODUKTE.items():
        if art and info["art"] != art:
            continue
        fraes = get_fraes_solldauern(artikel, menge) if menge else {}
        result[artikel] = {
            "art":                info["art"],
            "ceramaret_moeglich": info["ceramaret_moeglich"],
            "fraes_solldauern":   fraes,
            "ag_sequenz":         get_ag_sequenz_fuer_produkt(info["art"], artikel, False),
            "ag_sequenz_ceramaret": get_ag_sequenz_fuer_produkt(info["art"], artikel, True),
            "ausbringung_pro_ag":  AUSBRINGUNG_PRODUKT_AG.get(artikel, {1: AUSBRINGUNG_PRO_TAG, 2: AUSBRINGUNG_PRO_TAG, 3: AUSBRINGUNG_PRO_TAG}),
        }
    return success(dict(sorted(result.items())))


# ── GET /api/orders ───────────────────────────────────────────────────────────
@orders_bp.route("", methods=["GET"])
@login_required
def get_orders():
    conn   = get_db()
    status = request.args.get("status")
    art    = request.args.get("art")
    prio   = request.args.get("prio")
    q      = request.args.get("q", "").strip()
    prio_int = None
    if prio:
        try: prio_int = int(prio)
        except ValueError: return error("Priorität muss 1, 2 oder 3 sein.", 400)
    orders = list_orders(conn, status=status, art=art, prioritaet=prio_int, search=q or None)
    return success([_order_to_dict(conn, o) for o in orders])


# ── GET /api/orders/kpis ──────────────────────────────────────────────────────
@orders_bp.route("/kpis", methods=["GET"])
@login_required
def get_kpis_route():
    return success(get_kpis(get_db()))


# ── GET /api/orders/<pa_nr> ───────────────────────────────────────────────────
@orders_bp.route("/<pa_nr>", methods=["GET"])
@login_required
def get_order(pa_nr):
    conn  = get_db()
    order = get_order_by_pa_nr(conn, pa_nr)
    if not order:
        return error(f"Auftrag '{pa_nr}' nicht gefunden.", 404)
    return success(_order_to_dict(conn, order))


# ── POST /api/orders ──────────────────────────────────────────────────────────
@orders_bp.route("", methods=["POST"])
@login_required
@role_required("admin", "pl")
def create_order_route():
    from datetime import date as _date
    data    = request.get_json(silent=True) or {}
    pa_nr   = str(data.get("pa_nr",   "")).strip()
    artikel = str(data.get("artikel", "")).strip()

    if not pa_nr:   return error("pa_nr ist Pflichtfeld.", 400)
    if not artikel: return error("artikel ist Pflichtfeld.", 400)

    # Art aus Stammdaten ableiten
    prod_info = get_produkt_info(artikel)
    if not prod_info:
        return error(f"Artikel '{artikel}' nicht in Stammdaten.", 422)
    art = prod_info["art"]

    try: menge = int(data.get("menge", 0))
    except: return error("menge muss eine ganze Zahl sein.", 400)
    if menge <= 0: return error("menge muss > 0 sein.", 400)

    prio = int(data.get("prioritaet", 2))
    if prio not in (1,2,3): return error("prioritaet muss 1, 2 oder 3 sein.", 400)

    # Ceramaret-Validierung
    ceramaret_req = bool(data.get("ceramaret", False))
    if ceramaret_req and not is_ceramaret_moeglich(artikel):
        return error(
            f"Ceramaret ist für Artikel '{artikel}' nicht möglich. "
            f"Nur Artikel mit Präfix 'XT' unterstützen Ceramaret.", 422
        )

    pa_start_d   = parse_date_safe(data.get("pa_start"))   or _date.today()
    auslieferung = parse_date_safe(data.get("auslieferung_kunde"))

    conn = get_db()
    try:
        order_id = create_order(
            conn,
            pa_nr              = pa_nr,
            art                = art,
            artikel            = artikel,
            menge              = menge,
            prioritaet         = prio,
            pa_start           = pa_start_d,
            auslieferung_kunde = auslieferung,
            ceramaret          = ceramaret_req,
            spezielles         = data.get("spezielles"),
            haas_nr            = data.get("haas_nr"),
            bemerkung          = data.get("bemerkung"),
        )
        endtermin = create_operations_for_order(
            conn, order_id, art, pa_start_d,
            ceramaret=ceramaret_req,
            artikel=artikel,
            menge=menge,
        )
        from backend.services.date_calc import calc_abweichung
        abw = calc_abweichung(endtermin, auslieferung)
        update_order(conn, order_id,
                     endtermin_soll=endtermin.isoformat(),
                     abweichung_tage=abw)
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)

    order = get_order_by_pa_nr(conn, pa_nr)
    return success(_order_to_dict(conn, order), status=201)


# ── PUT /api/orders/<pa_nr> ───────────────────────────────────────────────────
@orders_bp.route("/<pa_nr>", methods=["PUT"])
@login_required
@role_required("admin", "pl")
def update_order_route(pa_nr):
    conn  = get_db()
    order = get_order_by_pa_nr(conn, pa_nr)
    if not order:
        return error(f"Auftrag '{pa_nr}' nicht gefunden.", 404)
    data = request.get_json(silent=True) or {}
    EDITABLE = {
        "artikel","spezielles","menge","prioritaet","status",
        "auslieferung_kunde","haas_nr","bemerkung","bestaetigung_kunde",
    }
    fields = {k: v for k, v in data.items() if k in EDITABLE}
    if "menge" in fields:
        try: fields["menge"] = int(fields["menge"])
        except: return error("menge muss eine ganze Zahl sein.", 400)
    if "prioritaet" in fields:
        try: fields["prioritaet"] = int(fields["prioritaet"])
        except: return error("prioritaet muss 1, 2 oder 3 sein.", 400)
    try:
        if "pa_start" in data:
            data["pa_start"] = parse_date_safe(data["pa_start"])
        update_order(conn, order["id"], **fields)
        auslieferung = parse_date_safe(data.get("auslieferung_kunde"))
        update_order_endtermin(conn, order["id"], auslieferung)
        conn.commit()
    except ValueError as e:
        return error(str(e), 422)
    return success(_order_to_dict(conn, get_order_by_pa_nr(conn, pa_nr)))


# ── GET /api/orders/<pa_nr>/ops ───────────────────────────────────────────────
@orders_bp.route("/<pa_nr>/ops", methods=["GET"])
@login_required
def get_order_ops(pa_nr):
    conn  = get_db()
    order = get_order_by_pa_nr(conn, pa_nr)
    if not order:
        return error(f"Auftrag '{pa_nr}' nicht gefunden.", 404)
    ops = get_operations(conn, order["id"])
    return success([_op_to_dict(conn, op) for op in ops])
