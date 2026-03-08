"""
backend/constants.py
"""

MASCHINEN = {
    "2001": "Haas 01", "2002": "Haas 02", "2003": "Haas 03",
    "2004": "Haas 04", "2005": "Haas 05", "2006": "Haas 06",
    "2007": "Haas 07", "2008": "Haas 08", "2009": "Haas 09",
    "2010": "Haas 10", "2011": "Haas 11", "2012": "Haas 12",
    "2013": "Haas 13", "2014": "Haas 14",
}

MASCHINENGRUPPEN = {
    "2000": {nr: label for nr, label in MASCHINEN.items()},
}

def get_maschinen_label(nr: str) -> str:
    return MASCHINEN.get(str(nr), nr)

# ── Kapazitäten pro AG ────────────────────────────────────────────────────────
# typ "maschine" → Dropdown Haas 01–14
# typ "fix"      → automatisch eingetragen, kein Eingabefeld
AG_KAPAZITAET = {
    1:  {"typ": "maschine", "gruppe": "2000"},
    2:  {"typ": "maschine", "gruppe": "2000"},
    3:  {"typ": "maschine", "gruppe": "2000"},
    4:  {"typ": "fix", "wert": "Manuell"},
    5:  {"typ": "fix", "wert": "Manuell"},
    6:  {"typ": "fix", "wert": "Manuell"},
    7:  {"typ": "fix", "wert": "Manuell"},
    8:  {"typ": "fix", "wert": "Manuell"},
    9:  {"typ": "fix", "wert": "Manuell"},
    10: {"typ": "fix", "wert": "Manuell"},
    11: {"typ": "fix", "wert": "Manuell"},
    12: {"typ": "fix", "wert": "Manuell"},
    14: {"typ": "fix", "wert": "Manuell"},
}

def get_ag_kapazitaet_config(ag_nr: int) -> dict:
    return AG_KAPAZITAET.get(ag_nr, {"typ": "fix", "wert": "—"})

def get_maschinen_fuer_ag(ag_nr: int) -> list:
    cfg = AG_KAPAZITAET.get(ag_nr, {})
    if cfg.get("typ") == "maschine":
        gruppe = MASCHINENGRUPPEN.get(cfg["gruppe"], {})
        return sorted(gruppe.items(), key=lambda x: int(x[0]))
    return []

def get_kapazitaet_fix(ag_nr: int) -> str | None:
    cfg = AG_KAPAZITAET.get(ag_nr, {})
    if cfg.get("typ") == "fix":
        return cfg.get("wert", "—")
    return None

def get_kapazitaet_optionen(ag_nr: int) -> list:
    return []  # nicht mehr verwendet

def ist_fraes_ag(ag_nr: int) -> bool:
    return AG_KAPAZITAET.get(ag_nr, {}).get("typ") == "maschine"


# ── Ausbringung Fräsen ────────────────────────────────────────────────────────
AUSBRINGUNG_PRO_TAG = 26  # Globaler Fallback (Teile pro Tag)

