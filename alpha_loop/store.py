"""
SQLite persistence for the alpha-mining loop: hypotheses, fired events, the
loop's own accumulating price panel, and resolved forward-return outcomes.

This is the loop's memory across restarts -- everything ai_agents/ was
missing (see docs/research/alpha_loop/alpha_loop_overview_20260927.md).
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    coin TEXT NOT NULL,
    params_json TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    coin TEXT NOT NULL,
    ts TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (coin, ts)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_id TEXT NOT NULL,
    event_time TEXT NOT NULL,
    coin TEXT NOT NULL,
    predicted_direction TEXT NOT NULL,
    price_at_event REAL NOT NULL,
    raw_json TEXT,
    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(id)
);

CREATE TABLE IF NOT EXISTS outcomes (
    event_id INTEGER NOT NULL,
    horizon TEXT NOT NULL,
    forward_price REAL NOT NULL,
    forward_return REAL NOT NULL,
    hit INTEGER NOT NULL,
    resolved_at TEXT NOT NULL,
    PRIMARY KEY (event_id, horizon)
);

CREATE TABLE IF NOT EXISTS cycle_log (
    cycle INTEGER PRIMARY KEY,
    ts TEXT NOT NULL,
    summary TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_hypothesis(conn, hypothesis) -> bool:
    """Returns True if newly inserted, False if it already existed."""
    existing = conn.execute("SELECT id FROM hypotheses WHERE id = ?", (hypothesis.id,)).fetchone()
    if existing:
        return False
    conn.execute(
        "INSERT INTO hypotheses (id, name, kind, coin, params_json, source, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            hypothesis.id, hypothesis.name, hypothesis.kind, hypothesis.coin,
            json.dumps(hypothesis.params), hypothesis.source, now_iso(),
        ),
    )
    return True


def active_hypotheses(conn):
    from .hypothesis_bank import Hypothesis
    rows = conn.execute("SELECT * FROM hypotheses WHERE status = 'active'").fetchall()
    out = []
    for r in rows:
        h = Hypothesis(
            name=r["name"], kind=r["kind"], coin=r["coin"],
            params=json.loads(r["params_json"]), source=r["source"],
        )
        out.append(h)
    return out


def record_price_snapshot(conn, coin, ts, price):
    conn.execute(
        "INSERT OR IGNORE INTO price_snapshots (coin, ts, price) VALUES (?, ?, ?)",
        (coin, ts, price),
    )


def record_event(conn, hypothesis_id, coin, predicted_direction, price_at_event, raw: dict, event_time=None):
    conn.execute(
        "INSERT INTO events (hypothesis_id, event_time, coin, predicted_direction, price_at_event, raw_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (hypothesis_id, event_time or now_iso(), coin, predicted_direction, price_at_event, json.dumps(raw)),
    )


def unresolved_event_horizons(conn):
    """Every (event, horizon) pair not yet in outcomes."""
    rows = conn.execute(
        """
        SELECT e.id AS event_id, e.hypothesis_id, e.event_time, e.coin,
               e.predicted_direction, e.price_at_event
        FROM events e
        """
    ).fetchall()
    return rows


def resolved_horizons_for_event(conn, event_id):
    rows = conn.execute("SELECT horizon FROM outcomes WHERE event_id = ?", (event_id,)).fetchall()
    return {r["horizon"] for r in rows}


def nearest_price_at_or_after(conn, coin, target_ts_iso):
    row = conn.execute(
        "SELECT ts, price FROM price_snapshots WHERE coin = ? AND ts >= ? ORDER BY ts ASC LIMIT 1",
        (coin, target_ts_iso),
    ).fetchone()
    return (row["ts"], row["price"]) if row else None


def record_outcome(conn, event_id, horizon, forward_price, forward_return, hit):
    conn.execute(
        "INSERT OR REPLACE INTO outcomes (event_id, horizon, forward_price, forward_return, hit, resolved_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (event_id, horizon, forward_price, forward_return, int(hit), now_iso()),
    )


def outcomes_for_hypothesis(conn, hypothesis_id, horizon):
    rows = conn.execute(
        """
        SELECT o.forward_return AS forward_return, o.hit AS hit
        FROM outcomes o
        JOIN events e ON e.id = o.event_id
        WHERE e.hypothesis_id = ? AND o.horizon = ?
        """,
        (hypothesis_id, horizon),
    ).fetchall()
    return rows


def append_cycle_log(conn, cycle, summary):
    conn.execute(
        "INSERT OR REPLACE INTO cycle_log (cycle, ts, summary) VALUES (?, ?, ?)",
        (cycle, now_iso(), summary),
    )


def next_cycle_number(conn):
    row = conn.execute("SELECT MAX(cycle) AS m FROM cycle_log").fetchone()
    return (row["m"] or 0) + 1
