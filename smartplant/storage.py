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
            db.execute("""CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY, device_id TEXT NOT NULL, started_at TEXT NOT NULL,
                ended_at TEXT, severity TEXT NOT NULL, reasons TEXT NOT NULL, acknowledged_at TEXT)""")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS active_alarm ON alarms(device_id) WHERE ended_at IS NULL")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def insert(self, sample):
        with self.connect() as db:
            cursor = db.execute("INSERT INTO samples(payload) VALUES (?)", (json.dumps(sample),))
            # Bound storage to roughly one day at 1 Hz.
            db.execute("DELETE FROM samples WHERE id <= ?", (cursor.lastrowid - 86400,))
            if 'status' in sample:
                self._update_alarm(db, sample)

    def _update_alarm(self, db, sample):
        device, timestamp = sample['device_id'], sample['timestamp']
        active = db.execute("SELECT id, severity, reasons FROM alarms WHERE device_id=? AND ended_at IS NULL",
                            (device,)).fetchone()
        if sample['status'] == 'normal':
            if active:
                db.execute("UPDATE alarms SET ended_at=? WHERE id=?", (timestamp, active[0]))
        elif active:
            severity = 'critical' if 'critical' in (active[1], sample['status']) else 'warning'
            reasons = list(dict.fromkeys(json.loads(active[2]) + sample['reasons']))
            db.execute("UPDATE alarms SET severity=?, reasons=? WHERE id=?",
                       (severity, json.dumps(reasons), active[0]))
        else:
            db.execute("INSERT INTO alarms(device_id,started_at,severity,reasons) VALUES (?,?,?,?)",
                       (device, timestamp, sample['status'], json.dumps(sample['reasons'])))

    def alarms(self, limit=100):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM alarms ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row, reasons=json.loads(row['reasons'])) for row in rows]

    def acknowledge(self, alarm_id, timestamp):
        with self.connect() as db:
            result = db.execute("UPDATE alarms SET acknowledged_at=COALESCE(acknowledged_at,?) WHERE id=?",
                                (timestamp, alarm_id))
            return result.rowcount > 0

    def history(self, limit=120):
        with self.connect() as db:
            rows = db.execute("SELECT id,payload FROM samples ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(json.loads(payload), id=id_) for id_, payload in reversed(rows)]
