import logging

import psycopg2

from db.connection import get_connection

logger = logging.getLogger(__name__)

_UPSERT_SQL = """
    INSERT INTO identity_links (email, linked_email, last_updated)
    VALUES (%s, %s, %s)
    ON CONFLICT (email, linked_email)
    DO UPDATE SET last_updated = EXCLUDED.last_updated
"""

_SELECT_LINKED_SQL = """
    SELECT email, linked_email
    FROM identity_links
    WHERE email = %s OR linked_email = %s
"""

_DELETE_BY_DATE_SQL = """
    DELETE FROM identity_links WHERE last_updated = %s
"""


def upsert_links(pairs):
    if not pairs:
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(_UPSERT_SQL, pairs)
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        logger.exception("Failed to upsert identity links")
        raise
    finally:
        conn.close()


def get_linked_identities(email):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SELECT_LINKED_SQL, (email, email))
            return [
                linked_email if row_email == email else row_email
                for row_email, linked_email in cur.fetchall()
            ]
    except psycopg2.Error:
        logger.exception("Failed to fetch linked identities for %s", email)
        raise
    finally:
        conn.close()


def delete_links_by_date(date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_DELETE_BY_DATE_SQL, (date,))
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        logger.exception("Failed to delete identity links for date %s", date)
        raise
    finally:
        conn.close()