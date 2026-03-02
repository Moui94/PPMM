# Produktionsmonitoring

Webbasiertes Produktionsüberwachungssystem für die Fertigung von Abutments und Implantaten.

---

## Schnellstart

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. Applikation starten
python run.py
# → http://localhost:5000
# → Login: admin / admin123
```

---

## Projektstruktur

```
├── run.py                    Startpunkt
├── requirements.txt
├── backend/
│   ├── app.py                Flask App Factory
│   ├── constants.py          Zentrale Konfiguration (AGs, Fehlerkatalog, ...)
│   ├── database.py           SQLite-Verbindung + Schema-Init
│   ├── models/
│   │   ├── order.py          Auftrags-CRUD
│   │   ├── operation.py      Arbeitsgänge-CRUD
│   │   ├── feedback.py       Rückmeldungen + Qualitätsauswertungen
│   │   └── user.py           Benutzerverwaltung
│   ├── routes/
│   │   ├── auth.py           POST /api/auth/login|logout
│   │   ├── orders.py         GET|POST /api/orders, ...
│   │   ├── operations.py     GET|PUT /api/operations/<id>, ...
│   │   ├── quality.py        GET /api/quality/pareto|ausschuss|catalog
│   │   ├── users.py          GET|POST /api/users, ...
│   │   └── export.py         GET /api/export/full|order/<pa_nr>
│   └── services/
│       └── date_calc.py      Termin- und Arbeitstage-Berechnungen
├── frontend/
│   ├── index.html            SPA-Einstiegspunkt (Bootstrap 5)
│   ├── css/app.css
│   └── js/
│       ├── api.js            Zentralisierte fetch()-Aufrufe
│       ├── auth.js           Login/Session
│       ├── app.js            SPA-Router + Utilities
│       ├── dashboard.js      Auftragsübersicht + KPIs
│       ├── order.js          Auftragsdetail + Formulare
│       ├── operations.js     AG-Bearbeitung + Rückmeldungen
│       ├── quality.js        Qualitäts-Dashboard + Fehlerkatalog
│       └── schedule.js       Fräsplanung-Dashboard (AG01–03)
└── tests/
    ├── conftest.py
    ├── test_date_calc.py
    ├── test_models_order.py
    ├── test_models_operation.py
    ├── test_models_feedback.py
    └── test_routes_api.py
```

---

## API-Übersicht

### Auth
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| POST | `/api/auth/login` | Login (Session) |
| POST | `/api/auth/logout` | Logout |
| GET  | `/api/auth/me` | Aktueller Benutzer |

### Aufträge
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| GET  | `/api/orders` | Liste (Filter: status, art, prio, q) |
| POST | `/api/orders` | Neuen Auftrag anlegen |
| GET  | `/api/orders/kpis` | Dashboard-KPIs |
| GET  | `/api/orders/<pa_nr>` | Auftragsdetail |
| PUT  | `/api/orders/<pa_nr>` | Auftrag bearbeiten |
| GET  | `/api/orders/<pa_nr>/ops` | Arbeitsgänge |

### Arbeitsgänge
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| GET  | `/api/operations/<id>` | AG-Detail |
| PUT  | `/api/operations/<id>` | AG bearbeiten |
| POST | `/api/operations/<id>/feedback` | Rückmeldung erfassen |
| GET  | `/api/operations/<id>/feedbacks` | Alle Rückmeldungen |

### Qualität
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| GET | `/api/quality/pareto` | Top-10 Fehlercodes (global) |
| GET | `/api/quality/pareto/<ag_nr>` | Top-10 pro AG |
| GET | `/api/quality/ausschuss/<pa_nr>` | Ausschussquote Auftrag |
| GET | `/api/quality/catalog` | Fehlerkatalog |

### Export
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| GET | `/api/export/full` | Alle aktiven Aufträge als .xlsx |
| GET | `/api/export/order/<pa_nr>` | Einzelauftrag als .xlsx |

---

## Tests ausführen

```bash
# Alle Tests
pytest tests/ -v

# Einzelne Datei
pytest tests/test_date_calc.py -v

# Mit Abdeckungsbericht
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=term-missing
```

---

## Rollen

| Rolle | Beschreibung | Berechtigungen |
|---|---|---|
| `admin` | Administrator | Alles inkl. Benutzerverwaltung |
| `pl` | Projektleitung | Aufträge anlegen/bearbeiten, Rückmeldungen |
| `ma` | Mitarbeiter | Nur lesen + Rückmeldungen erfassen |

---

## Produktion (Windows)

```bash
pip install waitress
python run.py
```

Für einen dauerhaften Betrieb als Windows-Dienst (z.B. mit NSSM):
```
nssm install Produktionsmonitoring "C:\Python\python.exe" "C:\App\run.py"
nssm start Produktionsmonitoring
```

---

## Standard-Login

| Feld | Wert |
|---|---|
| Benutzername | `admin` |
| Passwort | `admin123` |

> ⚠️ Passwort nach erstem Login unbedingt ändern!
