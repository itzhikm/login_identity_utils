CREATE TABLE IF NOT EXISTS identity_links (
    id            SERIAL PRIMARY KEY,
    system_1_email         VARCHAR NULL,
    system_2_email         VARCHAR NULL,
    system_3_email         VARCHAR NULL,
    last_updated  DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS identity_links_history (
    id            SERIAL PRIMARY KEY,
    system_1_email         VARCHAR NULL,
    system_1_ts            TIMESTAMP,
    system_2_email         VARCHAR NULL,
    system_2_ts            TIMESTAMP,
    system_3_email         VARCHAR NULL,
    system_3_ts            TIMESTAMP,
    inserted_date  DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS login_events (
    id            SERIAL,
    event_json    VARCHAR,
    email         VARCHAR NOT NULL,
    source_topic  VARCHAR,
    ts            TIMESTAMP NOT NULL ,
    ip            VARCHAR NOT NULL,
    inserted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (id, ts)
) PARTITION BY RANGE (ts);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_login_events_ip_ts      ON login_events (ip, ts);
CREATE INDEX IF NOT EXISTS idx_login_events_email_ts   ON login_events (email, ts);
CREATE INDEX IF NOT EXISTS idx_login_events_inserted   ON login_events (inserted_date);

