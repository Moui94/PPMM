"""
run.py – Startpunkt der Applikation.
"""

import sys
import os
import signal
import logging

# Projektverzeichnis zum Python-Pfad hinzufügen (wichtig für Spyder/IDE)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app

log = logging.getLogger("ppmm")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = create_app()


def _shutdown(signum, frame):
    sig_name = signal.Signals(signum).name
    log.info(f"Signal {sig_name} empfangen — Server wird beendet.")
    # SQLite-Verbindungen werden durch Flask-Teardown automatisch geschlossen.
    # Hier können weitere Cleanup-Aktionen ergänzt werden.
    sys.exit(0)


# SIGINT (Ctrl+C) und SIGTERM (Prozess-Kill / Task-Manager) abfangen
signal.signal(signal.SIGINT,  _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


if __name__ == "__main__":
    try:
        from waitress import serve
        log.info("Produktionsserver gestartet auf http://0.0.0.0:5000")
        log.info("Zum Beenden: Ctrl+C oder SIGTERM senden.")
        serve(app, host="0.0.0.0", port=5000, threads=4)
    except ImportError:
        log.info("Entwicklungsserver gestartet auf http://0.0.0.0:5000")
        log.info("Zum Beenden: Ctrl+C")
        try:
            app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
        except KeyboardInterrupt:
            log.info("Entwicklungsserver beendet.")
            sys.exit(0)