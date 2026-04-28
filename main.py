import logging
from datetime import date, timedelta
from pathlib import Path

from psycopg2 import sql

from db.connection import get_connection

logger = logging.getLogger(__name__)

_SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"

_PARTITION_DAYS_AHEAD = 30
_DEFAULT_PARTITION_NAME = "login_events_default"


def _tables_exist(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT to_regclass('public.identity_links'),"
            "       to_regclass('public.login_events')"
        )
        identity, login = cur.fetchone()
    return identity is not None and login is not None


def create_tables(conn):
    if _tables_exist(conn):
        logger.info("Tables already exist, skipping schema creation")
        return
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    logger.info("Created identity_links and login_events tables")


def ensure_default_partition(conn):
    stmt = sql.SQL(
        "CREATE TABLE IF NOT EXISTS {name} "
        "PARTITION OF login_events DEFAULT"
    ).format(name=sql.Identifier(_DEFAULT_PARTITION_NAME))
    with conn.cursor() as cur:
        cur.execute(stmt)
    conn.commit()
    logger.info("Ensured default partition %s", _DEFAULT_PARTITION_NAME)


def _partition_name(day):
    return f"login_events_{day:%Y_%m_%d}"


def ensure_daily_partition(conn, day):
    name = _partition_name(day)
    end = day + timedelta(days=1)
    stmt = sql.SQL(
        "CREATE TABLE IF NOT EXISTS {name} "
        "PARTITION OF login_events "
        "FOR VALUES FROM (%s) TO (%s)"
    ).format(name=sql.Identifier(name))
    with conn.cursor() as cur:
        cur.execute(stmt, (day, end))
    logger.info("Ensured partition %s for [%s, %s)", name, day, end)


def ensure_daily_partitions(conn, days_ahead=_PARTITION_DAYS_AHEAD):
    today = date.today()
    for offset in range(days_ahead):
        ensure_daily_partition(conn, today + timedelta(days=offset))
    conn.commit()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    conn = get_connection()
    try:
        create_tables(conn)
        ensure_default_partition(conn)
        ensure_daily_partitions(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()