# Ausbringung pro Produkt pro AG (Teile pro Tag).
# Format: { artikel: { ag_nr: stk_pro_tag } }
# Nicht definierte Einträge → Fallback AUSBRINGUNG_PRO_TAG.
AUSBRINGUNG_PRODUKT_AG = {
    # ── Abutments ────────────────────────────────────────────
    "RB16501-1": {1: 26, 2: 26},
    "RB16502-1": {1: 26, 2: 26},
    "RB16515-1": {1: 26, 2: 26},
    "RB16530-1": {1: 26, 2: 26},
    "RB16531-1": {1: 26, 2: 26},
    "RB16535-1": {1: 26, 2: 26},
    "RB16536-1": {1: 26, 2: 26},
    "WB17501-1": {1: 26, 2: 26},
    "WB17502-1": {1: 26, 2: 26},
    "WB17515-1": {1: 26, 2: 26},
    "WB17530-1": {1: 26, 2: 26},
    "WB17531-1": {1: 26, 2: 26},
    "WB17535-1": {1: 26, 2: 26},
    "WB17536-1": {1: 26, 2: 26},
    "SB15501-1": {1: 26, 2: 26},
    "SB15502-1": {1: 26, 2: 26},
    "SB15515-1": {1: 26, 2: 26},
    "SB15535-1": {1: 26, 2: 26},
    "SB15536-1": {1: 26, 2: 26},
    "SB15542-1": {1: 26, 2: 26},
    "SB15543-1": {1: 26, 2: 26},
    "SB15544-1": {1: 26, 2: 26},
    # ── Implantate XT ────────────────────────────────────────
    "XT16508-1": {1: 26, 2: 26, 3: 26},
    "XT16510-1": {1: 26, 2: 26, 3: 26},
    "XT16512-1": {1: 26, 2: 26, 3: 26},
    "XT16514-1": {1: 26, 2: 26, 3: 26},
    "XT17508-1": {1: 26, 2: 26, 3: 26},
    "XT17510-1": {1: 26, 2: 26, 3: 26},
    "XT17512-1": {1: 26, 2: 26, 3: 26},
    "XT15508-1": {1: 26, 2: 26, 3: 26},
    "XT15510-1": {1: 26, 2: 26, 3: 26},
    "XT15512-1": {1: 26, 2: 26, 3: 26},
    # ── Implantate HP ────────────────────────────────────────
    "HP1040.3809-1": {1: 26, 2: 26},
    "HP1040.3811-1": {1: 26, 2: 26},
    "HP1040.3813-1": {1: 26, 2: 26},
    "HP1040.4309-1": {1: 26, 2: 26},
    "HP1040.4311-1": {1: 26, 2: 26},
    "HP1040.4313-1": {1: 26, 2: 26},
    "HP1040.5009-1": {1: 26, 2: 26},
    "HP1040.5011-1": {1: 26, 2: 26},
    "HP1040.5013-1": {1: 26, 2: 26},
}

def get_ausbringung(artikel: str, ag_nr: int = 1) -> int:
    """Ausbringung pro Tag für ein Produkt + AG. Fallback: AUSBRINGUNG_PRO_TAG."""
    return AUSBRINGUNG_PRODUKT_AG.get(artikel, {}).get(ag_nr, AUSBRINGUNG_PRO_TAG)

def calc_solldauer_fraesen(menge: int, artikel: str = "", ag_nr: int = 1) -> int:
    """Solldauer in ganzen Tagen (aufrunden)."""
    import math
    return math.ceil(menge / get_ausbringung(artikel, ag_nr))

# ── Solldauer pro Produkt pro AG (AG1–3) ─────────────────────────────────────
# Ist ein AG für ein Produkt NICHT definiert → AG entfällt komplett.
# Format: { artikel: { ag_nr: anzahl_operationen } }
#
PRODUKT_AG_OPS = {
    # ── Abutments ────────────────────────────────────────────────────────────
    "RB16501-1": {1: 1, 2: 1},
    "RB16502-1": {1: 1, 2: 1},
    "RB16515-1": {1: 1, 2: 1},
    "RB16530-1": {1: 1, 2: 1},
    "RB16531-1": {1: 1, 2: 1},
    "RB16535-1": {1: 1, 2: 1},
    "RB16536-1": {1: 1, 2: 1},
    "WB17501-1": {1: 1, 2: 1},
    "WB17502-1": {1: 1, 2: 1},
    "WB17515-1": {1: 1, 2: 1},
    "WB17530-1": {1: 1, 2: 1},
    "WB17531-1": {1: 1, 2: 1},
    "WB17535-1": {1: 1, 2: 1},
    "WB17536-1": {1: 1, 2: 1},
    "SB15501-1": {1: 1, 2: 1},
    "SB15502-1": {1: 1, 2: 1},
    "SB15515-1": {1: 1, 2: 1},
    "SB15535-1": {1: 1, 2: 1},
    "SB15536-1": {1: 1, 2: 1},
    "SB15542-1": {1: 1, 2: 1},
    "SB15543-1": {1: 1, 2: 1},
    "SB15544-1": {1: 1, 2: 1},
    # ── Implantate XT ────────────────────────────────────────────────────────
    "XT16508-1":     {1: 1, 2: 1, 3: 1},
    "XT16510-1":     {1: 1, 2: 1, 3: 1},
    "XT16512-1":     {1: 1, 2: 1, 3: 1},
    "XT16514-1":     {1: 1, 2: 1, 3: 1},
    "XT17508-1":     {1: 1, 2: 1, 3: 1},
    "XT17510-1":     {1: 1, 2: 1, 3: 1},
    "XT17512-1":     {1: 1, 2: 1, 3: 1},
    "XT15508-1":     {1: 1, 2: 1, 3: 1},
    "XT15510-1":     {1: 1, 2: 1, 3: 1},
    "XT15512-1":     {1: 1, 2: 1, 3: 1},
    # ── Implantate HP ────────────────────────────────────────────────────────
    "HP1040.3809-1": {1: 1, 2: 1},
    "HP1040.3811-1": {1: 1, 2: 1},
    "HP1040.3813-1": {1: 1, 2: 1},
    "HP1040.4309-1": {1: 1, 2: 1},
    "HP1040.4311-1": {1: 1, 2: 1},
    "HP1040.4313-1": {1: 1, 2: 1},
    "HP1040.5009-1": {1: 1, 2: 1},
    "HP1040.5011-1": {1: 1, 2: 1},
    "HP1040.5013-1": {1: 1, 2: 1},
}


