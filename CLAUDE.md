# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python utilities for managing PostgreSQL-backed login events and identity links. The full design is specified in `postgres_spec.md` — treat that file as the source of truth for table shape, function signatures, and behavior. The `db/` package described there is not yet implemented; new work should follow the spec rather than improvising structure.

## Environment

- Python: 3.11 (`.venv/` is the project virtual environment)
- Activate venv (bash): `source .venv/Scripts/activate`
- Activate venv (PowerShell): `.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt` (psycopg2-binary == 2.9.9 per spec)

PostgreSQL connection is configured exclusively via env vars — `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`. `connection.get_connection()` must raise a clear error if any required var is missing. The target database (`POSTGRES_DB`) should be auto-created if it does not exist.

## Architecture

The `db/` package is split by table, with one module per table plus a shared connection helper:

- `db/connection.py` — env-driven `get_connection()` using psycopg2; the only place connection params are read.
- `db/login_events.py` — bulk insert + read paths for `login_events`. Reads must filter on `inserted_date` to leverage partition pruning (the table is `PARTITION BY RANGE (inserted_date)`).
- `db/identity_links.py` — upsert and lookup for `identity_links`. Lookups must be bidirectional (`WHERE email = %s OR linked_email = %s`); upserts use `INSERT ... ON CONFLICT (email, linked_email) DO UPDATE SET last_updated`.
- `db/schema.sql` — DDL for both tables and their indexes.

Cross-cutting conventions (from `postgres_spec.md`, enforce in every new function):

- Each public function opens and closes its own connection; close in a `finally` block.
- Always use `%s` placeholders — never f-string user input into SQL.
- `insert_events` uses `executemany` and commits in batches of 1000.
- Log DB errors before re-raising; do not swallow them.

## Notes for Claude

- When asked to implement DB code, follow `postgres_spec.md` exactly (function names, signatures, partition/index assumptions). Deviations should be raised with the user before coding.
- `requirements.txt` does not yet exist — create it from the spec when adding the first dependency.
- There is no test suite or lint config yet; do not invent commands for them.