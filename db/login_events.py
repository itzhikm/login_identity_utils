import logging

import psycopg2
from psycopg2.extras import RealDictCursor

from db.connection import get_connection

logger = logging.getLogger(__name__)

_BATCH_SIZE = 1000

_INSERT_SQL = """
    INSERT INTO login_events (email, ts, ip, inserted_date)
    VALUES (
        %(email)s,
        %(ts)s,
        %(ip)s,
        COALESCE(%(inserted_date)s, CURRENT_DATE)
    )
"""

_SELECT_BY_DATE_SQL = """
    SELECT id, email, ts, ip, inserted_date
    FROM login_events
    WHERE inserted_date = %s
"""

_SELECT_BY_IP_SQL = """
    SELECT id, email, ts, ip, inserted_date
    FROM login_events
    WHERE ip = %s AND inserted_date = %s
"""


def _normalize(events):
    return [
        {
            "email": e["email"],
            "ts": e["ts"],
            "ip": e["ip"],
            "inserted_date": e.get("inserted_date"),
        }
        for e in events
    ]


def insert_events(events):
    if not events:
        return
    rows = _normalize(events)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for start in range(0, len(rows), _BATCH_SIZE):
                batch = rows[start:start + _BATCH_SIZE]
                cur.executemany(_INSERT_SQL, batch)
                conn.commit()
    except psycopg2.Error:
        conn.rollback()
        logger.exception("Failed to insert login events")
        raise
    finally:
        conn.close()


def get_events_by_date(date):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(_SELECT_BY_DATE_SQL, (date,))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error:
        logger.exception("Failed to fetch login events for date %s", date)
        raise
    finally:
        conn.close()


def get_events_by_ip(ip, date):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(_SELECT_BY_IP_SQL, (ip, date))
            return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error:
        logger.exception(
            "Failed to fetch login events for ip %s on date %s", ip, date
        )
        raise
    finally:
        conn.close()