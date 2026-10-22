import json
import sqlite3
from datetime import datetime, timedelta, timezone

SCHEMA = """CREATE TABLE IF NOT EXISTS jobs(
  id TEXT PRIMARY KEY, source TEXT, title TEXT, company TEXT, location TEXT, region TEXT, url TEXT,
  description TEXT, salary_min REAL, salary_max REAL, posted TEXT, score REAL, reasons TEXT,
  first_seen TEXT, last_seen TEXT, notified INTEGER DEFAULT 0)"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str = "jobs.db") -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute(SCHEMA)
    return db


def upsert(db, jobs) -> None:
    ts = now()
    for j in jobs:
        db.execute(
            """INSERT INTO jobs(id,source,title,company,location,region,url,description,salary_min,salary_max,
                                posted,score,reasons,first_seen,last_seen)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET score=excluded.score, reasons=excluded.reasons,
                                             last_seen=excluded.last_seen, url=excluded.url""",
            (j.id, j.source, j.title, j.company, j.location, j.region, j.url, j.description[:1500],
             j.salary_min, j.salary_max, j.posted, j.score, json.dumps(j.reasons, ensure_ascii=False), ts, ts))
    db.commit()


def pending_notifications(db, min_score: float, limit: int):
    return db.execute("SELECT * FROM jobs WHERE notified=0 AND score>=? ORDER BY score DESC LIMIT ?",
                      (min_score, limit)).fetchall()


def mark_notified(db, ids) -> None:
    db.executemany("UPDATE jobs SET notified=1 WHERE id=?", [(i,) for i in ids])
    db.commit()


def prune(db, keep_days: int) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).isoformat(timespec="seconds")
    db.execute("DELETE FROM jobs WHERE last_seen < ?", (cutoff,))
    db.commit()
