"""
backend/constants.py
Zentrale Konfiguration: Arbeitsgänge, Produkte, Fehlerkatalog, Enums.
"""

# ──────────────────────────────────────────────────────────────────────────────
# ARBEITSGÄNGE  (ag_nr → {bezeichnung, solldauer_tage, maschinengruppe})
# ──────────────────────────────────────────────────────────────────────────────
ARBEITSGAENGE = {
    1:  {"bezeichnung": "Fräsen 1. Op",          "solldauer_tage": 2,  "maschinengruppe": "fraesen"},
    2:  {"bezeichnung": "Fräsen 2. Op",           "solldauer_tage": 2,  "maschinengruppe": "fraesen"},
    3:  {"bezeichnung": "Fräsen 3. Op",           "solldauer_tage": 2,  "maschinengruppe": "fraesen"},
    4:  {"bezeichnung": "Entgraten / Waschen",    "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    5:  {"bezeichnung": "Sandstrahlen",           "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    6:  {"bezeichnung": "Massprüfung",            "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    7:  {"bezeichnung": "Eloxieren",              "solldauer_tage": 2,  "maschinengruppe": "extern"},
    8:  {"bezeichnung": "Laserbeschriften",       "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    9:  {"bezeichnung": "Endkontrolle",           "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    10: {"bezeichnung": "Verpacken",              "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    11: {"bezeichnung": "Reinigung / Sterilisation", "solldauer_tage": 2, "maschinengruppe": "extern"},
    12: {"bezeichnung": "Zertifizierung",         "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    13: {"bezeichnung": "Versand vorbereiten",    "solldauer_tage": 1,  "maschinengruppe": "manuell"},
    14: {"bezeichnung": "Auslieferung",           "solldauer_tage": 1,  "maschinengruppe": "manuell"},
}

# ──────────────────────────────────────────────────────────────────────────────
# AG-SEQUENZEN pro Typ  (Standard ohne Ceramaret)
# ──────────────────────────────────────────────────────────────────────────────
AG_SEQUENZ = {
    "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "I": [1, 2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 13, 14],
}

# Wenn Ceramaret = True → AG1 entfällt (Fräsen bereits extern)
AG_SEQUENZ_CERAMARET = {
    "A": [   2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "I": [   2, 3, 4, 5, 6,    8, 9, 10, 11, 12, 13, 14],
}

# ──────────────────────────────────────────────────────────────────────────────
# KAPAZITÄTEN  (AG ≥ 4 → Kapazitätsfeld)
# Fräs-AGs 1–3: Maschinen-Nr (2001–2006 → Haas 1–6)
# ──────────────────────────────────────────────────────────────────────────────
MASCHINEN = {
    "2001": "Haas 1",
    "2002": "Haas 2",
    "2003": "Haas 3",
    "2004": "Haas 4",
    "2005": "Haas 5",
    "2006": "Haas 6",
}

KAPAZITAET_AG = {
    # AG 1–3: Frässmaschinen-Auswahl
    1: list(MASCHINEN.keys()),
    2: list(MASCHINEN.keys()),
    3: list(MASCHINEN.keys()),
    # AG 4+: Kapazitätsstufen
    4:  ["1 MA", "2 MA"],
    5:  ["1 MA", "2 MA"],
    6:  ["1 MA", "2 MA"],
    7:  ["Standard", "Express"],
    8:  ["1 MA", "2 MA"],
    9:  ["1 MA", "2 MA"],
    10: ["1 MA", "2 MA"],
    11: ["Standard", "Express"],
    12: ["Standard", "Express"],
    13: ["1 MA"],
    14: ["1 MA"],
}

def get_maschinen_label(nr: str) -> str:
    """2001 → 'Haas 1'"""
    return MASCHINEN.get(str(nr), nr)

# ──────────────────────────────────────────────────────────────────────────────
# PRODUKT-STAMMDATEN
# Ceramaret nur für Artikel die mit 'XT' beginnen.
# ag_sequenz_override: falls ein Produkt eine abweichende AG-Folge hat
# ──────────────────────────────────────────────────────────────────────────────
PRODUKTE = {
    # ── Abutments (A) ────────────────────────────────────────────────────────
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
    # ── Implantate (I) — XT-Artikel: ceramaret möglich ───────────────────────
    "XT16508-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT16510-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT16512-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT16514-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT17508-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT17510-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT17512-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT15508-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT15510-1":      {"art": "I", "ceramaret_moeglich": True},
    "XT15512-1":      {"art": "I", "ceramaret_moeglich": True},
    # ── Implantate (I) — HP-Artikel: kein Ceramaret ──────────────────────────
    "HP1040.3809-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.3811-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.3813-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4309-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4311-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.4313-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5009-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5011-1":  {"art": "I", "ceramaret_moeglich": False},
    "HP1040.5013-1":  {"art": "I", "ceramaret_moeglich": False},
}

def get_produkte_by_art(art: str) -> list[str]:
    """Gibt sortierte Artikelliste für eine Art zurück."""
    return sorted(k for k, v in PRODUKTE.items() if v["art"] == art)

def get_produkt_info(artikel: str) -> dict:
    """Gibt Produkt-Info zurück oder leeres Dict."""
    return PRODUKTE.get(artikel, {})

def is_ceramaret_moeglich(artikel: str) -> bool:
    """True wenn Artikel mit XT beginnt (Ceramaret möglich)."""
    return PRODUKTE.get(artikel, {}).get("ceramaret_moeglich", False)

def get_ag_sequenz(art: str, ceramaret: bool = False) -> list[int]:
    """Gibt die AG-Sequenz zurück, berücksichtigt Ceramaret (AG1 entfällt)."""
    if ceramaret:
        return AG_SEQUENZ_CERAMARET.get(art, AG_SEQUENZ_CERAMARET["I"])
    return AG_SEQUENZ.get(art, AG_SEQUENZ["I"])

def get_solldauer(ag_nr: int) -> float:
    return ARBEITSGAENGE.get(ag_nr, {}).get("solldauer_tage", 1)

def get_kapazitaet_optionen(ag_nr: int) -> list[str]:
    return KAPAZITAET_AG.get(ag_nr, [])

# ──────────────────────────────────────────────────────────────────────────────
# FERTIGUNGSMATRIX  (welche Maschinen dürfen welche AGs fertigen)
# ──────────────────────────────────────────────────────────────────────────────
FERTIGUNGSMATRIX = {
    "A": {"fraesen": ["2001","2002","2003","2004","2005","2006"]},
    "I": {"fraesen": ["2001","2002","2003","2004","2005","2006"]},
}

# ──────────────────────────────────────────────────────────────────────────────
# FEHLERKATALOG
# ──────────────────────────────────────────────────────────────────────────────
FEHLERKATALOG = {
    # M = Massfehler
    "M01": {"bezeichnung": "Durchmesser zu gross",         "kategorie": "M", "ag": [1,2,3,6]},
    "M02": {"bezeichnung": "Durchmesser zu klein",         "kategorie": "M", "ag": [1,2,3,6]},
    "M03": {"bezeichnung": "Länge ausserhalb Toleranz",    "kategorie": "M", "ag": [1,2,3,6]},
    "M04": {"bezeichnung": "Gewinde fehlerhaft",           "kategorie": "M", "ag": [1,2,3,6]},
    "M05": {"bezeichnung": "Rundlauffehler",               "kategorie": "M", "ag": [1,2,3,6]},
    # O = Oberflächenfehler
    "O01": {"bezeichnung": "Kratzer",                      "kategorie": "O", "ag": [4,5,6,9]},
    "O02": {"bezeichnung": "Riefen",                       "kategorie": "O", "ag": [4,5,6,9]},
    "O03": {"bezeichnung": "Poren / Lunker",               "kategorie": "O", "ag": [6,9]},
    "O04": {"bezeichnung": "Oxidation / Verfärbung",       "kategorie": "O", "ag": [5,7,9]},
    "O05": {"bezeichnung": "Beschichtungsfehler",          "kategorie": "O", "ag": [7,9]},
    # P = Prozessfehler
    "P01": {"bezeichnung": "Falsches Material",            "kategorie": "P", "ag": [1,6]},
    "P02": {"bezeichnung": "Falsche Charge",               "kategorie": "P", "ag": [1,6]},
    "P03": {"bezeichnung": "Programmierfehler",            "kategorie": "P", "ag": [1,2,3]},
    "P04": {"bezeichnung": "Werkzeugbruch",                "kategorie": "P", "ag": [1,2,3]},
    # H = Handlingfehler
    "H01": {"bezeichnung": "Deformation / Delle",         "kategorie": "H", "ag": [4,5,8,9,10]},
    "H02": {"bezeichnung": "Falsch beschriftet",          "kategorie": "H", "ag": [8]},
    "H03": {"bezeichnung": "Falsches Verpackungsmaterial", "kategorie": "H", "ag": [10]},
    # Q = Qualitätsfehler
    "Q01": {"bezeichnung": "Nicht konform (allgemein)",   "kategorie": "Q", "ag": [6,9,12]},
    "Q02": {"bezeichnung": "Dokumentation unvollständig", "kategorie": "Q", "ag": [12]},
    # S = Sonstiges
    "S01": {"bezeichnung": "Sonstiger Fehler",            "kategorie": "S", "ag": list(range(1,15))},
    "S02": {"bezeichnung": "Kundenbeanstandung",          "kategorie": "S", "ag": [14]},
}

def get_fehler_by_ag(ag_nr: int) -> dict:
    """Gibt Fehlercodes zurück die für einen AG relevant sind."""
    return {
        code: info for code, info in FEHLERKATALOG.items()
        if ag_nr in info.get("ag", [])
    }

# ──────────────────────────────────────────────────────────────────────────────
# ENUMS / VALIDIERUNG
# ──────────────────────────────────────────────────────────────────────────────
AUFTRAG_STATUS  = ["geplant", "aktiv", "abgeschlossen", "archiviert"]
AG_STATUS       = ["offen", "laufend", "abgeschlossen"]
AUFTRAG_TYPEN   = ["A", "I"]
PRIORITAETEN    = [1, 2, 3]
USER_ROLLEN     = ["admin", "pl", "ma"]