def get_fraes_solldauern(artikel: str, menge: int) -> dict:
    """
    Gibt {ag_nr: solldauer_tage} für AG1–3 zurück.
    Solldauer = ceil(menge * ops / get_ausbringung(artikel, ag_nr)).
    AG ohne Eintrag in PRODUKT_AG_OPS entfällt.
    """
    import math
    ops_map = PRODUKT_AG_OPS.get(artikel, {})
    result  = {}
    for ag_nr, ops in ops_map.items():
        if ag_nr in (1, 2, 3):
            ausbrg = get_ausbringung(artikel, ag_nr)
            result[ag_nr] = math.ceil(menge * ops / ausbrg)
    return result


def get_ag_sequenz_fuer_produkt(art: str, artikel: str, ceramaret: bool = False) -> list[int]:
    """
    Gibt die effektive AG-Sequenz zurück:
    - Fräs-AGs (1–3) nur wenn in PRODUKT_AG_OPS definiert
    - Ceramaret: AG1 entfällt zusätzlich
    """
    basis  = AG_SEQUENZ_CERAMARET.get(art, []) if ceramaret else AG_SEQUENZ.get(art, [])
    ops    = PRODUKT_AG_OPS.get(artikel, {})
    result = []
    for ag_nr in basis:
        if ag_nr in (1, 2, 3):
            if ag_nr in ops:        # nur wenn definiert
                result.append(ag_nr)
        else:
            result.append(ag_nr)
    return result

# ── Arbeitsgänge ──────────────────────────────────────────────────────────────
ARBEITSGAENGE = {
    1:  {"bezeichnung": "Fräsen AG1",                             "solldauer_tage": 2},
    2:  {"bezeichnung": "Fräsen AG2",                             "solldauer_tage": 2},
    3:  {"bezeichnung": "Fräsen AG3",                             "solldauer_tage": 2},
    4:  {"bezeichnung": "US Vorreinigen Elma Sonic",              "solldauer_tage": 1},
    5:  {"bezeichnung": "Optische Prüfung",                       "solldauer_tage": 1},
    6:  {"bezeichnung": "Massprüfung (messen)",                   "solldauer_tage": 5},
    7:  {"bezeichnung": "Sandstrahlen",                           "solldauer_tage": 2},
    8:  {"bezeichnung": "Säureätzen",                             "solldauer_tage": 2},
    9:  {"bezeichnung": "Säurereinigung (Oberflächenfinish)",     "solldauer_tage": 1},
    10: {"bezeichnung": "Neutralisieren /Vorreinigen Elma Sonic", "solldauer_tage": 1},
    11: {"bezeichnung": "Optische und Funktionale Prüfung",       "solldauer_tage": 2},
    12: {"bezeichnung": "Endreinigung Elma Solvex",               "solldauer_tage": 1},
    14: {"bezeichnung": "Vakuumverpackungen",                     "solldauer_tage": 1},
}

AG_SEQUENZ = {
    "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14],
    "I": [1, 2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 14],
}
AG_SEQUENZ_CERAMARET = {
    "A": [   2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14],
    "I": [   2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 14],
}

def get_ag_sequenz(art: str, ceramaret: bool = False) -> list:
    if ceramaret:
        return AG_SEQUENZ_CERAMARET.get(art, AG_SEQUENZ_CERAMARET["I"])
    return AG_SEQUENZ.get(art, AG_SEQUENZ["I"])

def get_solldauer(ag_nr: int) -> float:
    return ARBEITSGAENGE.get(ag_nr, {}).get("solldauer_tage", 1)

