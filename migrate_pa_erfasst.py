"""
migrate_pa_erfasst.py
Einmalig ausführen um pa_erfasst Spalte zur bestehenden DB hinzuzufügen.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "produktions.db")

conn = sqlite3.connect(DB_PATH)
try:
    conn.execute("ALTER TABLE orders ADD COLUMN pa_erfasst DATE;")
    conn.commit()
    print("✅ Spalte pa_erfasst erfolgreich hinzugefügt.")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("ℹ️  Spalte pa_erfasst existiert bereits — nichts zu tun.")
    else:
        raise
finally:
    conn.close()
