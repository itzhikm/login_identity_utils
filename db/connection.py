import logging
import os

import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)

_REQUIRED_ENV_VARS = (
    "POSTGRES_HOST",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)

_database_verified = False


def _read_params():
    missing = [v for v in _REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        raise RuntimeError(
            "Missing required PostgreSQL environment variable(s): "
            + ", ".join(missing)
        )
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }


def _ensure_database_exists(params):
    admin_params = dict(params, dbname="postgres")
    admin_conn = psycopg2.connect(**admin_params)
    try:
        admin_conn.autocommit = True
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (params["dbname"],),
            )
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(params["dbname"])
                    )
                )
                logger.info("Created database %s", params["dbname"])
    finally:
        admin_conn.close()


def get_connection():
    global _database_verified
    params = _read_params()
    if not _database_verified:
        try:
            _ensure_database_exists(params)
        except psycopg2.Error:
            logger.exception(
                "Failed to verify or create database %s", params["dbname"]
            )
            raise
        _database_verified = True
    return psycopg2.connect(**params)