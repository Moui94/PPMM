"""
backend/routes/quality.py
Qualitäts-API.

GET /api/quality/pareto              → Top-10 Fehlercodes global
GET /api/quality/pareto/<ag_nr>      → Top-10 Fehlercodes für AG
GET /api/quality/ausschuss/<pa_nr>   → Ausschussquote eines Auftrags
GET /api/quality/catalog             → Fehlerkatalog
"""

from flask import Blueprint, request
from backend.database import get_db
from backend.models.order import get_order_by_pa_nr
from backend.models.feedback import get_pareto_fehler, get_ausschuss_quote
from backend.constants import FEHLERKATALOG, get_fehler_by_ag
from ._helpers import success, error, login_required

quality_bp = Blueprint("quality", __name__, url_prefix="/api/quality")


@quality_bp.route("/pareto", methods=["GET"])
@login_required
def pareto_global():
    limit = int(request.args.get("limit", 10))
    return success(get_pareto_fehler(get_db(), limit=limit))


@quality_bp.route("/pareto/<int:ag_nr>", methods=["GET"])
@login_required
def pareto_ag(ag_nr):
    if ag_nr not in range(1, 15):
        return error(f"AG-Nr muss zwischen 1 und 14 liegen.", 400)
    limit = int(request.args.get("limit", 10))
    return success(get_pareto_fehler(get_db(), ag_nr=ag_nr, limit=limit))


@quality_bp.route("/ausschuss/<pa_nr>", methods=["GET"])
@login_required
def ausschuss_order(pa_nr):
    conn  = get_db()
    order = get_order_by_pa_nr(conn, pa_nr)
    if not order:
        return error(f"Auftrag '{pa_nr}' nicht gefunden.", 404)
    return success(get_ausschuss_quote(conn, order["id"]))


@quality_bp.route("/catalog", methods=["GET"])
@login_required
def catalog():
    ag_nr = request.args.get("ag_nr")
    if ag_nr:
        try: ag_nr = int(ag_nr)
        except: return error("ag_nr muss eine Zahl sein.", 400)
        return success(get_fehler_by_ag(ag_nr))
    return success(FEHLERKATALOG)
