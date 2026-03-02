"""
backend/constants.py
"""

# ── Maschinen-Stammdaten ─────────────────────────────────────────────────────
# Gruppe 2000 = Haas Fräsmaschinen
MASCHINEN = {
    "2001": "Haas 01",
    "2002": "Haas 02",
    "2003": "Haas 03",
    "2004": "Haas 04",
    "2005": "Haas 05",
    "2006": "Haas 06",
    "2007": "Haas 07",
    "2008": "Haas 08",
    "2009": "Haas 09",
    "2010": "Haas 10",
    "2011": "Haas 11",
    "2012": "Haas 12",
    "2013": "Haas 13",
    "2014": "Haas 14",
}

MASCHINENGRUPPEN = {
    "2000": {  # Haas Fräsmaschinen 2001–2014
        nr: label for nr, label in MASCHINEN.items()
    },
}

def get_maschinen_label(nr: str) -> str:
    return MASCHINEN.get(str(nr), nr)

# ── Kapazitäten / Maschinen pro AG ──────────────────────────────────────────
# "gruppe" → Dropdown aus MASCHINENGRUPPEN
# "optionen" → freie Auswahl-Liste (für nicht-Fräs-AGs)
AG_KAPAZITAET = {
    1:  {"typ": "maschine", "gruppe": "2000"},
    2:  {"typ": "maschine", "gruppe": "2000"},
    3:  {"typ": "maschine", "gruppe": "2000"},
    4:  {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    5:  {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    6:  {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    7:  {"typ": "optionen", "optionen": ["Standard", "Express"]},
    8:  {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    9:  {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    10: {"typ": "optionen", "optionen": ["1 MA", "2 MA"]},
    11: {"typ": "optionen", "optionen": ["Standard", "Express"]},
    12: {"typ": "optionen", "optionen": ["Standard", "Express"]},
    13: {"typ": "optionen", "optionen": ["1 MA"]},
    14: {"typ": "optionen", "optionen": ["1 MA"]},
}

def get_ag_kapazitaet_config(ag_nr: int) -> dict:
    """Gibt Kapazitäts-Konfiguration für einen AG zurück."""
    return AG_KAPAZITAET.get(ag_nr, {"typ": "optionen", "optionen": []})

def get_maschinen_fuer_ag(ag_nr: int) -> list[tuple]:
    """Gibt [(nr, label), ...] für Fräs-AGs zurück, sonst []."""
    cfg = AG_KAPAZITAET.get(ag_nr, {})
    if cfg.get("typ") == "maschine":
        gruppe = MASCHINENGRUPPEN.get(cfg["gruppe"], {})
        return sorted(gruppe.items(), key=lambda x: int(x[0]))
    return []

def get_kapazitaet_optionen(ag_nr: int) -> list[str]:
    cfg = AG_KAPAZITAET.get(ag_nr, {})
    if cfg.get("typ") == "optionen":
        return cfg.get("optionen", [])
    return []

def ist_fraes_ag(ag_nr: int) -> bool:
    return AG_KAPAZITAET.get(ag_nr, {}).get("typ") == "maschine"

# ── Arbeitsgänge ──────────────────────────────────────────────────────────────
ARBEITSGAENGE = {
    1:  {"bezeichnung": "Fräsen 1. Op",           "solldauer_tage": 2},
    2:  {"bezeichnung": "Fräsen 2. Op",            "solldauer_tage": 2},
    3:  {"bezeichnung": "Fräsen 3. Op",            "solldauer_tage": 2},
    4:  {"bezeichnung": "Entgraten / Waschen",     "solldauer_tage": 1},
    5:  {"bezeichnung": "Sandstrahlen",            "solldauer_tage": 1},
    6:  {"bezeichnung": "Massprüfung",             "solldauer_tage": 1},
    7:  {"bezeichnung": "Eloxieren",               "solldauer_tage": 2},
    8:  {"bezeichnung": "Laserbeschriften",        "solldauer_tage": 1},
    9:  {"bezeichnung": "Endkontrolle",            "solldauer_tage": 1},
    10: {"bezeichnung": "Verpacken",               "solldauer_tage": 1},
    11: {"bezeichnung": "Reinigung / Sterilisation","solldauer_tage": 2},
    12: {"bezeichnung": "Zertifizierung",          "solldauer_tage": 1},
    13: {"bezeichnung": "Versand vorbereiten",     "solldauer_tage": 1},
    14: {"bezeichnung": "Auslieferung",            "solldauer_tage": 1},
}

AG_SEQUENZ = {
    "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "I": [1, 2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 13, 14],
}
AG_SEQUENZ_CERAMARET = {
    "A": [   2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "I": [   2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 13, 14],
}

def get_ag_sequenz(art: str, ceramaret: bool = False) -> list[int]:
    if ceramaret:
        return AG_SEQUENZ_CERAMARET.get(art, AG_SEQUENZ_CERAMARET["I"])
    return AG_SEQUENZ.get(art, AG_SEQUENZ["I"])

def get_solldauer(ag_nr: int) -> float:
    return ARBEITSGAENGE.get(ag_nr, {}).get("solldauer_tage", 1)

# ── Produkt-Stammdaten ────────────────────────────────────────────────────────
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

# ── Fehlerkatalog ─────────────────────────────────────────────────────────────
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
