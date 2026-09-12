import json
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def insert(self, sample):
        with self.connect() as db:
            cursor = db.execute("INSERT INTO samples(payload) VALUES (?)", (json.dumps(sample),))
            # Bound storage to roughly one day at 1 Hz.
            db.execute("DELETE FROM samples WHERE id <= ?", (cursor.lastrowid - 86400,))

    def history(self, limit=120):
        with self.connect() as db:
            rows = db.execute("SELECT id,payload FROM samples ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(json.loads(payload), id=id_) for id_, payload in reversed(rows)]