# ── Produkte ──────────────────────────────────────────────────────────────────
PRODUKTE = {
    "RB16501-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16502-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16515-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16530-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16531-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16535-1": {"art": "A", "ceramaret_moeglich": False},
    "RB16536-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17501-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17502-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17515-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17530-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17531-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17535-1": {"art": "A", "ceramaret_moeglich": False},
    "WB17536-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15501-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15502-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15515-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15535-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15536-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15542-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15543-1": {"art": "A", "ceramaret_moeglich": False},
    "SB15544-1": {"art": "A", "ceramaret_moeglich": False},
    "XT16508-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT16510-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT16512-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT16514-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT17508-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT17510-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT17512-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT15508-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT15510-1":     {"art": "I", "ceramaret_moeglich": True},
    "XT15512-1":     {"art": "I", "ceramaret_moeglich": True},
    "HP1040.3809-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.3811-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.3813-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4309-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4311-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4313-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5009-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5011-1": {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5013-1": {"art": "I", "ceramaret_moeglich": False},
}

def get_produkte_by_art(art): return sorted(k for k,v in PRODUKTE.items() if v["art"]==art)
def get_produkt_info(artikel): return PRODUKTE.get(artikel, {})
def is_ceramaret_moeglich(artikel): return PRODUKTE.get(artikel,{}).get("ceramaret_moeglich", False)

FEHLERKATALOG = {
    "M01": {"bezeichnung": "Durchmesser zu gross",         "kategorie": "M", "ag": [1,2,3,6]},
    "M02": {"bezeichnung": "Durchmesser zu klein",         "kategorie": "M", "ag": [1,2,3,6]},
    "M03": {"bezeichnung": "Länge ausserhalb Toleranz",    "kategorie": "M", "ag": [1,2,3,6]},
    "M04": {"bezeichnung": "Gewinde fehlerhaft",           "kategorie": "M", "ag": [1,2,3,6]},
    "M05": {"bezeichnung": "Rundlauffehler",               "kategorie": "M", "ag": [1,2,3,6]},
    "O01": {"bezeichnung": "Kratzer",                      "kategorie": "O", "ag": [4,5,6,9]},
    "O02": {"bezeichnung": "Riefen",                       "kategorie": "O", "ag": [4,5,6,9]},
    "O03": {"bezeichnung": "Poren / Lunker",               "kategorie": "O", "ag": [6,9]},
    "O04": {"bezeichnung": "Oxidation / Verfärbung",       "kategorie": "O", "ag": [5,7,9]},
    "O05": {"bezeichnung": "Beschichtungsfehler",          "kategorie": "O", "ag": [7,9]},
    "P01": {"bezeichnung": "Falsches Material",            "kategorie": "P", "ag": [1,6]},
    "P02": {"bezeichnung": "Falsche Charge",               "kategorie": "P", "ag": [1,6]},
    "P03": {"bezeichnung": "Programmierfehler",            "kategorie": "P", "ag": [1,2,3]},
    "P04": {"bezeichnung": "Werkzeugbruch",                "kategorie": "P", "ag": [1,2,3]},
    "H01": {"bezeichnung": "Deformation / Delle",         "kategorie": "H", "ag": [4,5,8,9,10]},
    "H02": {"bezeichnung": "Falsch beschriftet",          "kategorie": "H", "ag": [8]},
    "H03": {"bezeichnung": "Falsches Verpackungsmaterial", "kategorie": "H", "ag": [10]},
    "Q01": {"bezeichnung": "Nicht konform (allgemein)",   "kategorie": "Q", "ag": [6,9,12]},
    "Q02": {"bezeichnung": "Dokumentation unvollständig", "kategorie": "Q", "ag": [12]},
    "S01": {"bezeichnung": "Sonstiger Fehler",            "kategorie": "S", "ag": list(range(1,15))},
    "S02": {"bezeichnung": "Kundenbeanstandung",          "kategorie": "S", "ag": [14]},
}

def get_fehler_by_ag(ag_nr):
    return {c: i for c,i in FEHLERKATALOG.items() if ag_nr in i.get("ag",[])}

AUFTRAG_STATUS = ["geplant","aktiv","abgeschlossen","archiviert"]
AG_STATUS      = ["offen","laufend","abgeschlossen"]
AUFTRAG_TYPEN  = ["A","I"]
PRIORITAETEN   = [1,2,3]
USER_ROLLEN    = ["admin","pl","ma"]
