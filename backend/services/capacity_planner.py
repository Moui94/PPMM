"""
backend/services/capacity_planner.py
Algorithmus zur optimalen Maschinenbelegung der Haas-Maschinen.

Optimierungsziele (absteigend priorisiert):
  1. Priorität des Auftrags (1=hoch)
  2. Wenig AG-Wechsel: gleicher AG-Typ auf gleicher Maschine bündeln
  3. Wenig Produktwechsel: gleicher Artikel auf gleicher Maschine bündeln
  4. Abhängigkeiten: AG2 erst nach AG1, AG3 erst nach AG2
"""
from datetime import date, timedelta
from backend.services.date_calc import add_workdays, parse_date_safe
from backend.constants import MASCHINEN


# ── Maschinen-Fertigungsmatrix ─────────────────────────────────────────────────
# Format: { maschinen_nr: { ag_nr: [artikel, ...] oder True (alle) } }
# True = alle Produkte erlaubt
MASCHINEN_MATRIX = {
    nr: {1: True, 2: True, 3: True}
    for nr in MASCHINEN.keys()
}


def get_faehige_maschinen(ag_nr: int, artikel: str) -> list[str]:
    """Gibt Maschinen-Nummern zurück die AG + Artikel fertigen können."""
    result = []
    for nr, caps in MASCHINEN_MATRIX.items():
        if ag_nr not in caps:
            continue
        allowed = caps[ag_nr]
        if allowed is True or artikel in allowed:
            result.append(nr)
    return sorted(result, key=lambda x: int(x))


# ── Hauptalgorithmus ───────────────────────────────────────────────────────────

def plan_haas_kapazitaet(offene_jobs: list, today: date = None) -> list:
    """
    Plant offene Fräs-AGs auf Haas-Maschinen.

    Args:
        offene_jobs: Liste von Dicts mit:
          { op_id, pa_nr, ag_nr, artikel, art, menge, solldauer_tage,
            prioritaet, start_soll, ende_soll, maschine (bisherige),
            vorgaenger_ende (ende_ist oder ende_soll von AG davor) }

    Returns:
        Liste von Planungs-Slots:
          { op_id, pa_nr, ag_nr, artikel, maschinen_nr, maschinen_label,
            start_vorschlag, ende_vorschlag, solldauer_tage,
            prioritaet, wechsel_typ }
    """
    if today is None:
        today = date.today()

    # 1. Sortierung: Prio → AG-Nr → Artikel (Bündelung)
    def sort_key(j):
        return (
            j["prioritaet"],           # Prio 1 zuerst
            j["ag_nr"],                # AG1 vor AG2 vor AG3
            j["artikel"],              # gleiche Artikel zusammen
            j["pa_nr"],
        )

    jobs = sorted(offene_jobs, key=sort_key)

    # 2. Maschinen-Kalender: { maschinen_nr: frei_ab_datum }
    maschinen_frei = {nr: today for nr in MASCHINEN.keys()}

    # 3. Bereits belegte Slots aus bisheriger Maschinenzuweisung berücksichtigen
    for j in jobs:
        if j.get("maschine") and j.get("ende_soll"):
            m = str(j["maschine"])
            ende = parse_date_safe(str(j["ende_soll"])[:10])
            if m in maschinen_frei and ende and ende > maschinen_frei[m]:
                maschinen_frei[m] = ende

    # 4. Letzte Zuweisung pro Maschine für Wechsel-Erkennung
    maschinen_letzter_job = {}  # { maschinen_nr: {ag_nr, artikel} }

    result = []

    for j in jobs:
        ag_nr   = j["ag_nr"]
        artikel = j["artikel"]
        dauer   = j["solldauer_tage"] or 1

        # Frühestmöglich: nach Vorgänger-AG
        fruehest = today
        if j.get("vorgaenger_ende"):
            v = parse_date_safe(str(j["vorgaenger_ende"])[:10])
            if v:
                fruehest = max(fruehest, v)

        faehig = get_faehige_maschinen(ag_nr, artikel)
        if not faehig:
            continue

        # Beste Maschine wählen:
        # Score: niedrig = besser
        # Kriterien: Wechsel-Kosten + frühest-freier Zeitpunkt
        def maschinen_score(nr):
            letzter = maschinen_letzter_job.get(nr, {})
            wechsel = 0
            if letzter:
                if letzter["ag_nr"] != ag_nr:
                    wechsel += 10   # AG-Wechsel kostet
                if letzter["artikel"] != artikel:
                    wechsel += 5    # Produkt-Wechsel kostet
            frei_ab = max(maschinen_frei.get(nr, today), fruehest)
            # Zeitkosten: Tage Wartezeit
            warte = (frei_ab - today).days
            return wechsel + warte * 0.1

        beste_maschine = min(faehig, key=maschinen_score)

        start = max(maschinen_frei.get(beste_maschine, today), fruehest)
        # Sicherstellen dass start ein Arbeitstag ist
        while start.weekday() >= 5:
            start += timedelta(days=1)

        ende = add_workdays(start, dauer)

        # Wechsel-Typ bestimmen
        letzter = maschinen_letzter_job.get(beste_maschine, {})
        if not letzter:
            wechsel_typ = "neu"
        elif letzter["ag_nr"] != ag_nr and letzter["artikel"] != artikel:
            wechsel_typ = "ag+produkt"
        elif letzter["ag_nr"] != ag_nr:
            wechsel_typ = "ag"
        elif letzter["artikel"] != artikel:
            wechsel_typ = "produkt"
        else:
            wechsel_typ = "gleich"

        result.append({
            "op_id":            j["op_id"],
            "pa_nr":            j["pa_nr"],
            "ag_nr":            ag_nr,
            "ag_nr_fmt":        f"AG{ag_nr:02d}",
            "artikel":          artikel,
            "menge":            j["menge"],
            "solldauer_tage":   dauer,
            "prioritaet":       j["prioritaet"],
            "maschinen_nr":     beste_maschine,
            "maschinen_label":  MASCHINEN.get(beste_maschine, beste_maschine),
            "start_vorschlag":  start.isoformat(),
            "ende_vorschlag":   ende.isoformat(),
            "wechsel_typ":      wechsel_typ,
        })

        # Kalender + letzter Job updaten
        maschinen_frei[beste_maschine]        = ende
        maschinen_letzter_job[beste_maschine] = {"ag_nr": ag_nr, "artikel": artikel}

    return result
