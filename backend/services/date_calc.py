"""
backend/services/date_calc.py
Terminberechnungen: Arbeitstage, AG-Terminplanung, Abweichungen.
"""

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from backend.constants import (
    ARBEITSGAENGE, get_ag_sequenz, get_solldauer,
    get_fraes_solldauern, get_ag_sequenz_fuer_produkt,
)


@dataclass
class AgTermin:
    ag_nr:          int
    bezeichnung:    str
    solldauer_tage: float
    start_soll:     date
    ende_soll:      date


def add_workdays(start: date, days: float) -> date:
    """Addiert Arbeitstage (Mo–Fr) zu einem Datum."""
    full_days = math.ceil(days) if days > 0 else 0
    current   = start
    added     = 0
    while added < full_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def diff_workdays(start: date, end: date) -> int:
    """Zählt Arbeitstage zwischen zwei Daten (ohne Startdatum)."""
    if start == end:
        return 0
    count     = 0
    direction = 1 if end > start else -1
    current   = start
    while current != end:
        current += timedelta(days=direction)
        if current.weekday() < 5:
            count += direction
    return count


def calc_ag_termine(
    art: str,
    pa_start: date,
    solldauern_override: Optional[dict] = None,
    ceramaret: bool = False,
    artikel: str = "",
    menge: int = 0,
) -> tuple[list[AgTermin], date]:
    """
    Berechnet Start/Ende aller AGs sequenziell.

    AG1–3: Solldauer = ceil(menge / 26 Stk/Tag), pro Produkt konfigurierbar.
           Ist ein Fräs-AG für das Produkt nicht definiert, entfällt er.
    Ceramaret: AG1 entfällt zusätzlich.
    """
    # Effektive Sequenz (Fräs-AGs nur wenn im Produkt definiert)
    if artikel:
        sequenz = get_ag_sequenz_fuer_produkt(art, artikel, ceramaret)
    else:
        sequenz = get_ag_sequenz(art, ceramaret)

    # Solldauern für Fräs-AGs aus Menge berechnen
    fraes_dauern = get_fraes_solldauern(artikel, menge) if artikel and menge else {}

    overrides = solldauern_override or {}
    termine   = []
    current   = pa_start

    while current.weekday() >= 5:
        current += timedelta(days=1)

    for ag_nr in sequenz:
        ag_info = ARBEITSGAENGE.get(ag_nr, {})
        if ag_nr in (1, 2, 3):
            # Priorität: 1. manueller Override, 2. Mengenberechnung, 3. Stamm
            solldauer = overrides.get(ag_nr,
                        fraes_dauern.get(ag_nr,
                        get_solldauer(ag_nr)))
        else:
            solldauer = overrides.get(ag_nr, get_solldauer(ag_nr))

        start = current
        ende  = add_workdays(start, solldauer)
        termine.append(AgTermin(
            ag_nr          = ag_nr,
            bezeichnung    = ag_info.get("bezeichnung", f"AG{ag_nr:02d}"),
            solldauer_tage = solldauer,
            start_soll     = start,
            ende_soll      = ende,
        ))
        current = ende

    endtermin = termine[-1].ende_soll if termine else pa_start
    return termine, endtermin


def recalc_endtermin(
    ops: list[dict],
    auslieferung_kunde: Optional[date] = None,
) -> tuple[date, int]:
    """
    Berechnet Endtermin aus AG-Enddaten und Abweichung zum Kundentermin.
    """
    dates = [parse_date_safe(op.get("ende_soll")) for op in ops]
    dates = [d for d in dates if d]
    if not dates:
        return date.today(), 0
    endtermin  = max(dates)
    abweichung = calc_abweichung(endtermin, auslieferung_kunde)
    return endtermin, abweichung


def calc_abweichung(soll: date, kunde: Optional[date]) -> int:
    """Verzug in Kalendertagen. Positiv = Verzug, Negativ = Puffer."""
    if not kunde:
        return 0
    return (soll - kunde).days


def ist_in_verzug(soll: date, kunde: Optional[date]) -> bool:
    return calc_abweichung(soll, kunde) > 0


def puffer_arbeitstage(soll: date, kunde: Optional[date]) -> int:
    if not kunde:
        return 0
    return diff_workdays(soll, kunde)


def fmt_date_ch(d) -> str:
    """Datum → DD.MM.YYYY, None → '—'"""
    if d is None:
        return "—"
    if isinstance(d, str):
        d = parse_date_safe(d)
        if d is None:
            return "—"
    try:
        return d.strftime("%d.%m.%Y")
    except Exception:
        return "—"


def parse_date_safe(s) -> Optional[date]:
    """ISO-String → date, sicher gegen None/Fehler."""
    if not s:
        return None
    if isinstance(s, date):
        return s
    try:
        return date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None
