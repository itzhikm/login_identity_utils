# Postgres Connection Spec for Claude Code

## Overview
Build a Python module that manages the PostgreSQL connection and provides functions to interact with the `identity_links` and `login_events` tables.

---

## Project Structure
```
db/
├── connection.py      # connection management
├── login_events.py    # login_events table operations
├── identity_links.py  # identity_links table operations
└── schema.sql         # DDL for all tables
```

---

## Environment Variables
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=identity_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
```
## Database
```
create database  according to POSTGRES_DB environment variables if database doesn't exists
```
---

## connection.py
```python
# Responsibilities:
# - Read connection params from environment variables
# - Provide a get_connection() function
# - Use psycopg2
# - Raise a clear error if any env variable is missing

import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
    )
```

---

## login_events.py
```python
# Responsibilities:
# - insert_events(events: list[dict]) → bulk insert into login_events
# - get_events_by_date(date: str) → list[dict]  fetch all events for a given date
# - get_events_by_ip(ip: str, date: str) → list[dict]  fetch all events for a given IP on a given date

# Notes:
# - insert_events should use executemany for performance
# - get_events_by_date must filter by inserted_date for partition pruning
# - All functions open and close their own connection
```

---

## identity_links.py
```python
# Responsibilities:
# - upsert_links(pairs: list[tuple]) → insert or update identity links
#   each pair is (email, linked_email, last_updated)
# - get_linked_identities(email: str) → list[str]  return all emails linked to the given email
# - delete_links_by_date(date: str) → delete all links for a given date (used for idempotency)

# Notes:
# - upsert_links should use INSERT ... ON CONFLICT (email, linked_email) DO UPDATE SET last_updated
# - get_linked_identities should return both directions:
#   WHERE email = %s OR linked_email = %s
# - All functions open and close their own connection
```

---

## schema.sql
```sql

CREATE TABLE identity_links (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR NOT NULL,
    linked_email  VARCHAR NOT NULL,
    last_updated  DATE NOT NULL,
    UNIQUE (email, linked_email)
);

CREATE TABLE login_events (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR NOT NULL,
    ts            TIMESTAMP NOT NULL,
    ip            VARCHAR NOT NULL,
    inserted_date DATE NOT NULL DEFAULT CURRENT_DATE
) PARTITION BY RANGE (inserted_date);

-- Indexes
CREATE INDEX idx_login_events_ip_ts      ON login_events (ip, ts);
CREATE INDEX idx_login_events_email_ts   ON login_events (email, ts);
CREATE INDEX idx_login_events_inserted   ON login_events (inserted_date);

CREATE INDEX idx_identity_links_email        ON identity_links (email);
CREATE INDEX idx_identity_links_linked_email ON identity_links (linked_email);
CREATE INDEX idx_identity_links_last_updated ON identity_links (last_updated);
```

---

## requirements.txt
```
psycopg2-binary==2.9.9
```

---

## Implementation Notes
- All functions must close the connection in a `finally` block
- Use `%s` placeholders for all queries (never f-strings with user input)
- Log all DB errors before re-raising
- `insert_events` should commit in batches of 1000 rows for performance
